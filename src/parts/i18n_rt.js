/* ===== i18n runtime (injected by build.py) ===== */
const LANG=(()=>{try{if(window.__LANG)return window.__LANG;const l=localStorage.getItem("nv2030apteka.lang");if(l==="ru"||l==="en")return l}catch(e){}
 const ls=(navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||"ru"]);const n=String(ls[0]||"ru").slice(0,2).toLowerCase();
 return ["ru","be","kk"].includes(n)?"ru":"en"})();
const I18N_EN=/*%%I18N%%*/{};
window.__MISS=[];
function _(s){if(LANG!=="en")return s;const t=I18N_EN[s];if(t===undefined){if(window.__MISS.length<200&&!window.__MISS.includes(s))window.__MISS.push(s);return s}return t}
function _t(q,...v){const key=q.map((x,i)=>(i?"{"+(i-1)+"}":"")+x).join("");const t=LANG==="en"?_(key):key;return t.replace(/\{(\d+)\}/g,(m,i)=>{const x=v[+i];return x===undefined?m:String(x)})}
function setLang(l){try{localStorage.setItem("nv2030apteka.lang",l)}catch(e){}location.reload()}
(function(){document.documentElement.lang=LANG;
 document.querySelectorAll("#langSw button").forEach(b=>{b.classList.toggle("on",b.dataset.l===LANG);b.addEventListener("click",()=>{if(b.dataset.l!==LANG)setLang(b.dataset.l)})});
 if(LANG!=="en")return;
 document.title="Nizhnevartovsk 2030: Pharmacy";
 const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);const ns=[];while(w.nextNode())ns.push(w.currentNode);
 ns.forEach(n=>{const pe=n.parentElement;if(pe&&(pe.tagName==="SCRIPT"||pe.tagName==="STYLE"))return;const v=n.nodeValue,t=v.trim();if(!t||!/[А-Яа-яЁё]/.test(t))return;const e=_(t);if(e!==t)n.nodeValue=v.replace(t,e)});
 document.querySelectorAll("[aria-label],[title],[placeholder],[alt]").forEach(el=>["aria-label","title","placeholder","alt"].forEach(a=>{const v=el.getAttribute(a);if(v&&/[А-Яа-яЁё]/.test(v))el.setAttribute(a,_(v.trim()))}));
 const ti=document.querySelector("#menuArt img");if(ti&&window.__TITLE_EN)ti.src=window.__TITLE_EN;
})();
