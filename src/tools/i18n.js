// Wrap every Cyrillic string/template literal of the game script into _() / _t`` and list the keys.
const acorn=require('acorn'),fs=require('fs');
const [,,inF,outF,keysF]=process.argv;
const src=fs.readFileSync(inF,'utf8');
const CY=/[А-Яа-яЁё]/;
const ast=acorn.parse(src,{ecmaVersion:'latest',ranges:true});
const ins=[],keys=new Set();
(function walk(n,parent,pkey){
  if(!n||typeof n.type!=='string')return;
  if(n.type==='Literal'&&typeof n.value==='string'&&CY.test(n.value)){
    const isKey=parent&&(parent.type==='Property'||parent.type==='MethodDefinition'||parent.type==='PropertyDefinition')&&pkey==='key'&&!parent.computed;
    if(!isKey){ins.push([n.start,' _(']);ins.push([n.end,')']);keys.add(n.value)}
  }
  if(n.type==='TemplateLiteral'&&!(parent&&parent.type==='TaggedTemplateExpression')&&n.quasis.some(q=>CY.test(q.value.cooked))){
    ins.push([n.start,' _t']);keys.add(n.quasis.map((q,i)=>(i?'{'+(i-1)+'}':'')+q.value.cooked).join(''));
  }
  for(const k in n){if(k==='loc'||k==='range')continue;const v=n[k];
    if(Array.isArray(v))v.forEach(x=>x&&typeof x.type==='string'&&walk(x,n,k));
    else if(v&&typeof v.type==='string')walk(v,n,k)}
})(ast,null,null);
ins.sort((a,b)=>b[0]-a[0]);let out=src;
for(const [p,t] of ins)out=out.slice(0,p)+t+out.slice(p);
fs.writeFileSync(outF,out);fs.writeFileSync(keysF,JSON.stringify([...keys],null,0));
console.log('wrapped',ins.length,'keys',keys.size);
