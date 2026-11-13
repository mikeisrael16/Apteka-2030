from playwright.sync_api import sync_playwright
import json,sys
URL='file:///home/claude/game/index.html'; W='/home/claude/work/'
fails=[]; n_ok=0
def ck(cond,name):
    global n_ok
    if cond: n_ok+=1; print("ok:",name,flush=True)
    else: fails.append(name); print('FAIL:',name)
with sync_playwright() as p:
    b=p.chromium.launch(channel='chrome',args=['--no-sandbox','--autoplay-policy=no-user-gesture-required'])
    ctx=b.new_context(viewport={'width':390,'height':844},device_scale_factor=1,has_touch=True)
    pg=ctx.new_page(); pg.add_init_script("window.__COMPAT=1")
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: m.type=='error' and errs.append(m.text))
    S=lambda: pg.evaluate("JSON.parse(JSON.stringify(__G.S))")
    R=lambda k: pg.evaluate(f"__G.R.{k}")
    C=lambda: pg.evaluate("JSON.parse(JSON.stringify(__G.R.c))")
    def w(ms): pg.wait_for_timeout(ms)
    def talk():
        for _ in range(60):
            if not pg.evaluate("!!(__G.R.wait||__G.R.typing)"): break
            pg.click('#dlg'); w(40)
    def until(expr,t=9000):
        pg.wait_for_function(expr,timeout=t)
    def checks(doctor):
        pg.click('#pName'); pg.click('#tName'); pg.click('#tDrug'); pg.click('#quote')
        pg.click('#tRef'); pg.click(f'#ref .row[data-n="{doctor}"]')
        pg.click('#tLamp'); pg.click('#seal')
    def take(m):
        pg.click('#s_shelfR'); pg.click(f'#shelf .item[data-m="{m}"]')
    def probe_drag():
        bx=pg.locator('#win').bounding_box(); y=bx['y']+bx['height']*.3
        pg.mouse.move(bx['x']+10,y); pg.mouse.down()
        for i in range(12): pg.mouse.move(bx['x']+10+(bx['width']-20)*((i%2)*1.0),y,steps=4)
        pg.mouse.up()
    def drag(sel,tsel,fx=.5,fy=.8):
        a=pg.locator(sel).bounding_box(); t=pg.locator(tsel).bounding_box()
        pg.mouse.move(a['x']+a['width']/2,a['y']+a['height']/2); pg.mouse.down()
        pg.mouse.move(t['x']+t['width']*fx,t['y']+t['height']*fy,steps=8); pg.mouse.up(); w(60)
    def give(): drag('#deskItem','#win')
    def swipe(dy):
        a=pg.locator('#lever').bounding_box(); x=a['x']+a['width']/2; y=a['y']+a['height']*(.2 if dy>0 else .8)
        pg.mouse.move(x,y); pg.mouse.down(); pg.mouse.move(x,y+dy,steps=10); pg.mouse.up(); w(60)
    def wipe():
        take('antiseptic'); ck(pg.is_visible('#deskItem'),'antiseptic appears on desk'); pg.click('#s_tray'); ck(S()['dirty'],'tap does not wipe'); give()
    NO='#choice button[data-k="no"]'; YES='#choice button[data-k="yes"]'
    def lever_open():
        talk(); until("__G.R.phase==='lever'"); swipe(200); until("__G.R.phase==='client'",9000)
    def measure():
        pg.click('#s_dosi')
        for _ in range(4): pg.click('#win',position={'x':40,'y':40})
    def stamp(t): pg.click('#s_doc'); pg.click('#tOk' if t=='ok' else '#tNo2'); pg.click('#talon'); 
    def tap_until(expr,t=15):
        for _ in range(int(t/0.08)):
            if pg.evaluate(expr): return
            if pg.evaluate("!!(__G.R.wait||__G.R.typing)"): pg.click('#dlg')
            w(80)
        until(expr,100)
    def nxt(): pg.click('#bNext'); tap_until("__G.R.phase==='client'||__G.R.phase==='voron'||__G.R.phase==='audit'||__G.R.phase==='bribe'")
    def journal_drag(): drag('#s_journal','#win',.5,.6)
    def close_shift():
        pg.click('#s_monitor'); ck(not pg.is_visible('#term'),'monitor blocked until window closed')
        swipe(-200); ck(R('closed') and R('lev')==0 and pg.locator('#shut.open').count()==0,'lever up closes shutters at end of shift')
        pg.click('#s_monitor')

    DOC={'petr':'Смирнов А.В.','anna':'Громов И.И.','viktor':'Смирнов А.В.','klavdia':'Казанцев П.Р.','gleb':'Орлов В.Г.','artem':'Петрова Н.К.','vera':'Смирнов А.В.','maria':'Ветрова М.А.','fedor':'Петрова Н.К.','egor':'Петрова Н.К.','vadim':'Лаптев О.Д.','annav':'Петрова Н.К.','timokha':'Лаптев О.Д.'}
    def docs(): pg.click('#s_tray'); pg.click('#s_doc')
    def inspect(): docs(); checks(DOC[C()['key']])
    def stamp_on(t): pg.click('#tOk' if t=='ok' else '#tNo2'); pg.click('#talon')
    def short(): return {k:v for k,v in pg.evaluate("Object.fromEntries(Object.keys(__G.S.stock).map(k=>[k,__G.S.doc[k]-__G.S.stock[k]]))").items() if v>0}
    def openv(): return [v for v in S()['viol'] if v['status']=='open']
    def sel(key): pg.click(f'.aurow[data-k="{key}"]')
    def finish_day(nextcp):
        close_shift(); pg.click('#tabs button[data-t="ord"]'); pg.click('button[data-o="antiseptic"][data-d="1"]'); pg.click('button[data-o="antiseptic"][data-d="1"]')
        pg.click('#tEnd'); until(f"__G.S.cp==={nextcp}")
    pg.goto(URL); w(300)
    pg.click('#mNew'); until("__G.R.phase==='ring'")
    def at_audit(day,cp,state):
        pg.evaluate(f"Object.assign(__G.S,{{day:{day}}},{state});__G.startCheckpoint({cp})"); nxt(); journal_drag(); tap_until(f"__G.R.phase==='auditm'||__G.S.cp==={cp+1}")
    def census(name):
        pg.click('#tCen'); pg.click(f'#cen .row[data-n="{name}"]') if name else pg.click('#cenNone')
    def ring_answer(): tap_until("__G.R.phase==='lever'"); swipe(200); tap_until("__G.R.phase==='ring'"); pg.click('#s_phone')
    # old save with legacy issues migrates into the ledger
    pg.evaluate("localStorage.setItem('nv2030apteka.manual',JSON.stringify({v:1,lay:2,day:3,cp:1,tp:300,dayStart:300,rad:0,journal:0,dirty:false,flags:{familyStrain:1},log:[],pending:[],issues:[{t:'old short',k:'short',drug:'stim'},{t:'old bad',k:'bad'},{t:'fixed',k:'short',drug:'bandage',fixed:true}],items:{},stock:{antiradin:2,antibiotic:2,painkiller:2,ai2:1,iodide:2,stim:0,antiseptic:3,bandage:4,sedative:2,antitoxin:1}}))")
    # ================= DAYS 7-11 =================
    FILL="(()=>{for(const k in __G.MEDS){const m=__G.MEDS[k],v=m.fake?0:m.nw?0:3;__G.S.stock[k]=v;__G.S.doc[k]=v}__G.S.bag={}})()"
    def serve(doctor,cen,drugs,pre=None,extra=False):
        measure(); docs(); checks(doctor)
        if cen is not False: census(cen)
        if extra: pg.click('#tExtra')
        stamp_on('ok'); pg.click('#iClose'); pg.click('#s_journal')
        for d in drugs: take(d); give()
    def refuse(): docs(); stamp_on('no')
    def cp_is(n,t=14000): tap_until(f"__G.S.cp==={n}",t/1000)
    pg.set_viewport_size({'width':390,'height':844}); w(200)
    FULL=FILL.replace("m.nw?0:3","3")
    pg.evaluate("Object.assign(__G.S,{flags:{sonSaved:'chizhov',family11:'fed',dad:'saved'},olya:70,viol:[{id:'z',k:'bad',t:'x',why:'',day:11,status:'open'}],warnings:1,items:{},tp:300,rad:0});"+FULL+";__G.S.doc.gem+=2;__G.S.stock.fakeT=1;__G.startDay(12)")
    ring_answer(); tap_until("__G.R.phase==='talk'&&__G.R.c&&__G.R.c.key==='gromov12'",25); ck(S()['olya']==100,'день 12: Оля сыта — отношения 100')
    pg.screenshot(path=W+'t12_gromov.png'); tap_until("__G.S.cp===3",30); s=S()
    ck(s['stock']['gem']==13 and s['doc']['gem']==13 and s['stock']['antiradin']==13 and s['stock']['fakeT']==0 and not short() and not openv(),'Громов: конвой +10, недостачи списаны, пустышки убраны, претензий нет')
    nxt(); pg.screenshot(path=W+'t12_anna.png'); tp=S()['tp']; serve('Петрова Н.К.','Крылова Анна Васильевна',['antibiotic','immunal']); s=S(); ck(s['tp']==tp+150 and s['items'].get('doll')==1 and not openv(),'Анна Васильевна: +150, кукла, чисто'); cp_is(4)
    nxt(); tp=S()['tp']; serve('Смирнов А.В.','Ильин Пётр Сергеевич',['antiradinM']); ck(S()['tp']==tp+150 and not openv() and C()['checks']['reg']=='ok','Пётр Ильин: прописка в переписи обновлена, +150'); cp_is(5); wipe()
    nxt(); tp=S()['tp']; serve('Ветрова М.А.','Сафина Эльвира Наилевна',['antitoxin']); ck(S()['tp']==tp+150,'Эльвира: +150'); cp_is(6)
    nxt(); pg.screenshot(path=W+'t12_refugee.png'); tp=S()['tp']; serve('Орлов В.Г.','Назаров Олег Тимурович',['bandage','antiseptic']); ck(S()['tp']==tp+100 and not openv(),'Беженец: +100, чисто'); cp_is(7)
    close_shift(); pg.click('#tabs button[data-t="ord"]'); ck('БЛОКАДА ПРОРВАНА' in pg.inner_text('#tbody'),'день 12: заявки не нужны'); pg.click('#tEnd'); until("__G.S.cp===8"); ck('ФИНАЛ' in pg.inner_text('#dNext') and pg.is_visible('#dNext'),'день 12 завершён → финал')
    pg.click('#dNext'); until("__G.R.phase==='ending'"); w(2500); ck(pg.is_visible('#ending') and 'ЧЕЛОВЕЧНОСТЬ' in pg.inner_text('#endTitle') and pg.locator('#endText p').count()==7 and S()['day']==13,'день 13: хорошая концовка'); pg.screenshot(path=W+'t13_good.png')
    pg.click('#endSkip'); ck(pg.locator('#endText p.on').count()==7 and 'свободны' in pg.inner_text('#endText'),'весь текст показан'); pg.screenshot(path=W+'t13_good2.png')
    a=pg.evaluate("__G.readSave(__G.K_AUTO)"); ck(a['day']==13 and a['cp']==0,'автосохранение на финале')
    pg.click('#endMenu'); ck(pg.is_visible('#menu') and 'Финал' in pg.inner_text('#mCont'),'из финала в меню'); pg.click('#mCont'); until("__G.R.phase==='ending'"); ck(pg.is_visible('#ending'),'«Продолжить» возвращает в финал')
    pg.evaluate("__G.S.flags={sonSaved:'x',family11:'fed',dad:'broken'};__G.startCheckpoint(0)"); w(600); pg.click('#endSkip'); t=pg.inner_text('#endText'); t0=t
    ck('ПОТЕРЯТЬ' in pg.inner_text('#endTitle') and 'родные голоса' in t and pg.locator('#endText p').count()==7,'плохая концовка: один общий текст (6 абзацев + титры)'); pg.screenshot(path=W+'t13_bad.png')
    pg.evaluate("__G.S.flags={family11:'ill',dad:'dead',nikitaFake:'x'};__G.startCheckpoint(0)"); w(400); pg.click('#endSkip'); t=pg.inner_text('#endText'); ck(t==t0 and 'некому тебя простить' in t,'плохая концовка одинакова при любых потерях'); pg.screenshot(path=W+'t13_bad2.png')
    pg.evaluate("__G.S.flags={sonSaved:'x',family11:'fed',dad:'saved',aFake:1,bFake:1,cFake:1};__G.startCheckpoint(0)"); w(300); ck('ПОТЕРЯТЬ' in pg.inner_text('#endTitle'),'3 обманутых пустышками → плохая концовка')
    pg.evaluate("__G.S.flags={sonSaved:'x',family11:'fed',dad:'saved',aFake:1,bFake:1};__G.startCheckpoint(0)"); w(300); ck('ЧЕЛОВЕЧНОСТЬ' in pg.inner_text('#endTitle'),'2 пустышки — ещё хорошая')
    pg.evaluate("Object.assign(__G.S,{day:12,flags:{family11:'ill'},olya:20});__G.startCheckpoint(1)"); until("__G.R.phase==='ring'"); pg.click('#s_phone'); w(900); ck('кашель' in pg.inner_text('#game'),'день 12: Оля больна (вариант Б)'); pg.screenshot(path=W+'t12_olya.png')
    pg.evaluate("Object.assign(__G.S,{day:9});__G.startCheckpoint(2)"); tap_until("__G.R.phase==='client'"); measure(); docs(); census('Ильин Пётр Сергеевич'); ck(C()['checks']['reg']=='bad','день 9: у Ильина в переписи всё ещё старый адрес')
    for vw,vh in [(360,640),(412,915)]:
        pg.set_viewport_size({'width':vw,'height':vh}); pg.evaluate("Object.assign(__G.S,{day:13});__G.startCheckpoint(0)"); w(400); bb=pg.locator('#endMenu').bounding_box(); ck(bb and bb['y']+bb['height']<=vh+1,f'финал помещается {vw}x{vh}')
    ck(not errs,f'no JS errors: {errs}')
    print('OK',n_ok,'FAIL',len(fails)); b.close()
