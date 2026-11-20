# Muon Reasoning

**Can Muon’s advantage in associative memory extend to reasoning?**

This repository accompanies a controlled study of optimizer-dependent learning and transfer. The protocol separates fitting from reuse by pairing training probes with new numerical instances, renamed entities, counterfactuals, and multi-step compositions.

The project is organized around four ideas.

- **Matched probes** keep the computation fixed while changing the information the model must use.
- **Source and optimizer pairs** distinguish effects that come from pretraining from effects that arise during adaptation.
- **Mechanism follow-ups** inspect components, spectra, prefix rescue, and coverage variants.
- **Audit-first releases** preserve manifests, hashes, evaluation contracts, and explicit evidence status.

The project page is available from [`docs/index.html`](docs/index.html) and is designed for GitHub Pages.

## Repository map

- [`designs_4scale/`](designs_4scale/) contains the current four-scale experiment specifications.
- Mechanism follow-up designs will be added after their public artifact audit.
- [`analysis/`](analysis/) contains the curated public protocol summary.
- [`hf_dataset_cards/`](hf_dataset_cards/) contains draft dataset cards for review.
- [`docs/`](docs/) contains the public project page.

Large run outputs, checkpoints, archives, generated row-level data, local sessions, and host-specific runtime files are intentionally excluded from the first public commit. The experimental record remains auditable through the manifests and reports that are selected for release.

## Citation

The manuscript title is **Muon’s Advantage in Associative Memory Extend to Reasoning?** The citation block will be added with the final bibliographic metadata.

## Status

The evidence base is still being extended across model scale and task family. The page marks ongoing work separately from completed analyses so that preliminary observations are not presented as final claims.
