const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve('RR_MECH_ANALYSES_20261120');
function walk(d){let a=[];for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);if(e.isDirectory()){if(e.name==='raw_temp'||e.name==='e4c_test')continue;a.push(...walk(p));}else if(e.name!=='SHA256SUMS')a.push(p);}return a;}
const out=walk(root).sort().map(p=>{const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');return `${h}  ${path.relative(root,p).replaceAll(path.sep,'/')}`;}).join('\n')+'\n';fs.writeFileSync(path.join(root,'SHA256SUMS'),out);console.log(out.split('\n').length-1);
