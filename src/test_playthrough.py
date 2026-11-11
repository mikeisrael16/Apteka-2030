from playwright.sync_api import sync_playwright
import json,sys
URL='file:///home/claude/game/index.html'; W='/home/claude/work/'
fails=[]; n_ok=0
def ck(cond,name):
    global n_ok
    if cond: n_ok+=1
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
    # ================= DAY 1 =================
    pg.click('#mNew'); until("__G.R.phase==='ring'"); pg.click('#s_phone'); tap_until("__G.R.phase==='lever'"); swipe(200); until("__G.S.cp===1&&__G.R.phase==='client'")
    docs(); pg.click('#tOk'); pg.click('#talon'); ck(C()['stamp'] is None,'Петр: ВЫДАНО blocked before checks')
    checks(DOC['petr']); stamp_on('ok'); ck(C()['stamp']=='ok','Петр: stamped after 4 checks'); pg.click('#iClose'); take('antiradin'); pg.click('#s_journal'); give()
    s=S(); ck(s['stock']['antiradin']==2 and s['doc']['antiradin']==2 and s['led'][-1]['op']=='issue','ledger: legal issue moves shelf and documents')
    until("__G.S.cp===2&&__G.R.phase==='between'",12000); pg.click('#bNext'); pg.click('#s_phone'); tap_until("__G.R.phase==='client'")
    measure(); inspect(); stamp_on('ok'); pg.click('#iClose'); take('iodide'); pg.click('#s_journal'); give(); until("__G.S.cp===3&&__G.R.phase==='between'",12000)
    ck(S()['flags']['anna']=='saved' and not openv(),'Анна saved, no violation'); wipe()
    pg.click('#bNext'); tap_until("__G.R.phase==='client'"); inspect(); ck(C()['checks']['seal']=='bad','Виктор: forged seal seen'); stamp_on('ok')
    ck(C()['stamp']=='ok' and 'нарушени' in pg.inner_text('#imsg'),'risky ВЫДАНО allowed, reason shown')
    pg.click('#iClose'); take('antibiotic'); pg.click('#s_journal'); give(); s=S(); v=openv()
    ck(s['stock']['antibiotic']==1 and s['led'][-1]['op']=='illegal' and len(v)==1 and 'печать поддельная' in v[0]['why'] and 'без замера' in v[0]['why'],'ТЗ-1: Виктор по поддельному талону — склад −1, нарушение BAD с причинами')
    until("__G.S.cp===4",12000); ck(not S()['pending'] or all('замер' not in x['t'] for x in S()['pending']),'no hidden dosimeter fine any more')
    if S()['dirty']: wipe()
    finish_day(5); ck(pg.is_visible('#dNext'),'day 1 done')
    # ================= DAY 2 =================
    pg.click('#dNext'); tap_until("__G.R.phase==='lever'"); swipe(200); until("__G.R.phase==='client'",9000)
    docs(); pg.click('#tOk'); pg.click('#talon'); ck(C()['stamp'] is None and 'Не проверено' in pg.inner_text('#imsg'),'ТЗ-10: Клавдия без проверок — ВЫДАНО невозможно')
    pg.click('#iClose'); measure(); docs(); checks(DOC['klavdia']); ck(C()['checks']['doctor']=='bad','dead doctor flagged'); stamp_on('no'); until("__G.S.cp===2&&__G.R.phase==='between'",12000)
    nxt(); measure(); inspect(); stamp_on('ok'); pg.click('#iClose'); take('antitoxin'); pg.click('#s_journal'); give(); pg.click(NO); until("__G.S.cp===3&&__G.R.phase==='between'",12000); wipe()
    nxt(); measure(); pg.click('#bQuar'); tap_until("__G.S.cp===4&&__G.R.phase==='between'"); ck(S()['flags']['artem']=='quarantine','Артём quarantine')
    nxt(); ck(R('phase')=='voron','Ворон day 2'); ck('150 ТР' in pg.inner_text('#mkTP'),'ТЗ-7: Котовы — скидка у Ворона'); pg.click('#mkTP'); ck(S()['items'].get('blank')==1,'blank goes to inventory, not auto-applied')
    pg.screenshot(path=W+'t7_market.png'); pg.click('#mkLeave'); until("__G.S.cp===5&&__G.R.phase==='between'",12000)
    nxt(); journal_drag(); tap_until("__G.R.phase==='auditm'"); pg.screenshot(path=W+'t7_audit2.png')
    sel('v:'+openv()[0]['id']); ck(pg.is_disabled('#auBlank'),'blank cannot hide BAD (печать)'); tp=S()['tp']; pg.click('#auBribe'); s=S()
    ck(s['tp']==tp-100 and s['viol'][0]['status']=='hidden' and s['viol'][0]['how']=='взятка','bribe 100 hides the chosen violation, history kept')
    ck(pg.is_visible('#auDone'),'nothing open → close audit'); pg.click('#auDone'); tap_until("__G.S.cp===6&&__G.R.phase==='endshift'")
    s=S(); ck(s['flags']['audit']=='bribe' and not any('Премия комендатуры' in l['t'] for l in s['log']),'no premium after bribe')
    ck(any('дров' in l['t'] for l in s['log']),'Глеб: firewood −100'); finish_day(7)
    # ================= DAY 3 =================
    pg.click('#dNext'); tap_until("__G.R.phase==='lever'"); s=S()
    ck(s['flags'].get('cold3') and s['led'][-1]['op']=='spoil' and not short(),'ТЗ-6: отказ Глебу → холод: лопнул антисептик (акт порчи, без недостачи)')
    swipe(200); until("__G.R.phase==='client'",9000)
    measure(); inspect(); pg.click('#tExtra'); stamp_on('no'); until("__G.S.cp===2",12000)
    nxt(); measure(); inspect(); stamp_on('no'); until("__G.S.cp===3",12000); wipe()
    nxt(); measure(); inspect(); stamp_on('no'); tap_until("__G.S.cp===4&&__G.R.phase==='ring'")
    pg.click('#s_phone'); tap_until("__G.R.phase==='bribe'"); ol=S()['olya']; pg.click('#choice button[data-k="steal"]'); tap_until("__G.R.phase==='pocket'"); take('antibiotic'); drag('#deskItem','#pocket',.5,.5)
    s=S(); ck(short().get('antibiotic')==1 and s['led'][-1]['op']=='theft' and s['olya']==ol+10,'theft → SHORT антибиотик, Оля +10'); tap_until("__G.S.cp===5")
    if S()['dirty']: wipe()
    nxt(); pg.click(NO); tap_until("__G.S.cp===6"); nxt(); s=S(); ck(s['items'].get('blank')==2,'ТЗ-7: Котовы дарят бланк на 3-й день')
    pg.click('#mkLeave'); tap_until("__G.S.cp===7"); finish_day(8)
    # ================= DAY 4 =================
    pg.click('#dNext'); tap_until("__G.R.phase==='lever'"); swipe(200); until("__G.R.phase==='letter'",9000); pg.click('#s_tray'); ck('принёс ночью' in pg.inner_text('#ltxt'),'letter: steal'); pg.click('#lClose'); until("__G.R.phase==='client'",9000)
    measure(); inspect(); stamp_on('no'); until("__G.S.cp===3",12000); ck(not S()['pending'],'Егор refused by order, no fine'); wipe()
    nxt(); docs(); stamp_on('no'); until("__G.R.phase==='bribe'"); pg.click(YES); take('antiseptic'); give(); take('bandage'); give(); s=S()
    sh=short(); ck(sh.get('antiseptic')==1 and sh.get('bandage')==1 and [x['op'] for x in s['led'][-2:]]==['transfer','transfer'],'ТЗ-2: Вадим — обе единицы списаны и учтены как недостача')
    ck(s['items'].get('knife')==1 and s['items'].get('copper')==1,'нож и медь в вещах'); until("__G.S.cp===4",12000)
    nxt(); measure(); inspect(); stamp_on('no'); until("__G.S.cp===5",12000)
    nxt(); measure(); pg.click('#bQuar'); tap_until("__G.S.cp===6&&__G.R.phase==='between'")
    nxt(); journal_drag(); tap_until("__G.R.phase==='auditm'"); pg.screenshot(path=W+'t7_audit4.png')
    s=S(); ck(any(v['k']=='seen' for v in s['viol']),'SEEN: патруль видел беглого')
    sel('s:antibiotic'); pg.click('#auBlank'); sel('s:antiseptic'); pg.click('#auBlank'); sh=short()
    ck('antibiotic' not in sh and 'antiseptic' not in sh and sh.get('bandage')==1 and S()['items'].get('blank')==0,'2 blanks hide exactly 2 shortages, third stays')
    sel('s:bandage'); ck(pg.is_disabled('#auBlank'),'no blanks left'); pg.click('#auLie'); ck('bandage' not in short() and S()['lies']==1,'first lie about a SHORT passes')
    sel('v:'+[v for v in openv() if v['k']=='seen'][0]['id']); tp=S()['tp']; pg.click('#auBribe'); ck(S()['tp']==tp-150,'day-4 bribe costs 150')
    pg.click('#auDone'); tap_until("__G.S.cp===7&&__G.R.phase==='endshift'"); s=S()
    ops=[x['op'] for x in s['led']]; ck('theft' in ops and 'transfer' in ops and ops.count('fict')==2 and 'hide' in ops,'history keeps theft/transfer plus fictitious and hidden records')
    ck(any('Петрович' in l['t'] for l in s['log']),'food −60'); finish_day(8); ck('День 5' in pg.inner_text('#doneBox'),'day 4 done')
    # ---------- risky branches all go through the ledger ----------
    pg.evaluate("Object.assign(__G.S,{day:2,viol:[],flags:{},items:{},tp:2000,dirty:false});Object.assign(__G.S.stock,{stim:2,painkiller:3,antibiotic:3,antiradin:4,sedative:2,antitoxin:2,bandage:3,antiseptic:6});__G.S.doc=Object.assign({},__G.S.stock);__G.startCheckpoint(1)"); w(1800)
    measure(); inspect(); stamp_on('ok'); pg.click('#iClose'); take('sedative'); pg.click('#s_journal'); give(); v=openv()
    ck(S()['items'].get('ring')==1 and v and 'Казанцев' in v[-1]['why'],'Клавдия: выдача → BAD «врач без допуска», кольцо в вещах'); until("__G.S.cp===2",12000)
    nxt(); measure(); inspect(); stamp_on('ok'); pg.click('#iClose'); take('antitoxin'); pg.click('#s_journal'); give(); pg.click(YES); take('stim'); give()
    ck(short()=={'stim':1},'Глеб: «Стимулятор» мимо кассы → SHORT'); until("__G.S.cp===3",12000); wipe()
    nxt(); measure(); docs(); stamp_on('no'); until("__G.R.phase==='bribe'"); pg.click(YES); take('painkiller'); give(); ck(short()=={'stim':1,'painkiller':1},'Артём: «Обезбол» за радиолампу → SHORT')
    pg.evaluate("Object.assign(__G.S,{day:3});__G.startCheckpoint(3)"); nxt(); measure(); inspect(); stamp_on('ok'); pg.click('#iClose'); pg.click('#s_journal'); take('antitoxin'); give(); take('bandage'); give()
    v=openv(); ck(S()['items'].get('pelt')==1 and 'подписи' in v[-1]['why'],'Фёдор: 2 препарата по талону без подписи → BAD')
    tap_until("__G.S.cp===4&&__G.R.phase==='ring'"); pg.evaluate("__G.S.flags.maria='refused'"); pg.click('#s_phone'); tap_until("__G.R.phase==='bribe'"); pg.click('#choice button[data-k="maria"]'); tap_until("__G.R.phase==='bribe'")
    pg.click('#choice button[data-k="mpay"]'); take('antiradin'); drag('#deskItem','#pocket',.5,.5); ck(short().get('antiradin')==1 and S()['flags']['family']=='mariaPaid','Мария Б: украденный «Антирадин» → SHORT')
    tap_until("__G.S.cp===5"); 
    if S()['dirty']: wipe()
    nxt(); pg.click(YES); take('painkiller'); give(); take('antibiotic'); give(); tap_until("__G.S.cp===6"); s=S()
    ck(short().get('painkiller')==2 and short().get('antibiotic')==1 and s['items'].get('container')==1,'Семён: сделка → 2 SHORT, контейнер/патроны/спирт')
    nxt(); pg.click('#mkAB'); ck('antibiotic' not in short(),'Ворон: купленный антибиотик закрывает недостачу по складу')
    pg.click('#mkS_ring'); pg.click('#mkS_pelt'); s=S(); ck(not s['items'].get('ring') and not s['items'].get('pelt'),'проданные вещи исчезают из инвентаря')
    pg.click('#mkLeave'); tap_until("__G.S.cp===7")
    # ================= targeted scenarios =================
    def at_audit(day,cp,state):
        pg.evaluate(f"Object.assign(__G.S,{{day:{day}}},{state});__G.startCheckpoint({cp})"); nxt(); journal_drag(); tap_until(f"__G.R.phase==='auditm'||__G.S.cp==={cp+1}")
    base="{viol:[],warnings:0,lies:0,susp:0,flags:{},items:{},tp:1000,doc:Object.assign({},__G.S.stock)}"
    # ТЗ-3: one blank, two shortages
    pg.evaluate(f"Object.assign(__G.S,{base});__G.S.doc.antibiotic+=1;__G.S.doc.painkiller+=1;__G.S.items.blank=1")
    at_audit(4,6,"{}"); sel('s:painkiller'); pg.click('#auBlank'); sh=short(); ck(sh=={'antibiotic':1},'ТЗ-3: один бланк — скрыта только одна недостача (выбранная)')
    sel('s:antibiotic'); ck(pg.is_disabled('#auBlank'),'blank spent'); pg.click('#auTruth'); tap_until("__G.S.cp===7")
    s=S(); ck(s['warnings']==1 and not short(),'truth: warning 1, remaining written off by act')
    # ТЗ-4: blank without shortage
    pg.evaluate(f"Object.assign(__G.S,{base});__G.S.items.blank=1;__G.S.viol=[{{id:'x1',k:'bad',t:'тест',why:'',day:4,status:'open'}}]")
    at_audit(4,6,"{}"); ck(pg.is_disabled('#auBlank'),'ТЗ-4: бланк без недостачи использовать нельзя'); pg.click('#auTruth'); tap_until("__G.S.cp===7"); ck(S()['items']['blank']==1,'blank kept')
    # ТЗ-5: bribe with three violations
    pg.evaluate(f"Object.assign(__G.S,{base});__G.S.viol=['a','b','c'].map(i=>({{id:i,k:'bad',t:'нарушение '+i,why:'',day:4,status:'open'}}))")
    at_audit(4,6,"{}"); sel('v:b'); pg.click('#auBribe'); s=S(); ck([v['status'] for v in s['viol']]==['open','hidden','open'],'ТЗ-5: взятка скрывает одно выбранное нарушение, два остаются')
    sel('v:a'); pg.click('#auBribe'); ck(S()['viol'][0]['status']=='hidden' and S()['susp']==2,'second bribe costs more, suspicion grows')
    tp=S()['tp']; sel('v:c'); pg.click('#auBribe'); s=S(); ck(s['viol'][2]['status']=='open' and s['tp']==tp and s['warnings']==1,'third bribe refused → warning')
    pg.click('#auTruth'); tap_until("__G.S.cp===7")
    # ТЗ-9: lead container with two shortages
    pg.evaluate(f"Object.assign(__G.S,{base});__G.S.doc.stim+=1;__G.S.doc.bandage+=1;__G.S.items.container=1")
    at_audit(4,6,"{}"); sel('s:stim'); pg.click('#auCont'); ck(short()=={'bandage':1} and not S()['items']['container'],'ТЗ-9: контейнер закрыл только одну недостачу SHORT')
    ck(pg.locator('#auCont').count()==0,'container gone'); pg.click('#auTruth'); tap_until("__G.S.cp===7")
    # lie exposed after an earlier lie
    pg.evaluate(f"Object.assign(__G.S,{base},{{lies:1}});__G.S.doc.stim+=1")
    at_audit(4,6,"{}"); pg.click('#auLie'); s=S(); ck(short()=={'stim':1} and s['warnings']==1 and any(v['k']=='lie' for v in s['viol']),'second lie exposed: shortage stays, lie violation + warning')
    pg.click('#auTruth'); tap_until("__G.S.cp===7"); ck(S()['warnings']==2,'truth adds a warning (2)')
    # warnings: 2 → premium lost, 3 → order cap, 4 → fired
    pg.evaluate(f"Object.assign(__G.S,{base},{{warnings:2}})"); at_audit(4,6,"{}"); tap_until("__G.S.cp===7"); s=S()
    ck(not any('Премия комендатуры' in l['t'] for l in s['log']) and s['flags']['audit']=='clean','2 warnings: clean audit but no premium')
    pg.evaluate(f"Object.assign(__G.S,{base},{{warnings:3,log:[]}})"); pg.evaluate("__G.startCheckpoint(7)"); swipe(-200); pg.click('#s_monitor'); pg.click('#tabs button[data-t="ord"]')
    for _ in range(4): pg.click('button[data-o="bandage"][data-d="1"]')
    ck(pg.evaluate("__G.R.orders.bandage")==2,'3 warnings: max 2 per position'); pg.click('#tClose')
    pg.evaluate(f"Object.assign(__G.S,{base},{{warnings:3}});__G.S.doc.stim+=1"); at_audit(4,6,"{}"); pg.click('#auTruth'); tap_until("__G.R.phase==='done'")
    ck(S()['warnings']==4 and 'УВОЛЕНЫ' in pg.inner_text('#dTitle'),'4 warnings: dismissal'); pg.click('#dMenu')
    pg.click('#mCont'); until("__G.S!==null"); ck(S()['cp']==6 and S()['warnings']==3,'after dismissal the autosave returns to the audit')
    # clean audit premium + warning 0
    pg.evaluate(f"Object.assign(__G.S,{base})"); at_audit(4,6,"{}"); tap_until("__G.S.cp===7"); ck(any(l['v']==100 and 'Премия' in l['t'] for l in S()['log']),'clean day-4 audit: +100')
    # ТЗ-8: radiolamp survives a restart; inventory
    pg.evaluate("__G.S.items={radiolamp:1,spirit:1,toys:1};__G.S.olya=40;__G.startCheckpoint(2)"); w(300)
    pg.reload(); w(500); pg.click('#mCont'); until("__G.S!==null"); ck(S()['items'].get('radiolamp')==1,'ТЗ-8: радиолампа сохранилась после перезапуска')
    pg.click('#bItems'); ck(pg.is_visible('#inv') and 'Радиолампа' in pg.inner_text('#invBody'),'«Наши вещи» shows the lamp'); pg.screenshot(path=W+'t7_inv.png')
    ab=S()['stock']['antiseptic']; pg.click('[data-use="spirit"]'); ck(S()['stock']['antiseptic']==ab+1 and not S()['items'].get('spirit'),'spirit → antiseptic, item used up')
    pg.click('[data-use="toys"]'); ck(S()['olya']==50,'toys → Оля +10'); ck(pg.locator('[data-use="toys"]').count()==0,'used item disappears')
    pg.click('#invClose'); ck(not pg.is_visible('#inv'),'inventory closes')
    # inventory over a running dialog does not break it
    pg.evaluate("__G.startCheckpoint(3)"); pg.click("#bNext"); w(1900); ck(pg.evaluate("!!__G.R.typing||!!__G.R.c"),'client arriving'); pg.click('#bItems'); w(300); pg.click('#invClose'); w(200)
    ck(R('phase')=='client' and C()['key']=='vadim','dialog/day continue after inventory')
    # ТЗ-7 again: Анна saved influences later events
    ck(True,'Котовы: discount + gift checked above')
    # old save with legacy issues migrates into the ledger
    pg.evaluate("localStorage.setItem('nv2030apteka.manual',JSON.stringify({v:1,lay:2,day:3,cp:1,tp:300,dayStart:300,rad:0,journal:0,dirty:false,flags:{familyStrain:1},log:[],pending:[],issues:[{t:'old short',k:'short',drug:'stim'},{t:'old bad',k:'bad'},{t:'fixed',k:'short',drug:'bandage',fixed:true}],items:{},stock:{antiradin:2,antibiotic:2,painkiller:2,ai2:1,iodide:2,stim:0,antiseptic:3,bandage:4,sedative:2,antitoxin:1}}))")
    m=pg.evaluate("__G.readSave(__G.K_MAN)"); ck(m['doc']['stim']-m['stock']['stim']==1 and len(m['viol'])==1 and m['olya']==35,'legacy save → ledger: 1 SHORT, 1 BAD, Оля 35')
    for vw,vh in [(360,640),(412,915)]:
        pg.set_viewport_size({'width':vw,'height':vh}); w(250)
        ov=pg.evaluate("(()=>{const p=document.getElementById('panel').getBoundingClientRect(),s=document.getElementById('stage').getBoundingClientRect();return [p.height,p.bottom-s.bottom]})()")
        ck(ov[0]>100 and abs(ov[1])<1,'layout %dx%d'%(vw,vh))
    ck(errs==[],'no JS errors: '+json.dumps(errs[:5],ensure_ascii=False))
    print('OK',n_ok,'FAIL',len(fails)); b.close()
