import re,sys
for src,dst in [('t9.py','tEN9.py'),('t14.py','tEN14.py')]:
    s=open(src,encoding='utf8').read()
    s=s.replace("window.__LANG='ru'","window.__LANG='en'")
    s=s.replace("""def ck(cond,name):
    global n_ok""","""CYR=set(); PG=[None]
def cyr_scan():
    try:
        t=PG[0].evaluate("(()=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);while(w.nextNode()){const n=w.currentNode,e=n.parentElement;if(!e||!/[А-Яа-яЁё]/.test(n.nodeValue))continue;const r=e.getBoundingClientRect(),cs=getComputedStyle(e);if(r.width>0&&r.height>0&&cs.visibility!=='hidden'&&e.closest('.screen.on'))out.push(n.nodeValue.trim().slice(0,90))}return out})()")
        for x in t: CYR.add(x)
    except Exception as e: pass
def ck(cond,name):
    global n_ok
    cyr_scan()""")
    s=re.sub(r"(\n    pg=ctx.new_page\(\);[^\n]*)",r"\1; PG[0]=pg",s,1)
    s=s.replace("""pg.click(f'#ref .row[data-n="{doctor}"]')""","""pg.click('#ref .row[data-n=%s]'%json.dumps(pg.evaluate('_(%s)'%json.dumps(doctor))))""")
    s=s.replace("print('OK',n_ok,'FAIL',len(fails))","""cyr_scan(); miss=pg.evaluate('window.__MISS'); print('MISS',len(miss),json.dumps(miss[:40],ensure_ascii=False)); print('CYR',len(CYR)); [print('  CY',x) for x in sorted(CYR)]
    print('OK',n_ok,'FAIL',len(fails))""")
    s=re.sub(r"""f'#(\w+) \.row\[data-n="\{(\w+)\}"\]'""",r"""'#\1 .row[data-n=%s]'%json.dumps(pg.evaluate('_(%s)'%json.dumps(\2)))""",s)
    open(dst,'w',encoding='utf8').write(s)
