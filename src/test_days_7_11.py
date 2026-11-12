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
