const fs=require('fs'),path=require('path'),crypto=require('crypto');
const chunkSize=25_000_000;
const files=[
  ['MuonPaperData_20261120_vt_passes.zip','MuonPaperData_20261120_vt_passes.parts'],
  ['RR_MECH_ANALYSES_20261120/MuonPaperData_20261120_mech_analyses.zip','MuonPaperData_20261120_mech_analyses.parts']
];
for(const [file,dir] of files){
  const size=fs.statSync(file).size, total=Math.ceil(size/chunkSize), out=[];
  fs.mkdirSync(dir,{recursive:true});
  const fd=fs.openSync(file,'r'), buf=Buffer.allocUnsafe(chunkSize);
  for(let i=0;i<total;i++){const n=Math.min(chunkSize,size-i*chunkSize), got=fs.readSync(fd,buf,0,n,i*chunkSize);const name=path.join(dir,`${path.basename(file)}.part${String(i+1).padStart(2,'0')}-of-${String(total).padStart(2,'0')}`);fs.writeFileSync(name,buf.subarray(0,got));out.push(`${crypto.createHash('sha256').update(buf.subarray(0,got)).digest('hex')}  ${path.basename(name)}  ${got}`);}
  fs.closeSync(fd);const full=crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  fs.writeFileSync(path.join(dir,'SHA256SUMS.txt'),`original_sha256 ${full}\noriginal_bytes ${size}\nchunk_bytes ${chunkSize}\nchunks ${total}\n`+out.join('\n')+'\n');
  fs.writeFileSync(path.join(dir,'JOIN.txt'),`PowerShell\n$parts=Get-ChildItem ${path.basename(file)}.part*-of-* | Sort-Object Name\n$out=[IO.File]::OpenWrite('${path.basename(file)}')\nforeach($p in $parts){$b=[IO.File]::ReadAllBytes($p.FullName);$out.Write($b,0,$b.Length)}\n$out.Close()\n\n或者 Linux/macOS\ncat ${path.basename(file)}.part*-of-* > ${path.basename(file)}\n`);
  console.log(file,size,total);
}
