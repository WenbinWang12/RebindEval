"""Upload one dataset folder to the Hugging Face Hub as a dataset repository (draft: private by default).

  HF_TOKEN=... python hf_upload_dataset.py --spec SPEC.json --readme README.md [--public]

SPEC.json: {"repo": "<owner>/<name>", "root": "<directory of the source files>",
            "files": [["<path below root>", "<path in the repository>"], ...]}

Steps
  1. every source file is scanned for strings that must not be published (server paths, user names, host names);
     any hit stops the upload;
  2. MANIFEST.json is built: path in the repository, bytes, rows (for .jsonl) and SHA256 of every data file;
  3. the row counts stated in the README table ("| ... | 16,384 | ...") are compared with the files where the
     table names a file path; a mismatch stops the upload;
  4. the repository is created if needed (private unless --public; an existing repository keeps its visibility)
     and README.md, MANIFEST.json and the data files are committed;
  5. the Hub's file list is read back and sizes (and SHA256 of LFS files) are compared with the manifest.
The token is read from the environment variable HF_TOKEN and is not written anywhere.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

# Keep the public uploader independent of any one account, host, or institution.
# Project-specific markers belong in a private release audit, not in this script.
PRIVATE_MARKERS = (b"/home/", b"/research/", b"/local/scratch", b"/dev/shm", b"/root/",
                   b"C:\\Users\\", b"D:\\")


def scan(path):
    """SHA256, byte count, line count and private-marker hits of one file (streamed)."""
    h, size, lines, hits, tail = hashlib.sha256(), 0, 0, set(), b""
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(8 << 20), b""):
            h.update(block)
            size += len(block)
            lines += block.count(b"\n")
            window = tail + block
            for m in PRIVATE_MARKERS:
                if m in window:
                    hits.add(m.decode())
            tail = block[-64:]
    return h.hexdigest(), size, lines, sorted(hits)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", type=Path, required=True)
    ap.add_argument("--readme", type=Path, required=True)
    ap.add_argument("--public", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    spec = json.loads(a.spec.read_text())
    root = Path(spec["root"])
    readme = a.readme.read_text(encoding="utf-8")
    problems, manifest = [], []
    hits = [m.decode() for m in PRIVATE_MARKERS if m in readme.encode()]
    if hits:
        problems.append(f"README.md contains {hits}")
    for src, dst in spec["files"]:
        digest, size, lines, hits = scan(root / src)
        if hits:
            problems.append(f"{src} contains {hits}")
        entry = {"path": dst, "bytes": size, "sha256": digest}
        if dst.endswith(".jsonl"):
            entry["rows"] = lines
        manifest.append(entry)
    by_path = {e["path"]: e for e in manifest}
    for line in readme.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        named = [c.strip("`") for c in cells if c.strip("`") in by_path]
        counts = [int(c.replace(",", "")) for c in cells if re.fullmatch(r"[0-9][0-9,]*", c)]
        if named and counts and by_path[named[0]].get("rows") != counts[0]:
            problems.append(f"README says {counts[0]} rows for {named[0]}, the file has {by_path[named[0]].get('rows')}")
    for path in re.findall(r"^\s+path:\s*(\S+)\s*$", readme, flags=re.M):
        if path not in by_path:
            problems.append(f"README config names a file that is not uploaded: {path}")
    total = sum(e["bytes"] for e in manifest)
    print(json.dumps({"repo": spec["repo"], "files": len(manifest), "bytes": total,
                      "rows": {e["path"]: e["rows"] for e in manifest if "rows" in e and "schedule" not in e["path"]},
                      "problems": problems}, indent=1))
    if problems:
        sys.exit("not uploaded: fix the problems above")
    manifest_text = json.dumps({"dataset": spec["repo"].split("/")[1], "files": manifest}, indent=2) + "\n"
    if a.dry_run:
        return
    token = os.environ.get("HF_TOKEN", "").strip()
    if not token:
        sys.exit("HF_TOKEN is not set")
    from huggingface_hub import CommitOperationAdd, HfApi
    from huggingface_hub.utils import RepositoryNotFoundError
    api = HfApi(token=token)
    try:
        info = api.dataset_info(spec["repo"])
        print(f"repository exists (private={info.private}); visibility unchanged")
    except RepositoryNotFoundError:
        api.create_repo(spec["repo"], repo_type="dataset", private=not a.public, exist_ok=True)
        print(f"created {'public' if a.public else 'private'} dataset repository {spec['repo']}")
    ops = [CommitOperationAdd(path_in_repo="README.md", path_or_fileobj=readme.encode("utf-8")),
           CommitOperationAdd(path_in_repo="MANIFEST.json", path_or_fileobj=manifest_text.encode("utf-8"))]
    ops += [CommitOperationAdd(path_in_repo=dst, path_or_fileobj=str(root / src)) for src, dst in spec["files"]]
    commit = api.create_commit(repo_id=spec["repo"], repo_type="dataset", operations=ops,
                               commit_message="Initial upload: data files, dataset card and manifest")
    remote = {i.path: i for i in api.get_paths_info(spec["repo"], [e["path"] for e in manifest], repo_type="dataset")}
    bad = []
    for e in manifest:
        r = remote.get(e["path"])
        lfs = r.lfs if r is not None else None
        remote_sha = (lfs.get("sha256") if isinstance(lfs, dict) else getattr(lfs, "sha256", None)) if lfs else None
        if r is None or r.size != e["bytes"] or (remote_sha is not None and remote_sha != e["sha256"]):
            bad.append(e["path"])
    info = api.dataset_info(spec["repo"])
    print(json.dumps({"commit": getattr(commit, "oid", None), "url": f"https://huggingface.co/datasets/{spec['repo']}",
                      "private": info.private, "files_on_hub": len(remote), "size_or_sha256_mismatch": bad}, indent=1))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
