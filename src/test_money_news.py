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
    pg=ctx.new_page()
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
        pg.click('#tLamp'); pg.click('#seal'); pg.click('#tPay')
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
    P='t14_'
    def shot(n): pg.screenshot(path=W+P+n+'.png')
    ck(pg.evaluate("__G.OLD")==False,'новый режим денег (не совместимость)')
    # ---- A. Day 1 tutorial: payment check + money on the desk
    pg.click('#s_phone'); tap_until("__G.R.phase==='lever'"); swipe(200); tap_until("__G.R.phase==='client'",30)
    s=S(); ck(s['tp']==200 and s['kdoc']==200 and s['pers']==100 and s['desk']==0,'старт: касса 200, личных 100'); pg.evaluate('__G.S.pers=0')
    docs(); doc=pg.evaluate("__G.R.c.def.doctor")
    pg.click('#pName'); pg.click('#tName'); pg.click('#tDrug'); pg.click('#quote'); pg.click('#tRef'); pg.click(f'#ref .row[data-n="{doc}"]'); pg.click('#tLamp'); pg.click('#seal')
    ck('Оплата' in pg.inner_text('#ihint') and '150 ТР' in pg.inner_text('#tPay'),'обучение: подсказка про оплату, в талоне «К оплате 150 ТР»'); shot('01_pay_hint')
    stamp_on('ok'); ck(not C().get('stamp') and 'оплата' in pg.inner_text('#imsg'),'штамп «ВЫДАНО» заблокирован без проверки оплаты')
    pg.click('#tPay'); ck(C()['checks']['pay']=='ok' and 'ОПЛАТА ✓' in pg.inner_text('#checks'),'проверка оплаты: деньги у клиента есть'); shot('02_pay_ok')
    stamp_on('ok'); pg.click('#iClose'); pg.click('#s_journal'); take('antiradin'); give(); s=S()
    ck(s['desk']==150 and s['tp']==200 and s['kdoc']==350 and pg.is_visible('#cashd') and '150' in pg.inner_text('#cashN'),'оплата легла на стол: 150 ТР, касса по журналу ждёт 350')
    tap_until("__G.R.phase==='between'",30); w(1200); shot('03_money_on_desk'); ck('КАССУ' in pg.inner_text('#hint'),'обучение: подсказка про кассу и рюкзак')
    pg.click('#bNext'); ck(R('phase')=='between' and 'Сначала уберите деньги' in pg.inner_text('#toast'),'день 1: нельзя звать следующего, пока деньги на столе')
    pg.click('#cashd'); ck(pg.is_visible('#cashM') and '150 ТР' in pg.inner_text('#cmV'),'нажатие на пачку открывает выбор суммы'); pg.click('#cmClose'); ck(S()['desk']==150,'отмена ничего не двигает')
    drag('#cashd','#kassa',.5,.5); s=S(); ck(s['desk']==0 and s['tp']==350 and s['pers']==0 and pg.evaluate("__G.cashShort()")==0 and not pg.is_visible('#cashd'),'деньги перетащены в кассу: 350, сходится'); shot('04_in_kassa')
    # ---- B. borrow from the cash box, backpack and back
    pg.click('#kassa'); shot('05a_picker'); pg.click('#cmQ [data-q="100"]'); pg.click('#cmAct [data-to="d"]'); s=S(); ck(s['tp']==250 and s['desk']==100,'касса: выбрал 100 ТР → на стол')
    drag('#cashd','#bag',.5,.5); s=S(); ck(s['pers']==100 and s['desk']==0 and pg.evaluate("__G.cashShort()")==100 and '100' in pg.inner_text('#bagN'),'со стола в рюкзак: личные 100, недостача кассы 100'); shot('05_borrowed')
    pg.click('#bag'); ck('Личные деньги: 100 ТР' in pg.inner_text('#invBody'),'рюкзак показывает личные деньги'); shot('06_backpack')
    pg.click('#invBody [data-cash]'); pg.click('#cmQ [data-q="all"]'); pg.click('#cmAct [data-to="d"]'); s=S(); ck(s['pers']==0 and s['desk']==100,'из рюкзака на стол: всё (100 ТР)')
    drag('#cashd','#kassa',.5,.5); ck(S()['tp']==350 and pg.evaluate("__G.cashShort()")==0,'долг кассе возвращён')
    # ---- C. audit: cash shortage
    BASE="{viol:[],warnings:0,lies:0,susp:0,flags:{cashTut:1},items:{},desk:0,rad:0}"
    FULL="(()=>{for(const k in __G.MEDS){const m=__G.MEDS[k],v=m.fake?0:3;__G.S.stock[k]=v;__G.S.doc[k]=v}__G.S.bag={}})()"
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{tp:100,kdoc:300,pers:500}});"+FULL); at_audit(2,5,"{}")
    ck(R('phase')=='auditm' and 'CASH' in pg.inner_text('#auBody') and '200 ТР' in pg.inner_text('#auBody') and pg.evaluate("!!__G.A.tT||!__G.A.ctx"),'ревизия: недостача кассы 200 ТР — отдельная претензия'); shot('07_audit_cash')
    pg.click('#auTruth'); tap_until("__G.S.cp===6",30); s=S(); ck(s['tp']==300 and s['pers']==200 and s['warnings']==1 and pg.evaluate("!__G.A.tT"),'правда: 200 ТР удержаны из личных в кассу (и −100 за дрова дома), предупреждение; тревожная музыка выключена')
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{tp:100,kdoc:300,pers:500}});"+FULL); at_audit(2,5,"{}"); pg.click('#auBribe'); s=S(); ck(s['pers']==400 and pg.evaluate("__G.cashShort()")==0 and s['tp']==100,'взятка 100 ТР из личных закрыла недостачу кассы'); pg.click('#auDone'); tap_until("__G.S.cp===6",30)
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{tp:300,kdoc:300,pers:0}});"+FULL); at_audit(2,5,"{}"); tap_until("__G.S.cp===6",30); s=S(); ck(s['pers']==-50 and s['tp']==300 and any(l['v']==50 and l.get('w')=='p' for l in s['log']),'чистая ревизия: премия 50 ТР — в личные (минус 100 за дрова дома), касса не тронута')
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{tp:100,kdoc:300,pers:0,desk:200}});"+FULL); at_audit(2,5,"{}"); tap_until("__G.S.cp===6",30); ck(S()['tp']==300 and S()['desk']==0,'деньги со стола на ревизии считаются кассой')
    # ---- D. clients who cannot pay
    ck(pg.evaluate("__G.DAYS[5].stages[__G.NEWST[5]]")=='n:vera2' and pg.evaluate("__G.DAYS[9].stages[__G.NEWST[9]]")=='n:zahar2' and pg.evaluate("__G.DAYS[11].stages[__G.NEWST[11]]")=='n:nina2','новые клиенты без денег: дни 5, 9, 11')
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:5,tp:300,kdoc:300,pers:100}});"+FULL+";__G.startCheckpoint(__G.NEWST[5])"); nxt()
    ck(C()['key']=='vera2','день 5: Вера Лебедева без денег'); measure(); docs(); checks('Петрова Н.К.'); census('Лебедева Вера Олеговна'); c=C()['checks']
    ck(c['pay']=='bad' and all(c[k]=='ok' for k in ['name','drug','doctor','seal','reg']) ,'Вера: документы чистые, платить нечем'); shot('08_no_money')
    stamp_on('ok'); ck('касса недосчитается 90' in pg.inner_text('#imsg'),'штамп ставится, предупреждение о недостаче 90 ТР'); pg.click('#iClose'); pg.click('#s_journal'); take('antibiotic'); give(); s=S()
    ck(s['desk']==0 and s['kdoc']==390 and s['tp']==300 and pg.evaluate("__G.cashShort()")==90 and s['flags']['vera2']=='helped' and not openv() and not short(),'выдано бесплатно: нарушения нет, касса должна 90 ТР'); shot('09_given_free')
    tap_until(f"__G.S.cp==={pg.evaluate('__G.NEWST[5]')+1}",30); pg.click('#bag'); pg.click('#invBody [data-cash]'); pg.click('#cmQ [data-q="all"]'); pg.click('#cmAct [data-to="k"]'); s=S(); ck(s['tp']==400 and s['pers']==0 and pg.evaluate("__G.cashShort()")==0,'доложил 100 ТР из своих — касса сошлась')
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:5,tp:300,kdoc:300,pers:0,pending:[]}});"+FULL+";__G.startCheckpoint(__G.NEWST[5])"); nxt(); docs(); stamp_on('no'); tap_until(f"__G.S.cp==={pg.evaluate('__G.NEWST[5]')+1}",30); s=S()
    ck(s['flags']['vera2']=='refused' and not s['pending'] and s['kdoc']==300,'отказ неплатёжеспособной — без штрафа')
    for day,key,doc,name,drugs,due in [(9,'zahar2','Петрова Н.К.','Лютый Захар Васильевич',['painkiller','bandage'],70),(11,'nina2','Петрова Н.К.','Кузнецова Нина Павловна',['gem'],110)]:
        pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:{day},tp:300,kdoc:300,pers:0,olya:60}});"+FULL+f";__G.startCheckpoint(__G.NEWST[{day}])"); nxt(); serve(doc,name,drugs); s=S()
        ck(C()['key']==key and s['kdoc']==300+due and s['desk']==0 and not openv(),f'{key}: чистые документы, выдано без оплаты, касса −{due}')
        if day==11: shot('10_nina')
        tap_until(f"__G.S.cp==={pg.evaluate(f'__G.NEWST[{day}]')+1}",30)
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:7,tp:300,kdoc:300,pers:0}});"+FULL+";__G.startCheckpoint(5)"); nxt(); docs(); pg.click('#tPay'); ck(C()['key']=='serafim' and C()['checks']['pay']=='bad' and '190' in pg.inner_text('#tPay') and 'крест' in pg.inner_text('#imsg'),'Серафим: платит крестом, касса ждёт 190 ТР')
    # paying client on a later day, pocket the money
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:7,tp:300,kdoc:300,pers:0}});"+FULL+";__G.startCheckpoint(4)"); tap_until("__G.R.phase==='client'",30); serve('Петрова Н.К.','Лютый Захар Васильевич',['strept','ointment']); s=S(); ck(s['desk']==150 and s['kdoc']==450,'Захар заплатил 150 — на столе')
    drag('#cashd','#bag',.5,.5); s=S(); ck(s['pers']==150 and s['tp']==300 and pg.evaluate("__G.cashShort()")==150,'деньги клиента мимо кассы: личные +150, недостача кассы 150'); shot('11_pocketed')
    # cash client without talon: money is nobody's on paper
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:9,tp:300,kdoc:300,pers:0}});"+FULL+";__G.startCheckpoint(5)"); nxt(); pg.click(YES); take('stim'); give(); take('oftalmo'); give(); s=S(); ck(s['desk']==250 and s['kdoc']==300,'Геннадий без талона: 250 ТР на столе, по журналу их нет')
    drag('#cashd','#bag',.5,.5); ck(S()['pers']==250 and pg.evaluate("__G.cashShort()")==0 and short().get('stim')==1,'в рюкзак: касса сходится, но на складе недостача')
    # ---- E. Voron and orders
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:7,tp:300,kdoc:300,pers:60}});"+FULL+";__G.startCheckpoint(8)"); nxt(); ck('60 ТР' in pg.inner_text('#mkBody'),'Ворон видит только личные деньги'); pg.click('#mkF_fakeT'); s=S(); ck(s['pers']==10 and s['tp']==300 and s['stock']['fakeT']==1,'пустышка куплена на личные'); ck(pg.locator('#mkF_fakeT').is_disabled(),'на кассу у Ворона не купишь'); shot('12_voron'); pg.click('#mkLeave'); tap_until("__G.S.cp===9",30)
    pg.evaluate("__G.S.desk=40"); close_shift(); ck('В КАССЕ: 340' in pg.inner_text('#tbody') and 'Личные деньги (рюкзак): 10' in pg.inner_text('#tbody'),'терминал: касса и личные раздельно'); shot('13_terminal')
    pg.click('#tabs button[data-t="ord"]'); pg.click('button[data-o="strept"][data-d="1"]'); pg.click('#tEnd'); until("__G.S.cp===10"); s=S(); ck(s['tp']==260 and s['kdoc']==220 and s['pers']==10 and s['desk']==0 and s['stock']['strept']==4,'заявка оплачена из кассы; деньги со стола убраны в кассу'); shot('14_report')
    ck('В КАССЕ АПТЕКИ' in pg.inner_text('#doneBox') and 'ЛИЧНЫЕ' in pg.inner_text('#doneBox'),'отчёт: касса и личные')
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:11,tp:300,kdoc:300,pers:520,olya:60,flags:{{cashTut:1,food:'promise',np11:1}}}});"+FULL+";__G.startCheckpoint(__G.NEWST[11]+1)"); nxt(); ck(R('phase')=='voron' and '520 ТР' in pg.inner_text('#mkBody'),'день 11: Ворон (обещаны 500 ТР) — рынок открывается'); pg.click('#mkLeave'); tap_until(f"__G.S.cp==={pg.evaluate('__G.NEWST[11]')+2}",30)
    nxt(); journal_drag(); tap_until(f"__G.R.phase==='auditm'||__G.S.cp==={pg.evaluate('__G.NEWST[11]')+3}",40); 
    if R('phase')=='auditm': pg.click('#auTruth')
    tap_until(f"__G.S.cp==={pg.evaluate('__G.NEWST[11]')+3}",40); p0=S()['pers']; close_shift(); ck('хватает' in pg.inner_text('#tbody'),'терминал: 500 ТР личных для Оли есть'); pg.click('#tEnd'); until(f"__G.S.cp==={pg.evaluate('__G.NEWST[11]')+4}"); s=S(); ck(s['flags']['family11']=='fed' and s['pers']==p0-570 and s['tp']==300,'продукты семье (500) и ежедневные 70 оплачены из личных, касса не тронута')
    # ---- F. newspaper
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{flags:{{cashTut:1,anna:'quarantine',klavdia:'helped',gleb:'talon',audit:'clean'}}}});__G.startDay(3)"); tap_until("__G.R.phase==='lever'",30); swipe(200); until("__G.R.phase==='paper'"); w(500); shot('15_paper_tray')
    ck(pg.evaluate("document.getElementById('s_tray').classList.contains('npaper')") and S()['cp']==0,'день 3: газета в лотке окна')
    pg.click('#s_tray'); t=pg.inner_text('#newsP').lower(); ck(pg.is_visible('#news') and 'вестник' in t and 'изолирована' in t and 'благодарит' in t and 'авария на тэц-2' in t and 'премией' in t and 'разыскивается' in t,'газета №1: новости по решениям игрока'); shot('16_newspaper')
    pg.click('#newsClose'); until("__G.S.cp===1"); ck(S()['flags'].get('np3')==1,'газета прочитана → смена продолжается')
    pg.evaluate("__G.S.flags={cashTut:1,anna:'saved',gleb:'stim'}"); t=pg.evaluate("JSON.stringify(__G.newsFor(3))"); ck('Чудо на Омской' in t and 'выстояла' in t and 'найдена мёртвой' in t,'газета меняется от решений')
    for d in [5,7,9,11]:
        n=pg.evaluate(f"__G.newsFor({d})"); ck(n['lead'] and len(n['it'])>=4 and n['box'],f'газета дня {d}: {len(n["it"])} заметок')
    pg.evaluate("__G.S.flags={cashTut:1,petr2Fake:'x',rodion:'quarantine',larisa:'helped'};__G.startDay(11)"); tap_until("__G.R.phase==='lever'",30); swipe(200); until("__G.R.phase==='paper'"); pg.click('#s_tray'); t=pg.inner_text('#newsP').lower(); ck('коме' in t and 'налётчик задержан' in t and 'муляжи' in t,'газета дня 11: кома Ильина, налётчик, муляжи'); shot('17_newspaper11'); pg.click('#newsClose'); until("__G.S.cp===1")
    pg.evaluate("__G.S.flags={cashTut:1};__G.startDay(4)"); tap_until("__G.R.phase==='lever'",30); swipe(200); until("__G.S.cp===1"); ck(R('phase')!='paper','день 4: газеты нет (через день)')
    # ---- G. old save migration
    old=pg.evaluate("(()=>{const s=JSON.parse(JSON.stringify(__G.S));s.day=9;s.cp=6;s.lay=2;s.tp=420;delete s.pers;delete s.desk;delete s.kdoc;localStorage.setItem(__G.K_MAN,JSON.stringify(s));return __G.readSave(__G.K_MAN)})()")
    ck(old['cp']==7 and old['pers']==0 and old['kdoc']==420 and old['lay']==3,'старое сохранение: этап сдвинут, касса перенесена')
    # ---- H. test slots
    pg.goto(URL); w(400); pg.click('#mLoad'); ck(pg.is_visible('#slots') and pg.locator('#slotList button').count()==7,'меню «Загрузить»: моё сохранение + 6 тестовых'); shot('18_slots')
    pg.click('#slotList button[data-s="12:0"]'); until("__G.S&&__G.S.day===12"); s=S(); ck(s['flags']['family11']=='ill' and s['flags']['dad']=='dead' and not s['flags'].get('sonSaved') and pg.evaluate("__G.endingKind().good")==False,'тест День 12 (плохой путь)')
    pg.goto(URL); w(300); pg.click('#mLoad'); pg.click('#slotList button[data-s="12:1"]'); until("__G.S&&__G.S.day===12"); ck(pg.evaluate("__G.endingKind().good")==True,'тест День 12 (хороший путь)')
    ring_answer(); tap_until("__G.R.phase==='talk'&&__G.R.c&&__G.R.c.key==='gromov12'",30); ck(pg.evaluate("!__G.A.tT"),'день 12: Громов без тревожной музыки'); tap_until("__G.S.cp===3",40); nxt(); serve('Петрова Н.К.','Крылова Анна Васильевна',['antibiotic','immunal']); ck(S()['desk']==150,'день 12 из тестового сохранения играется: оплата на столе')
    pg.goto(URL); w(300); pg.click('#mLoad'); pg.click('#slotList button[data-s="7:1"]'); until("__G.S&&__G.S.day===7"); tap_until("__G.R.phase==='lever'",30); swipe(200); until("__G.R.phase==='paper'"); pg.click('#s_tray'); ck('освобождений' in pg.inner_text('#newsP'),'тест День 7: газета, затем письмо'); pg.click('#newsClose'); until("__G.R.phase==='letter'")
    pg.goto(URL); w(300); pg.click('#mLoad'); pg.click('#slotList button[data-s="10:0"]'); until("__G.S&&__G.S.day===10"); ck(S()['flags']['dad']=='dead','тест День 10 (плохой путь)')
    # ---- I. layouts
    for vw,vh in [(360,640),(412,915),(390,844)]:
        pg.set_viewport_size({'width':vw,'height':vh}); pg.evaluate("__G.S.desk=150;__G.startCheckpoint(3)"); w(500)
        k=pg.locator('#kassa').bounding_box(); c=pg.locator('#cashd').bounding_box()
        hit=pg.evaluate(f"document.elementFromPoint({k['x']+k['width']*.3},{k['y']+k['height']*.4}).id")
        ck(k['x']>=0 and c['x']+c['width']<=vw and hit=='kassa',f'касса и деньги на месте {vw}x{vh} (hit={hit})')
    shot('19_day10')
    # ---- J. family budget, radiation, weather
    pg.set_viewport_size({'width':390,'height':844})
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:3,tp:300,kdoc:300,pers:80,olya:60,flags:{{cashTut:1}}}});"+FULL+";__G.startCheckpoint(7)"); close_shift(); ck('Семье на вечер: еда 30 + дрова 20' in pg.inner_text('#tbody') and 'хватает' in pg.inner_text('#tbody'),'терминал: семейный бюджет на вечер'); shot('20_budget')
    pg.click('#tEnd'); until("__G.S.cp===8"); s=S(); ck(s['pers']==30 and s['tp']==300 and s['olya']==60,'еда 30 + дрова 20 списаны из личных')
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:3,tp:300,kdoc:300,pers:35,olya:60,flags:{{cashTut:1}}}});"+FULL+";__G.startCheckpoint(7)"); close_shift(); pg.click('#tEnd'); until("__G.S.cp===8"); s=S(); ck(s['pers']==5 and s['olya']==56 and s['flags']['hungry']==1 and 'не хватило на дрова' in pg.inner_text('#doneBox'),'денег хватило только на еду: Оля −4')
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:10,tp:300,kdoc:300,pers:0,olya:60,flags:{{cashTut:1}}}});"+FULL+";__G.startCheckpoint(7)"); close_shift(); pg.click('#tEnd'); until("__G.S.cp===8"); s=S(); ck(s['pers']==0 and s['olya']==52 and pg.evaluate("__G.homeCost().food")==50,'личных нет: семья без еды и дров, Оля −8; в дефицит еда дороже')
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{rad:55,flags:{{cashTut:1}},bag:{{}}}});__G.startDay(4)"); tap_until("__G.R.phase==='lever'",30); s=S(); ck(s['rad']==80 and 'ЛУЧЕВАЯ БОЛЕЗНЬ' in pg.inner_text('#radbar') and pg.evaluate("document.getElementById('scene').classList.contains('sick')"),'доза 55% не снята → утром лучевая болезнь 80%'); shot('21_sick')
    pg.evaluate("__G.S.bag={antiradinM:1,antiradin:1}"); pg.click('#bag'); shot('22_drink'); pg.click('#invBody [data-drink="antiradinM"]'); ck(S()['rad']==30 and not S()['bag']['antiradinM'],'«Антирадин-М» выпит: 80 → 30%'); pg.click('#invBody [data-drink="antiradin"]'); ck(S()['rad']==0,'«Антирадин»: −30%'); pg.click('#invClose')
    ck('ЛУЧЕВАЯ' not in pg.inner_text('#radbar') and not pg.evaluate("document.getElementById('scene').classList.contains('sick')"),'болезнь снята')
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{rad:45,flags:{{cashTut:1}}}});__G.startDay(4)"); tap_until("__G.R.phase==='lever'",30); ck(S()['rad']==45,'ниже 50% — без последствий')
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{rad:85,flags:{{cashTut:1}}}});__G.startDay(5)"); until("__G.R.phase==='done'"); ck(S()['rad']==100 and 'ПОГИБЛИ' in pg.inner_text('#dTitle') and not pg.is_visible('#dNext'),'80%+ не снято → 100%, смерть'); shot('23_death'); pg.click('#dMenu')
    pg.click('#mLoad'); pg.click('#slotList button[data-s="10:1"]'); until("__G.S&&__G.S.day===10"); ck(pg.locator('#snow').count()==1 and not pg.evaluate("document.getElementById('scene').classList.contains('calm')"),'снег за окном, день 10 — буря')
    pg.evaluate("(()=>{document.getElementById('scene').classList.remove('gust','brown');const r=Math.random;Math.random=()=>0.01;__G.weatherTick();Math.random=r})()"); w(900); ck(pg.evaluate("document.getElementById('scene').classList.contains('gust')") and pg.evaluate("document.getElementById('scene').classList.contains('brown')"),'порыв ветра и перебой света'); shot('24_brownout'); w(3500)
    ck(not pg.evaluate("document.getElementById('scene').classList.contains('brown')"),'свет вернулся')
    # ---- K. v2.2: any amount, debt, minor violations, toys, menu
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:3,tp:300,kdoc:300,pers:40,desk:0,olya:50}});"+FULL+";__G.startCheckpoint(2)"); w(400)
    pg.click('#kassa'); pg.click('#cmQ [data-q="20"]'); pg.click('#cmRow [data-d="10"]'); ck('30 ТР' in pg.inner_text('#cmV'),'выбор суммы: 20 + 10 = 30'); pg.click('#cmAct [data-to="p"]'); s=S(); ck(s['tp']==270 and s['pers']==70 and s['desk']==0 and pg.evaluate("__G.cashShort()")==30,'30 ТР из кассы сразу в рюкзак')
    pg.click('#bag'); pg.click('#invBody [data-cash]'); pg.evaluate("(()=>{const r=document.getElementById('cmR');r.value=15;r.dispatchEvent(new Event('input'))})()"); ck('15 ТР' in pg.inner_text('#cmV'),'ползунок: 15 ТР'); pg.click('#cmAct [data-to="k"]'); s=S(); ck(s['tp']==285 and s['pers']==55,'15 ТР из рюкзака в кассу')
    pg.evaluate("__G.S.desk=150"); pg.click('#hDay'); w(200); pg.evaluate("__G.startCheckpoint(2)"); pg.evaluate("__G.S.desk=150"); w(300); pg.click('#hTime'); 
    pg.evaluate("document.getElementById('cashd').classList.add('on')"); pg.click('#cashd'); pg.click('#cmQ [data-q="100"]'); pg.click('#cmAct [data-to="k"]'); s=S(); ck(s['desk']==50,'пачку со стола можно разделить: 100 в кассу, 50 осталось'); drag('#cashd','#bag',.5,.5); ck(S()['desk']==0,'остаток перетащен в рюкзак (он теперь висит у окна)')
    bb=pg.locator('#bag').bounding_box(); l=pg.locator('#lever').bounding_box(); ck(bb['y']+bb['height']<=l['y']+4 and bb['width']>90 and not pg.is_visible('#bag img'),'рюкзак — часть сцены, рычаг под ним'); shot('25_scene')
    # debt
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{pers:-60,flags:{{cashTut:1}}}});__G.startDay(4)"); w(700); tap_until("__G.R.phase==='lever'",30); ck(S()['flags']['debt']==1 and 'ДОЛГ' in pg.inner_text('#bagN'),'минус в личных: предупреждение, 2 дня'); shot('26_debt')
    pg.evaluate("__G.startDay(5)"); w(700); ck(S()['flags']['debt']==2 and R('phase')!='done','второй день в минусе: последний день')
    pg.evaluate("__G.startDay(6)"); until("__G.R.phase==='done'"); ck('НЕ ПЕРЕЖИЛА' in pg.inner_text('#dTitle') and not pg.is_visible('#dNext'),'третий день в минусе → игра проиграна'); shot('27_debt_over'); pg.click('#dMenu')
    pg.click('#mLoad'); pg.click('#slotList button[data-s="10:1"]'); until("__G.S&&__G.S.day===10"); pg.evaluate("__G.S.pers=-10;__G.S.flags.debt=2;__G.startDay(11)"); w(500); pg.evaluate("__G.S.pers=40;__G.startDay(12)"); w(600); ck(S()['flags']['debt']==0 and R('phase')!='done','вышел в плюс — счётчик долга сброшен')
    pg.evaluate("__G.S.pers=10;__G.S.pending=[];__G.S.log=[]"); 
    # minor violation: the extra line
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:3,tp:300,kdoc:300,pers:200,olya:50}});"+FULL+";__G.startCheckpoint(1)"); tap_until("__G.R.phase==='client'",30); measure(); docs(); pg.click('#tExtra'); ck('ПРОСРОЧЕН' in pg.inner_text('#imsg') and 'bad' in pg.get_attribute('#tExtra','class'),'доп. проверка: срок действия талона'); shot('28_extra')
    checks(pg.evaluate("__G.R.c.def.doctor")); stamp_on('ok'); pg.click('#iClose'); pg.click('#s_journal'); take('antibiotic'); give(); v=openv(); ck(len(v)==1 and v[0]['k']=='note' and 'просрочен' in v[0]['why'],'выдача по просроченному талону = замечание (NOTE), не грубое нарушение')
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{tp:300,kdoc:300,pers:200,viol:[{{id:'n1',k:'note',t:'Замечание: выдача по талону с изъяном — Вера',why:'талон просрочен',day:2,status:'open'}}]}});"+FULL); at_audit(2,5,"{}"); ck('NOTE' in pg.inner_text('#auBody'),'ревизия видит замечание'); shot('29_note_audit'); pg.click('#auTruth'); tap_until("__G.S.cp===6",30); s=S()
    ck(s['warnings']==0 and any(l['v']==-50 and 'мелкое' in l['t'] for l in s['log']) and not any('Премия' in l['t'] for l in s['log']),'замечание: штраф 50 ТР, без предупреждения, без премии')
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{tp:300,kdoc:300,pers:200,viol:[{{id:'b1',k:'bad',t:'Выдача по неправильному талону',why:'врач без допуска',day:2,status:'open'}}]}});"+FULL); at_audit(2,5,"{}"); pg.click('#auTruth'); tap_until("__G.S.cp===6",30); ck(S()['warnings']==1,'основная проверка провалена → предупреждение (строже)')
    pg.evaluate("__G.S.olya=50;__G.S.flags={};__G.S.items={};__G.addItem('toys')"); ck(S()['olya']==70 and S()['items']['toys']==1,'игрушки для Алины: +20 сразу при получении'); pg.click('#bag'); ck(pg.locator('#invBody img[src^="data:image/webp"]').count()>=2 and 'ПОДАРИТЬ' not in pg.inner_text('#invBody'),'иконка игрушек из нового набора'); 
    pg.evaluate("for(const k of ['radiolamp','pelt','ammo','spirit','container','stew','fishoil','knife','copper','parts'])__G.addItem(k)"); pg.click('#invClose'); pg.click('#bag'); shot('30_icons'); pg.click('#invClose')
    for vw,vh in [(390,844),(360,640),(412,915)]:
        pg.set_viewport_size({'width':vw,'height':vh}); pg.goto(URL); w(500)
        ys=[pg.locator(i).bounding_box() for i in ['#mNew','#mCont','#mLoad','#mSound']]; img=pg.locator('#mBot img').bounding_box()
        ck(all(ys[i]['y']+ys[i]['height']<=ys[i+1]['y']+1 for i in range(3)) and ys[3]['y']+ys[3]['height']<=img['y']+img['height']*.45 and img['y']+img['height']<=vh+1 and vh-(img['y']+img['height'])>vw*.1,f'меню {vw}x{vh}: 4 кнопки по порядку, звук под «Загрузить», подпись студии поднята')
        if vw==390: shot('31_menu')
    pg.click('#mSound'); ck('ВКЛЮЧИТЬ' in pg.inner_text('#mSound'),'кнопка звука переключается'); pg.click('#mSound')
    # ---- L. out of stock after approval
    pg.set_viewport_size({'width':390,'height':844}); pg.goto(URL); w(400); pg.click('#mLoad'); pg.click('#slotList button[data-s="7:1"]'); until("__G.S&&__G.S.day===7"); w(300)
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:4,tp:300,kdoc:300,pers:50,olya:50,pending:[]}});"+FULL+";__G.S.stock.antibiotic=0;__G.S.doc.antibiotic=0;__G.startCheckpoint(4)"); nxt(); ck(C()['key']=='annav','день 4: Анна Васильевна, антибиотиков на полке нет')
    measure(); docs(); pg.click('#tDrug'); pg.click('#quote'); ck('НА ПОЛКЕ НЕТ' in pg.inner_text('#imsg'),'сверка препарата сразу говорит, что его нет на полке'); shot('32_nostock_check')
    checks('Петрова Н.К.'); stamp_on('ok'); ck('НЕТ В НАЛИЧИИ' in pg.inner_text('#imsg'),'после «ВЫДАНО» — подсказка про выход'); pg.click('#iClose'); pg.click('#s_journal'); w(300)
    ck(pg.is_visible('#bNoSt'),'кнопка «НЕТ В НАЛИЧИИ · ОТПУСТИТЬ»'); shot('33_nostock_btn'); pg.click('#bNoSt'); tap_until("__G.S.cp===5",30); s=S()
    ck(s['flags']['annav']=='nostock' and not openv() and not s['pending'] and s['kdoc']==300 and s['desk']==0,'клиент отпущен: без нарушения, без штрафа, касса не тронута')
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:7,tp:300,kdoc:300,pers:50}});"+FULL+";__G.S.stock.ointment=0;__G.S.doc.ointment=0;__G.startCheckpoint(4)"); tap_until("__G.R.phase==='client'",30); measure(); docs(); checks('Петрова Н.К.'); census('Лютый Захар Васильевич'); stamp_on('ok'); pg.click('#iClose'); pg.click('#s_journal')
    ck(pg.is_visible('#bNoSt'),'два препарата, одного нет — кнопка есть сразу'); take('strept'); give(); pg.click('#bNoSt'); tap_until("__G.S.cp===5",30); s=S(); ck(s['flags']['zahar']=='partial' and s['desk']==80 and s['kdoc']==380 and s['stock']['strept']==2,'частичная выдача: оплата только за выданное (80 из 150)')
    pg.evaluate(f"Object.assign(__G.S,{BASE},{{day:7,tp:300,kdoc:300,pers:50}});"+FULL+";__G.startCheckpoint(4)"); tap_until("__G.R.phase==='client'",30); measure(); docs(); checks('Петрова Н.К.'); census('Лютый Захар Васильевич'); stamp_on('ok'); pg.click('#iClose'); ck(not pg.is_visible('#bNoSt'),'всё есть на полке — кнопки нет')
    ck(not errs,f'no JS errors: {errs[:4]}')
    print('OK',n_ok,'FAIL',len(fails)); b.close()
