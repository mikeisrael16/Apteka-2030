from playwright.sync_api import sync_playwright
import json
URL='file:///home/claude/game/index.html'; D='/home/claude/work/shots_en/'
fails=[];n=0
def ck(c,name):
    global n
    if c: n+=1; print('ok:',name,flush=True)
    else: fails.append(name); print('FAIL:',name,flush=True)
CY="(()=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);while(w.nextNode()){const n=w.currentNode,e=n.parentElement;if(!e||!/[А-Яа-яЁё]/.test(n.nodeValue))continue;const r=e.getBoundingClientRect(),cs=getComputedStyle(e);if(r.width>0&&r.height>0&&cs.visibility!=='hidden'&&e.closest('.screen.on'))out.push(n.nodeValue.trim().slice(0,80))}return out})()"
with sync_playwright() as p:
    b=p.chromium.launch(channel='chrome',args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
    def page(loc):
        ctx=b.new_context(viewport={'width':390,'height':844},has_touch=True,locale=loc); pg=ctx.new_page()
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.goto(URL); pg.wait_for_timeout(600); return pg,errs
    pg,_e=page('ru-RU'); ck(pg.evaluate("document.documentElement.lang")=='ru','ru phone → Russian')
    ck('НОВАЯ ИГРА' in pg.inner_text('#mNew'),'ru menu text'); pg.screenshot(path=D+'menu_ru.png')
    pg,_e=page('de-DE'); ck(pg.evaluate("document.documentElement.lang")=='en','non-Russian phone → English')
    pg,errs=page('en-US'); ck(pg.evaluate("document.documentElement.lang")=='en','en phone → English')
    ck(pg.inner_text('#mNew').strip()=='NEW GAME','EN menu: '+pg.inner_text('#mNew'))
    ck('title' in pg.evaluate("document.querySelector('#menuArt img').src.slice(0,30)") or pg.evaluate("document.querySelector('#menuArt img').src.length")>1000,'title art present')
    ck(pg.evaluate(CY)==[],'menu: no Cyrillic '+json.dumps(pg.evaluate(CY),ensure_ascii=False))
    ck(pg.locator('#langSw button.on').get_attribute('data-l')=='en','EN flag highlighted')
    pg.screenshot(path=D+'menu_en.png')
    pg.click('#langSw button[data-l="ru"]'); pg.wait_for_timeout(700)
    ck(pg.evaluate("document.documentElement.lang")=='ru' and 'НОВАЯ' in pg.inner_text('#mNew'),'RU flag → reload in Russian')
    pg.click('#langSw button[data-l="en"]'); pg.wait_for_timeout(700)
    ck(pg.evaluate("document.documentElement.lang")=='en','EN flag → back to English')
    # scenes via test slots
    def slot(day,good):
        pg.evaluate(f"(()=>{{const s=__G.presetState({day},{str(good).lower()});}})()")
    pg.click('#mNew'); pg.wait_for_timeout(1500)
    for _ in range(40):
        if pg.evaluate("!!(__G.R.wait||__G.R.typing)"): pg.click('#dlg')
        pg.wait_for_timeout(120)
    pg.screenshot(path=D+'day1_start.png'); print('CY day1',pg.evaluate(CY))
    pg.click('#bPause'); pg.wait_for_timeout(300); pg.screenshot(path=D+'pause.png'); print('CY pause',pg.evaluate(CY))
    # endings in English: no recorded voice, timed text
    pg.evaluate("__G.toMenu&&0"); pg.goto(URL); pg.wait_for_timeout(500)
    pg.click('#mLoad'); pg.wait_for_timeout(300); pg.screenshot(path=D+'slots.png'); print('CY slots',pg.evaluate(CY))
    pg.click('#slotList button[data-s="12:1"]'); pg.wait_for_function("__G.S&&__G.S.day===12"); pg.wait_for_timeout(1500)
    for _ in range(30):
        if pg.evaluate("!!(__G.R.wait||__G.R.typing)"): pg.click('#dlg')
        pg.wait_for_timeout(120)
    pg.screenshot(path=D+'day12.png'); print('CY day12',pg.evaluate(CY))
    pg.evaluate("Object.assign(__G.S,{day:13});__G.startCheckpoint(0)"); pg.wait_for_timeout(3000)
    ck(pg.evaluate("!__G.NAR.au||__G.NAR.au.paused"),'EN good ending: recorded Russian voice is not played')
    ck('HUMANITY' in pg.inner_text('#endTitle') and pg.locator('#endText p.cur').count()==1,'EN good ending text runs by timer')
    pg.screenshot(path=D+'end_good.png'); print('CY end',pg.evaluate(CY))
    pg.click('#endSkip'); pg.wait_for_timeout(400); pg.evaluate("document.getElementById('endText').scrollTop=1e5"); pg.wait_for_timeout(300); pg.screenshot(path=D+'end_good_all.png')
    pg.click('#endMenu'); pg.wait_for_timeout(300); pg.click('#mCont'); pg.wait_for_function("__G.R.phase==='ending'"); pg.evaluate("__G.S.flags={family11:'ill'};__G.startCheckpoint(0)"); pg.wait_for_timeout(2500)
    ck(pg.evaluate("!__G.NAR.au||__G.NAR.au.paused") and 'EVERYTHING' in pg.inner_text('#endTitle'),'EN bad ending: no voice, English title')
    pg.screenshot(path=D+'end_bad.png'); print('CY endbad',pg.evaluate(CY))
    ck(errs==[],'no JS errors '+json.dumps(errs[:3]))
    print('MISS',pg.evaluate('window.__MISS'))
    print('OK',n,'FAIL',len(fails))
