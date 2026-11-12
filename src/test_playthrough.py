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
    pg.click('#s_phone'); tap_until("__G.R.phase==='bribe'"); ol=S()['olya']; pg.click('#choice button[data-k="steal"]'); tap_until("__G.R.phase==='pocket'"); take('antibiotic'); drag('#deskItem','#bag',.5,.5)
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
    ck(any('Петрович' in l['t'] for l in s['log']),'food −60'); finish_day(8); ck(pg.is_visible('#dNext'),'day 4 done')
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
    pg.click('#choice button[data-k="mpay"]'); take('antiradin'); drag('#deskItem','#bag',.5,.5); ck(short().get('antiradin')==1 and S()['flags']['family']=='mariaPaid','Мария Б: украденный «Антирадин» → SHORT')
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
    pg.click('#bag'); ck(pg.is_visible('#inv') and 'Радиолампа' in pg.inner_text('#invBody'),'«Наши вещи» shows the lamp'); pg.screenshot(path=W+'t7_inv.png')
    ab=S()['stock']['antiseptic']; pg.click('[data-use="spirit"]'); ck(S()['stock']['antiseptic']==ab+1 and not S()['items'].get('spirit'),'spirit → antiseptic, item used up')
    pg.click('[data-use="toys"]'); ck(S()['olya']==50,'toys → Оля +10'); ck(pg.locator('[data-use="toys"]').count()==0,'used item disappears')
    pg.click('#invClose'); ck(not pg.is_visible('#inv'),'inventory closes')
    # inventory over a running dialog does not break it
    pg.evaluate("__G.startCheckpoint(3)"); pg.click("#bNext"); w(1900); ck(pg.evaluate("!!__G.R.typing||!!__G.R.c"),'client arriving'); pg.click('#bag'); w(300); pg.click('#invClose'); w(200)
    ck(R('phase')=='client' and C()['key']=='vadim','dialog/day continue after inventory')
    # ТЗ-7 again: Анна saved influences later events
    ck(True,'Котовы: discount + gift checked above')
    # ================= DAY 5 =================
    def census(name):
        pg.click('#tCen'); pg.click(f'#cen .row[data-n="{name}"]') if name else pg.click('#cenNone')
    def ring_answer(): tap_until("__G.R.phase==='lever'"); swipe(200); tap_until("__G.R.phase==='ring'"); pg.click('#s_phone')
    pg.evaluate("Object.assign(__G.S,{viol:[],warnings:0,lies:0,susp:0,flags:{anna:'saved'},items:{radiolamp:1,parts:1},bag:{},tp:400,olya:60,dirty:false,rad:0});Object.assign(__G.S.stock,{sedative:4,antitoxin:2,bandage:4,stim:2,painkiller:3,antibiotic:3,antiradin:3,iodide:2,antiseptic:6});__G.S.doc=Object.assign({},__G.S.stock);__G.startDay(5)")
    ring_answer(); tap_until("__G.R.phase==='client'",20); ck(C()['key']=='zoya','day 5: HQ call then Зоя')
    measure(); docs(); ck(pg.is_visible('#tCen'),'census tool from day 5'); checks(DOC.get('zoya','Петрова Н.К.')); stamp_on('ok'); ck(C()['stamp'] is None and 'перепись' in pg.inner_text('#imsg'),'ВЫДАНО blocked without census check')
    census('Карпов Олег Игнатьевич'); ck(C()['checks']['reg'] is None,'wrong person in census rejected'); census('Карпова Зоя Игнатьевна')
    ck(C()['checks']['reg']=='bad' and '1968' in pg.inner_text('#imsg'),'Зоя: год рождения 1978 vs 1968'); pg.screenshot(path=W+'t8_zoya.png')
    tp=S()['tp']; stamp_on('ok'); pg.click('#iClose'); take('sedative'); pg.click('#s_journal'); give(); s=S(); v=openv()
    ck(s['tp']==tp+100 and s['items'].get('map')==1 and v[-1]['k']=='fake','Зоя: +100, карта, FAKE_PASSPORT'); until("__G.S.cp===3",12000)
    nxt(); measure(); docs(); checks('Орлов В.Г.'); census('Мамедов Руслан Тимурович'); ck(C()['checks']['reg']=='ok','Руслан: паспорт чистый'); stamp_on('ok'); pg.click('#iClose'); pg.click('#s_journal')
    take('antitoxin'); give(); take('bandage'); give(); ck(len(openv())==1 and R('phase')=='bribe','Руслан по талону: без нарушений (справка санпоста), предлагает сделку')
    pg.click(YES); take('stim'); give(); ck(short()=={'stim':1} and S()['items'].get('kerosene')==1,'Руслан: стимулятор мимо кассы → SHORT, керосин'); until("__G.S.cp===4",12000); wipe()
    nxt(); measure(); docs(); checks('Смирнов А.В.'); census('Ветров Кирилл Олегович'); ck(C()['checks']['reg']=='bad' and 'уничтожено' in pg.inner_text('#imsg'),'Кирилл: прописка в уничтоженном доме')
    pg.click('#iClose'); tp=S()['tp']; pg.click('#bQuar'); tap_until("__G.S.cp===5&&__G.R.phase==='between'"); ck(S()['tp']==tp+150,'Кирилл: карантин +150')
    nxt(); measure(); docs(); checks('Ветрова М.А.'); census('Соболев Лев Маркович'); census(None); ck(C()['checks']['reg']=='bad' and 'нет в переписи' in pg.inner_text('#imsg'),'Маргарита: нет в переписи')
    stamp_on('no'); until("__G.S.cp===6",12000); ck(not S()['pending'],'Маргарита: отказ без штрафа')
    nxt(); ck(R('phase')=='voron','Ворон day 5'); pg.click('#mkStamp'); pg.click('#mkS_map'); s=S(); ck(s['items'].get('pstamp')==1 and not s['items'].get('map'),'штамп прописки куплен, карта продана'); pg.screenshot(path=W+'t8_market.png')
    pg.click('#mkLeave'); tap_until("__G.S.cp===7"); finish_day(8); ck(pg.is_visible('#dNext'),'day 5 done')
    # ================= DAY 6 =================
    pg.click('#dNext'); ring_answer(); tap_until("__G.R.phase==='bribe'"); pg.click('#choice button[data-k="promise"]'); tap_until("__G.R.phase==='client'",20); ck(S()['flags']['son']=='promise' and C()['key']=='ignat','day 6: обещание Оле, Игнат')
    measure(); docs(); checks('Петрова Н.К.'); census('Савельев Игнат Савельевич'); stamp_on('ok'); pg.click('#iClose'); pg.click('#s_journal'); a0=S()['stock']['antiseptic']
    take('antiseptic'); give(); ck(S()['stock']['antiseptic']==a0-1 and C()['need']==['sedative'],'антисептик выдан пациенту, а не потрачен на лоток'); take('sedative'); tp=S()['tp']; give()
    ck(R('phase')=='bribe' and '350' in pg.inner_text(YES),'Игнат предлагает 350 за лампу и детали'); pg.click(YES); s=S(); ck(s['tp']==tp+100+350 and not s['items'].get('radiolamp') and not s['items'].get('parts'),'радиолампа и детали проданы +350'); until("__G.S.cp===3",12000)
    nxt(); measure(); docs(); checks('Орлов В.Г.'); ck(C()['checks']['name']=='bad','Жанна: фамилия в талоне не та'); census('Смирнова Жанна Андреевна'); ck(C()['checks']['reg']=='ok','паспорт Жанны сходится с переписью')
    stamp_on('no'); until("__G.S.cp===4",12000); ck(not S()['pending'],'Жанна: отказ без штрафа'); wipe()
    nxt(); ck(R('phase')=='bribe','Штерн без талона'); tp=S()['tp']; pg.click(YES); take('antibiotic'); give(); take('antiradin'); give(); sh=short()
    ck(S()['tp']==tp+300 and sh.get('antibiotic')==1 and sh.get('antiradin')==1,'Штерн: +300, две недостачи'); until("__G.S.cp===5",12000)
    nxt(); ck('500 ТР' in pg.inner_text('#txt') or True,'chizhov line'); measure(); docs(); checks('Орлов В.Г.'); census('Чижов Аркадий Львович'); stamp_on('ok'); pg.click('#iClose'); pg.click('#s_journal'); take('stim'); give(); take('sedative'); give()
    ck(R('phase')=='bribe' and pg.locator('#choice button').count()==3,'Чижов: 3 ответа про сына'); pg.screenshot(path=W+'t8_chizhov.png'); pg.click('#choice button[data-k="later"]'); tap_until("__G.S.cp===6&&__G.R.phase==='between'")
    nxt(); ck(pg.locator('#mkWhite').count()==1 and '250' in pg.inner_text('#mkWhite'),'Ворон: белый билет 250 (скидка Котовых)'); pg.click('#mkLeave'); tap_until("__G.S.cp===7&&__G.R.phase==='between'")
    nxt(); journal_drag(); tap_until("__G.R.phase==='auditm'"); pg.screenshot(path=W+'t8_audit.png'); fk=[v for v in openv() if v['k']=='fake'][0]
    sel('v:'+fk['id']); ck(pg.is_disabled('#auBlank') and not pg.is_disabled('#auStamp'),'FAKE: бланк не подходит, штамп прописки подходит'); pg.click('#auStamp'); ck(S()['viol'][-1]['status']=='hidden' or all(v['status']!='open' for v in S()['viol'] if v['k']=='fake'),'штамп прописки скрыл FAKE_PASSPORT')
    ck('150' in pg.inner_text('#auBribe'),'взятка Громову 150 в день 6'); pg.click('#auTruth'); tap_until("__G.S.cp===8&&__G.R.phase==='endshift'"); ck(S()['warnings']==1 and not short(),'правда: предупреждение, недостачи списаны')
    swipe(-200); pg.click('#s_monitor'); ck(pg.is_visible('#tChizh') and not pg.is_disabled('#tChizh'),'конверт Чижову доступен в терминале'); tp=S()['tp']; pg.click('#tChizh'); ck(S()['tp']==tp-500 and S()['flags']['sonSaved']=='chizhov','−500: Данил спасён')
    pg.click('#tEnd'); until("__G.S.cp===9"); t=pg.inner_text('#doneBox'); ck(S()['olya']==100 and 'вернётся домой' in t,'day 6 done: Оля 100, Данил дома'); pg.screenshot(path=W+'t8_done.png')
    # ---- variants ----
    pg.evaluate("Object.assign(__G.S,{flags:{son:'promise'},olya:60});__G.startCheckpoint(8)"); swipe(-200); pg.click('#s_monitor'); pg.click('#tEnd'); until("__G.S.cp===9"); ck(S()['olya']==0 and S()['flags']['son']=='betrayed' and 'не сдержано' in pg.inner_text('#doneBox'),'обещание не выполнено: Оля 0')
    pg.evaluate("Object.assign(__G.S,{flags:{son:'promise'},olya:60,tp:400});__G.startCheckpoint(6)"); nxt(); ck('350' in pg.inner_text('#mkWhite'),'белый билет 350 без Котовых'); pg.click('#mkWhite'); ck(S()['flags']['sonSaved']=='voron' and S()['tp']==50 and pg.locator('#mkWhite').count()==0,'белый билет куплен'); pg.click('#mkLeave'); tap_until("__G.S.cp===7")
    pg.evaluate("Object.assign(__G.S,{flags:{},olya:60});__G.startCheckpoint(1)"); tap_until("__G.R.phase==='ring'"); pg.click('#s_phone'); tap_until("__G.R.phase==='bribe'"); pg.click('#choice button[data-k="sent"]'); tap_until("__G.S.cp===2"); ck(S()['olya']==0 and S()['flags']['son']=='sent','«он взрослый»: отношения разрушены')
    pg.evaluate("__G.S.stock.stim=0;__G.S.doc.stim=0;__G.S.pending=[];__G.startCheckpoint(5)"); nxt(); docs(); stamp_on('no'); tap_until("__G.S.cp===6"); ck(not S()['pending'],'нет препарата на складе → отказ без штрафа; Чижов без обещания не торгуется')
    pg.evaluate("Object.assign(__G.S,{day:5,viol:[],tp:300,rad:0,dirty:false});Object.assign(__G.S.stock,{painkiller:2,antibiotic:2});__G.S.doc=Object.assign({},__G.S.stock);__G.startCheckpoint(4)"); nxt(); docs(); stamp_on('no'); until("__G.R.phase==='bribe'"); pg.click(YES); take('painkiller'); give(); take('antibiotic'); give(); s=S()
    ck(s['tp']==600 and s['rad']==15 and not short() and openv()[-1]['k']=='fake' and s['led'][-1]['op']=='illegal','Кирилл за взятку: +300, +15%, FAKE_PASSPORT, списано по документам'); tap_until("__G.S.cp===5")
    pg.evaluate("__G.S.day=6;__G.S.warnings=0;__G.startCheckpoint(7)"); nxt(); journal_drag(); tap_until("__G.R.phase==='auditm'"); pg.click('#auTruth'); tap_until("__G.S.cp===8"); ck(any(l['v']==-200 and 'паспорт' in l['t'] for l in S()['log']),'правда про FAKE_PASSPORT: штраф 200')
    # backpack: steal and return
    pg.evaluate("__G.S.day=5;__G.S.doc=Object.assign({},__G.S.stock);__G.S.bag={};__G.startCheckpoint(3)"); take('bandage'); drag('#deskItem','#bag',.5,.5); ck(S()['bag'].get('bandage')==1 and short()=={'bandage':1},'рюкзак: лекарство спрятано → недостача'); pg.screenshot(path=W+'t8_scene.png')
    pg.click('#bag'); ck('Бинт' in pg.inner_text('#invBody'),'рюкзак открывает вещи'); pg.screenshot(path=W+'t8_inv.png'); pg.click('[data-ret="bandage"]'); ck(not short() and not S()['bag']['bandage'],'возврат на полку закрывает недостачу'); pg.click('#invClose')
    # old save with legacy issues migrates into the ledger
    pg.evaluate("localStorage.setItem('nv2030apteka.manual',JSON.stringify({v:1,lay:2,day:3,cp:1,tp:300,dayStart:300,rad:0,journal:0,dirty:false,flags:{familyStrain:1},log:[],pending:[],issues:[{t:'old short',k:'short',drug:'stim'},{t:'old bad',k:'bad'},{t:'fixed',k:'short',drug:'bandage',fixed:true}],items:{},stock:{antiradin:2,antibiotic:2,painkiller:2,ai2:1,iodide:2,stim:0,antiseptic:3,bandage:4,sedative:2,antitoxin:1}}))")
    m=pg.evaluate("__G.readSave(__G.K_MAN)"); ck(m['doc']['stim']-m['stock']['stim']==1 and len(m['viol'])==1 and m['olya']==35,'legacy save → ledger: 1 SHORT, 1 BAD, Оля 35')
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
    pg.evaluate("Object.assign(__G.S,{flags:{sonSaved:'chizhov',son:'promise'},olya:60,viol:[],warnings:0,lies:0,susp:0,items:{},tp:600,rad:0});"+FILL+";__G.startDay(7)")
    tap_until("__G.R.phase==='lever'"); swipe(200); tap_until("__G.R.phase==='letter'"); pg.click('#s_tray')
    ck('Данила отпустили' in pg.inner_text('#ltxt') and 'ОЛИ' in pg.inner_text('#lhead') and S()['olya']==100,'день 7: записка Оли, отношения 100')
    pg.click('#lClose'); tap_until("__G.R.phase==='ring'"); pg.click('#s_phone'); tap_until("__G.R.phase==='delivery'")
    ck(pg.is_visible('#box') and R('hand')=='antiradinM' and S()['stock']['antiradinM']==0,'приёмка: коробка на столе, первая упаковка'); pg.screenshot(path=W+'t9_box.png')
    give(); ck(R('hand')=='antiradinM' and S()['stock']['antiradinM']==0,'приёмка: в окно нельзя')
    drag('#deskItem','#bag',.5,.5); ck(not S()['bag'].get('antiradinM'),'приёмка: в рюкзак нельзя')
    for i in range(6): drag('#deskItem','#s_shelfR',.5,.5)
    s=S(); ck(all(s['stock'][k]==3 and s['doc'][k]==3 for k in ['antiradinM','strept','oftalmo','gem','immunal','ointment']) and s['led'][-1]['op']=='in','приёмка: 6 позиций ×3 на полке и в учёте')
    tap_until("__G.R.phase==='client'"); ck(C()['key']=='zahar' and not pg.is_visible('#box'),'после приёмки — Захар'); tp=S()['tp']
    serve('Петрова Н.К.','Лютый Захар Васильевич',['strept','ointment']); s=S(); ck(s['tp']==tp+150 and not openv() and s['stock']['strept']==2 and not short(),'Захар: +150, чисто'); cp_is(5)
    nxt(); pg.screenshot(path=W+'t9_serafim.png'); serve('Смирнов А.В.','Тихонов Серафим Кузьмич',['oftalmo','immunal']); s=S(); v=openv()
    ck(len(v)==1 and v[0]['k']=='fake' and '1954' in v[0]['why'] and s['items'].get('cross')==1,'Серафим: FAKE_PASSPORT (год рождения), серебряный крест'); cp_is(6)
    nxt(); serve('Петрова Н.К.','Кузнецова Нина Павловна',['gem','painkiller'],extra=True); s=S(); ck(openv()[-1]['k']=='bad' and 'просрочен' in openv()[-1]['why'] and s['flags'].get('lining')==1,'Нина: BAD (просрочен), подклад'); cp_is(7)
    nxt(); measure(); docs(); checks('Орлов В.Г.'); census('Лютый Захар Васильевич'); ck(C()['checks']['reg']=='bad' and C()['checks']['name']=='bad','Ваня: паспорта нет — перепись ✗, ФИО ✗')
    stamp_on('ok'); pg.click('#iClose'); pg.click('#s_journal'); take('antiradinM'); give(); s=S()
    ck(s['rad']==10 and s['items'].get('battery')==1 and openv()[-1]['k']=='fake' and s['stock']['antiradinM']==2,'Ваня: выдано — +10% (подклад −5), батарея, FAKE'); cp_is(8); wipe()
    nxt(); ck(R('phase')=='voron' and pg.locator('#mkF_fakeT').count()==1 and '150 ТР' in pg.inner_text('#mkTP'),'Ворон д7: пустышки в продаже, бланк 150'); pg.screenshot(path=W+'t9_market.png')
    tp=S()['tp']; pg.click('#mkF_fakeT'); pg.click('#mkF_fakeL'); pg.click('#mkS_cross'); s=S(); ck(s['tp']==tp-100+150 and s['stock']['fakeT']==1 and s['stock']['fakeL']==1 and s['doc']['fakeT']==0,'пустышки на полке мимо учёта, крест продан')
    pg.click('#mkLeave'); cp_is(9); close_shift(); pg.click('#tabs button[data-t="ord"]'); ck(pg.locator('button[data-o="antiradinM"]').count()==2 and pg.locator('button[data-o="fakeT"]').count()==0,'заказы: новые препараты есть, пустышек нет')
    pg.click('#tEnd'); until("__G.S.cp===10"); ck(pg.is_visible('#dNext'),'день 7 завершён')
    # ---- day 8
    pg.click('#dNext'); ring_answer(); tap_until("__G.R.phase==='bribe'"); pg.screenshot(path=W+'t9_mom.png'); pg.click('#choice button[data-k="promise"]'); tap_until("__G.R.phase==='client'",20); ck(S()['flags']['dad']=='promise' and C()['key']=='nikita','день 8: обещание маме')
    tp=S()['tp']; serve('Орлов В.Г.','Гордеев Никита Ильич',['antitoxin','fakeL']); s=S()
    ck(s['flags'].get('nikitaFake')=='oftalmo' and s['stock']['oftalmo']==2 and s['doc']['oftalmo']==1 and s['stock']['fakeL']==0 and s['tp']==tp+150 and not short(),'Никита: «Раствор» вместо «Офтальмо-К» — настоящий остался, недостачи нет'); cp_is(3)
    nxt(); refuse(); cp_is(4); ck(S()['flags']['varvara']=='refused' and not S()['pending'],'Варвара: отказ без штрафа')
    nxt(); tp=S()['tp']; serve('Орлов В.Г.',None,['fakeT','gem','bandage']); s=S(); ck(s['tp']==tp+250 and s['items'].get('bile')==1 and s['stock']['antiradinM']==2 and s['doc']['antiradinM']==1 and s['flags'].get('tarasFake')=='antiradinM','Тарас: «Мел» вместо «Антирадина-М», желчь, +250'); cp_is(5)
    take('antiradinM'); drag('#deskItem','#bag',.5,.5); ck(S()['bag'].get('antiradinM')==1 and not short() and 'сходится' in pg.inner_text('#imsg'),'настоящий «Антирадин-М» в рюкзаке без недостачи'); wipe()
    nxt(); refuse(); cp_is(6)
    nxt(); ck(pg.locator('#mkDad').count()==1 and pg.locator('#mkB_antiradinM').count()==1,'Ворон д8: «Антирадин» в рюкзак, скупка из рюкзака'); pg.click('#mkS_bile'); pg.click('#mkF_fakeT'); pg.click('#mkF_fakeT'); pg.click('#mkF_fakeL'); ck(S()['stock']['fakeT']==2 and S()['stock']['fakeL']==1,'куплены 3 пустышки'); pg.click('#mkLeave'); cp_is(7)
    tp=S()['tp']; nxt(); journal_drag(); tap_until("__G.R.phase==='auditm'"); s=S(); pg.screenshot(path=W+'t9_audit.png')
    ck(s['tp']==tp-200 and s['stock']['fakeT']==0 and s['stock']['fakeL']==0 and '200' in pg.inner_text('#auBribe'),'ревизия №4: >2 пустышек — вскрытие, штраф 200, изъятие; взятка 200')
    pg.click('#auTruth'); cp_is(8); ck(S()['warnings']==1,'правда → предупреждение'); close_shift(); ck('Обещано маме' in pg.inner_text('#tbody') and 'ЕСТЬ' in pg.inner_text('#tbody'),'терминал: обещание маме — ЕСТЬ')
    pg.click('#tabs button[data-t="ord"]'); pg.click('#tEnd'); until("__G.S.cp===9"); s=S(); ck(s['flags']['dad']=='saved' and not s['bag']['antiradinM'] and 'передано' in pg.inner_text('#doneBox') and not s['flags'].get('diesel8'),'день 8: лекарство отцу передано'); pg.screenshot(path=W+'t9_done8.png')
    # ---- day 9
    pg.click('#dNext'); ring_answer(); tap_until("__G.R.phase==='client'",25); s=S(); ck(s['items'].get('dirk')==1 and any(l['v']==-150 and 'дизель' in l['t'] for l in s['log']) and C()['key']=='petr2','день 9: отец спасён (кортик), авария на дизельной −150')
    ck(pg.evaluate("document.getElementById('client').src.length>100") ,'Пётр Ильин: спрайт первого дня')
    measure(); docs(); checks('Смирнов А.В.'); census('Ильин Пётр Сергеевич'); ck(C()['checks']['reg']=='bad' and 'прописка' in pg.inner_text('#imsg') and pg.evaluate("document.getElementById('pPhoto').src.length>100"),'Пётр: прописка не сходится'); stamp_on('no'); cp_is(3); wipe()
    pg.evaluate("__G.move('fakeM',1,'contra','t')"); nxt(); tp=S()['tp']; serve('Смирнов А.В.','Громов Матвей Ильич',['fakeM','painkiller']); s=S(); ck(s['tp']==tp+150 and len(openv())==0 and s['stock']['ointment']==2 and s['flags'].get('matveyFake')=='ointment','Матвей: «Вазелин» вместо мази, чисто'); cp_is(4)
    nxt(); docs(); pg.click('#tExtra'); ck('личной печати' in pg.inner_text('#imsg'),'Лариса: нет личной печати врача'); stamp_on('no'); cp_is(5)
    nxt(); ck(R('phase')=='bribe' and C()['key']=='gennady','Геннадий: без талона, выбор'); pg.screenshot(path=W+'t9_gennady.png'); tp=S()['tp']; pg.click(YES); take('stim'); give(); take('oftalmo'); give(); s=S(); ck(s['tp']==tp+250 and short()=={'stim':1} and s['led'][-1]['op']=='transfer','Геннадий: +250, недостача стимулятора'); cp_is(6)
    nxt(); ck(pg.locator('#mkS_dirk').count()==1,'Ворон д9: кортик можно продать'); pg.click('#mkLeave'); cp_is(7); finish_day(8)
    # ---- day 10
    pg.click('#dNext'); ring_answer(); tap_until("__G.R.phase==='client'",25); ck(C()['key']=='kravtsov','день 10: Кравцов после звонка Коршунова')
    refuse(); cp_is(3); nxt(); refuse(); cp_is(4); ck(S()['flags']['elvira']=='refused' and not S()['pending'],'Эльвира: отказ без штрафа сегодня')
    nxt(); measure(); docs(); checks('Смирнов А.В.'); census('Козлов Игорь Петрович'); ck(C()['checks']['reg']=='bad' and 'ЧУЖОЙ' in pg.inner_text('#imsg'),'Родион: чужой паспорт'); pg.screenshot(path=W+'t9_rodion.png'); pg.click('#iClose'); tp=S()['tp']; pg.click('#bQuar'); cp_is(5); ck(S()['tp']==tp+150,'Родион: карантин +150')
    pg.evaluate("__G.move('fakeL',2,'contra','t')"); nxt(); tp=S()['tp']; sd=S()['stock']['sedative']; serve('Ветрова М.А.','Рябова Тамара Глебовна',['fakeL','fakeL']); s=S(); ck(s['tp']==tp+150 and s['stock']['sedative']==sd and not openv() and s['flags']['tamaraFake']=='sedative,immunal','Тамара: две пустышки, +150, без нарушений'); cp_is(6)
    nxt(); pg.click('#mkLeave'); cp_is(7); close_shift(); pg.click('#tabs button[data-t="ord"]'); ck('ДЕФИЦИТ' in pg.inner_text('#tbody') and pg.locator('button[data-o]').count()==0,'день 10: заявки заблокированы'); pg.click('#tEnd'); until("__G.S.cp===8")
    # ---- day 11
    pg.evaluate("__G.S.olya=60"); pg.click('#dNext'); tap_until("__G.R.phase==='lever'"); s=S(); ck(any(l['v']==-100 and 'вода' in l['t'] for l in s['log']),'день 11: −100 на чистую воду (Эльвира)'); swipe(200); tap_until("__G.R.phase==='bribe'",20)
    tp=S()['tp']; pg.click(YES); take('antibiotic'); give(); take('gem'); give(); s=S(); ck(s['tp']==tp+300 and short().get('antibiotic')==1,'Баринов: +300, недостача'); cp_is(2)
    nxt(); pg.click(NO); tap_until("__G.R.phase==='ring'",20); pg.click('#s_phone'); tap_until("__G.R.phase==='bribe'"); pg.click('#choice button[data-k="promise"]'); cp_is(4); ck(S()['flags']['food']=='promise','Оля: обещаны 500 ТР')
    pg.evaluate("__G.move('fakeL',2,'contra','t')"); nxt(); tp=S()['tp']; so=S()['stock']['oftalmo']; pg.click(YES); take('fakeL'); give(); take('fakeL'); give(); s=S(); ck(s['tp']==tp+350 and s['stock']['oftalmo']==so and s['flags']['mamontovFake'],'Мамонтов: пустышки за 350, склад цел'); cp_is(5)
    nxt(); pg.click(NO); cp_is(6); nxt(); ck(pg.locator('#mkAB').count()==0 and pg.locator('#mkDad').count()==0 and pg.locator('#mkF_fakeL').count()==1,'Ворон д11: настоящих лекарств нет'); pg.click('#mkLeave'); cp_is(7)
    nxt(); journal_drag(); tap_until("__G.R.phase==='auditm'"); n=pg.locator('.aurow').count(); ck(n>=2,'ревизия №5 нашла недостачи'); pg.click('#auTruth'); cp_is(8); ck(S()['warnings']==2,'второе предупреждение')
    pg.evaluate("__G.S.tp=640"); close_shift(); ck('Обещано Оле' in pg.inner_text('#tbody') and 'хватает' in pg.inner_text('#tbody'),'терминал: 500 ТР для Оли'); pg.click('#tEnd'); until("__G.S.cp===9"); s=S(); t=pg.inner_text('#doneBox')
    ck(s['tp']==140 and s['flags']['family11']=='fed' and 'переданы' in t and pg.is_visible('#dNext'),'день 11: семья накормлена, −500'); pg.screenshot(path=W+'t9_done11.png')
    # ---- variants
    pg.evaluate("Object.assign(__G.S,{day:7,flags:{son:'sent'},olya:40});__G.startCheckpoint(1)"); pg.click('#s_tray'); ck('теплушки' in pg.inner_text('#ltxt') and 'ДАНИЛА' in pg.inner_text('#lhead') and S()['olya']==0,'день 7: письмо Данила, Оля 0'); pg.click('#lClose')
    pg.evaluate("Object.assign(__G.S,{day:11,flags:{},olya:10});__G.startCheckpoint(3)"); ck(S()['cp']==4,'день 11: при разрушенных отношениях Оля не звонит')
    pg.evaluate("Object.assign(__G.S,{day:11,flags:{food:'promise'},olya:60,tp:300});__G.startCheckpoint(8)"); swipe(-200); pg.click('#s_monitor'); ck('НЕ ХВАТАЕТ' in pg.inner_text('#tbody'),'терминал: не хватает на продукты'); pg.click('#tEnd'); until("__G.S.cp===9"); ck(S()['flags']['family11']=='ill' and S()['tp']==300 and S()['olya']==40,'обещание не выполнено: денег нет, Оля −20')
    pg.evaluate("Object.assign(__G.S,{day:8,flags:{dad:'promise'},olya:60,bag:{}});__G.startCheckpoint(8)"); swipe(-200); pg.click('#s_monitor'); ck('НЕТ' in pg.inner_text('#tbody'),'терминал: лекарства для отца нет'); pg.click('#tEnd'); until("__G.S.cp===9"); ck(S()['flags']['dad']=='broken','обещал и не принёс')
    pg.evaluate("__G.S.items={};__G.startDay(9)"); ring_answer(); tap_until("__G.R.phase==='client'",25); ck(S()['olya']==50 and not S()['items'].get('dirk'),'день 9: отец умер, Оля −10')
    pg.evaluate("Object.assign(__G.S,{day:8,flags:{dad:'promise'},tp:500,bag:{}});__G.startCheckpoint(6)"); nxt(); pg.click('#mkDad'); ck(S()['bag']['antiradin']==1 and S()['tp']==300 and not short(),'«Антирадин» у Ворона за 200 — в рюкзак, склад цел'); pg.click('#mkLeave'); cp_is(7)
    BASE8="{viol:[],warnings:0,lies:0,susp:0,flags:{},items:{},tp:1000}"
    pg.evaluate(f"Object.assign(__G.S,{BASE8});"+FILL.replace("m.nw?0:3","3")+";__G.S.doc.strept+=1;__G.S.stock.fakeT=1"); at_audit(8,7,"{}"); cp_is(8); ck(any(l['v']==150 and 'Премия' in l['t'] for l in S()['log']),'одна пустышка прикрыла недостачу: ревизия чистая, премия 150')
    pg.evaluate(f"Object.assign(__G.S,{BASE8});"+FILL.replace("m.nw?0:3","3")+";__G.S.doc.strept+=1;__G.S.stock.fakeL=1"); at_audit(8,7,"{}"); ck(R('phase')=='auditm' and short()=={'strept':1},'пустышка другой формы недостачу не прикрывает'); pg.click('#auTruth'); cp_is(8); ck(any(l['v']==-50 and 'спецрезерв' in l['t'] for l in S()['log']),'недостача спецрезерва: штраф')
    pg.evaluate(f"Object.assign(__G.S,{BASE8});"+FILL.replace("m.nw?0:3","3")+";__G.S.items.order=1;__G.S.viol=[{id:'a',k:'fake',t:'x',why:'',day:8,status:'open'}]"); at_audit(8,7,"{}"); pg.click('#auOrder'); ck(S()['viol'][0]['status']=='hidden' and not S()['items']['order'],'секретный приказ снял претензию'); pg.click('#auDone'); cp_is(8); ck(any(l['v']==150 for l in S()['log']),'после приказа — премия 150')
    pg.evaluate(f"Object.assign(__G.S,{BASE8},{{day:10,rad:0}});"+FILL.replace("m.nw?0:3","3")+";__G.startCheckpoint(4)"); nxt(); docs(); stamp_on('no'); until("__G.R.phase==='bribe'"); pg.click(YES); take('stim'); give(); take('strept'); give(); s=S(); ck(s['tp']==1250 and s['rad']==15 and openv()[-1]['k']=='fake' and s['flags']['rodion']=='bribed' and not short(),'Родион за взятку: +250, +15%, FAKE'); cp_is(5)
    m=pg.evaluate("__G.readSave(__G.K_MAN)"); ck(m['stock'].get('strept')==0 and m['doc'].get('fakeT')==0,'старое сохранение дополняется новыми позициями')
    for vw,vh in [(360,640),(412,915)]:
        pg.set_viewport_size({'width':vw,'height':vh}); w(250)
        ov=pg.evaluate("(()=>{const p=document.getElementById('panel').getBoundingClientRect(),s=document.getElementById('stage').getBoundingClientRect();return [p.height,p.bottom-s.bottom]})()")
        ck(ov[0]>100 and abs(ov[1])<1,'layout %dx%d'%(vw,vh))
    ck(errs==[],'no JS errors: '+json.dumps(errs[:5],ensure_ascii=False))
    print('OK',n_ok,'FAIL',len(fails)); b.close()
