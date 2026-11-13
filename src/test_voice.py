from playwright.sync_api import sync_playwright
ok=0;fails=[]
def ck(c,n):
    global ok
    if c: ok+=1; print('ok:',n)
    else: fails.append(n); print('FAIL:',n)
with sync_playwright() as p:
    b=p.chromium.launch(channel='chrome',args=['--no-sandbox','--autoplay-policy=no-user-gesture-required']); pg=b.new_context(viewport={'width':390,'height':844}).new_page(); pg.add_init_script("window.__LANG='ru'")
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///home/claude/game/index.html'); pg.wait_for_timeout(400)
    pg.click('#mLoad'); pg.click('#slotList button[data-s="12:1"]'); pg.wait_for_function("__G.S&&__G.S.day===12")
    pg.evaluate("Object.assign(__G.S,{day:13});__G.startCheckpoint(0)"); pg.wait_for_timeout(2500)
    st=pg.evaluate("(()=>{const a=__G.NAR.au;return a?[a.paused,a.currentTime,a.duration,a.src.slice(0,22)]:null})()")
    print(st); ck(st and not st[0] and st[1]>1 and 80<st[2]<90,'хорошая концовка: играет запись (~85 с)')
    ck('ЧЕЛОВЕЧНОСТЬ' in pg.inner_text('#endTitle') and pg.locator('#endText p.cur').count()==1,'текст: первый абзац подсвечен')
    pg.evaluate("__G.NAR.au.currentTime=__G.NAR.au.duration*0.62"); pg.wait_for_timeout(900); i=pg.evaluate("[...document.querySelectorAll('#endText p')].findIndex(p=>p.classList.contains('cur'))"); ck(i>=3,f'текст идёт за голосом: на 62% — абзац {i+1}')
    pg.screenshot(path='/home/claude/work/vo_good.png')
    pg.evaluate("__G.NAR.au.currentTime=__G.NAR.au.duration-0.4"); pg.wait_for_timeout(1500); ck(pg.locator('#endText p.fin.on').count()==1 and pg.evaluate("__G.NAR.au.ended"),'конец записи → титры')
    pg.click('#endAgain'); pg.wait_for_timeout(1200); ck(pg.evaluate("!__G.NAR.au.paused&&__G.NAR.au.currentTime<3"),'«Заново» — запись сначала')
    pg.click('#endMenu'); pg.wait_for_timeout(300); ck(pg.evaluate("__G.NAR.au.paused"),'выход в меню останавливает голос')
    pg.click('#mCont'); pg.wait_for_function("__G.R.phase==='ending'"); pg.evaluate("__G.S.flags={family11:'ill'};__G.startCheckpoint(0)"); pg.wait_for_timeout(2000)
    st=pg.evaluate("(()=>{const a=__G.NAR.au;return [a.paused,a.currentTime,a.duration]})()"); ck('ПОТЕРЯТЬ' in pg.inner_text('#endTitle') and not st[0] and 78<st[2]<85,'плохая концовка: своя запись (~81 с)')
    pg.screenshot(path='/home/claude/work/vo_bad.png')
    pg.evaluate("__G.A.set.sfx=false;__G.startCheckpoint(0)"); pg.wait_for_timeout(1500); ck(pg.evaluate("__G.NAR.au.paused"),'звук выключен — запись не играет, текст по таймеру')
    ck(not errs,f'нет ошибок JS {errs[:3]}')
    print('OK',ok,'FAIL',len(fails)); b.close()
