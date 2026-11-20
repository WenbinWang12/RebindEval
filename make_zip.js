const fs=require('fs'),path=require('path');
const root=path.resolve('_mech_stage'),out=path.resolve('MuonPaperData_20261120_mech_analyses_v7.zip');
const crcTable=new Uint32Array(256);for(let n=0;n<256;n++){let c=n;for(let k=0;k<8;k++)c=(c&1)?(0xedb88320^(c>>>1)):(c>>>1);crcTable[n]=c>>>0;}
function crc32(b){let c=0xffffffff;for(const x of b)c=crcTable[(c^x)&255]^(c>>>8);return (c^0xffffffff)>>>0;}
function walk(d){let a=[];for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);if(e.isDirectory())a.push(...walk(p));else a.push(p)}return a.sort();}
function u16(n){const b=Buffer.alloc(2);b.writeUInt16LE(n);return b}function u32(n){const b=Buffer.alloc(4);b.writeUInt32LE(n>>>0);return b}
const fd=fs.openSync(out,'w'),cent=[];let off=0;
for(const p of walk(root)){const data=fs.readFileSync(p),name=path.relative(root,p).replaceAll(path.sep,'/'),nb=Buffer.from(name),crc=crc32(data);const h=Buffer.concat([u32(0x04034b50),u16(20),u16(0),u16(0),u16(0),u16(0),u32(crc),u32(data.length),u32(data.length),u16(nb.length),u16(0),nb]);fs.writeSync(fd,h);fs.writeSync(fd,data);cent.push({name:nb,crc,size:data.length,off});off+=h.length+data.length;}
const cdStart=off;for(const c of cent){const h=Buffer.concat([u32(0x02014b50),u16(20),u16(20),u16(0),u16(0),u16(0),u16(0),u32(c.crc),u32(c.size),u32(c.size),u16(c.name.length),u16(0),u16(0),u16(0),u16(0),u32(0),u32(c.off),c.name]);fs.writeSync(fd,h);off+=h.length;}
const e=Buffer.concat([u32(0x06054b50),u16(0),u16(0),u16(cent.length),u16(cent.length),u32(off-cdStart),u32(cdStart),u16(0)]);fs.writeSync(fd,e);fs.closeSync(fd);console.log(JSON.stringify({files:cent.length,bytes:off+e.length}));
