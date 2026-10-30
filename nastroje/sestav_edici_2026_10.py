# -*- coding: utf-8 -*-
"""Složí edici 2026-10 do data/history.json a zmrazí dubnovou do data/editions/2026-04.json.
Vstupy: zdroje/2026-10 (raw.json, brand.json, organic.json, gsc_mm.json, gt_norm.json, april_findings.json)."""
import json,os,collections
Z='zdroje/2026-10/'
J=lambda f:json.load(open(f,encoding='utf-8'))
old=J('data/history.json') if not os.path.exists('data/editions/2026-04.json') else J('data/editions/2026-04.json')
b=J(Z+'brand.json'); ms=b['months']; bs=b['brandSearch']; kw=b['kw']
org=J(Z+'organic.json'); gm=J(Z+'gsc_mm.json'); gt=J(Z+'gt_norm.json'); af=J(Z+'april_findings.json')
raw=J(Z+'raw.json')
i=lambda m:ms.index(m)
L=slice(i('2025-10'),i('2026-09')+1); P=slice(i('2024-10'),i('2025-09')+1)
sm=lambda k,s:sum(bs[k][s])
ids=list(bs); TL=sum(sm(k,L) for k in ids); TP=sum(sm(k,P) for k in ids)
sos=lambda k,s,T:100*sm(k,s)/T
yoy=lambda k:100*(sm(k,L)-sm(k,P))/sm(k,P)
n1=lambda x:f"{x:.1f}".replace('.',',')
n2=lambda x:f"{x:.2f}".replace('.',',')
n0=lambda x:f"{round(x):,}".replace(',',' ')
sg=lambda x:('+' if x>=0 else '−')+n1(abs(x))
sg0=lambda x:('+' if x>=0 else '−')+str(abs(round(x)))
NARROW=['erikafashion','lelosi','glami','orsay','buga','evona','miadresses','blankastraka','londonclub','coolboutique','bestmoda','sqvele']
NL=sum(sm(k,L) for k in NARROW); NP=sum(sm(k,P) for k in NARROW)
ORG_CZ=['erikafashion','glami','aboutyou','bonprix','orsay','londonclub','miadresses','zalando','modivo','lelosi','sqvele']
DOM={'erikafashion':'erikafashion.cz','glami':'glami.cz','aboutyou':'aboutyou.cz','bonprix':'bonprix.cz','orsay':'orsay.cz','londonclub':'londonclub.cz','miadresses':'miadresses.cz','zalando':'zalando.cz','modivo':'modivo.cz','lelosi':'lelosi.cz','sqvele':'sqvele.com'}
organic={k:[org[DOM[k]+'|None'][m] for m in ms] for k in ORG_CZ}
INTL={'sinsay':'sinsay.com','shein':'shein.com','reserved':'reserved.com','mohito':'mohito.com'}
organicIntl={k:[org[d+'|CZ'].get(m) for m in ms] for k,d in INTL.items()}
# GSC: Ahrefs do 2025-06, Marketing Miner od 2025-07 (do června se shodují na klik)
ah=[r for r in raw if r['tool']=='gsc-performance-history' and 'HTTP 400' not in r['text'][:60]][0]
ahd=json.JSONDecoder().raw_decode(ah['text'].lstrip())[0]['metrics']
g=collections.OrderedDict()
for r in ahd:
    k=r['date'][:7]
    if k<='2025-06': g[k]=(r['clicks'],r['impressions'],round(r['ctr'],2),round(r['position'],2))
for k in gm['months']:
    if '2025-07'<=k<='2026-09':
        c,im,p=gm['all'][k][:3]; g[k]=(c,im,round(100*c/im,2),round(p/im,2))
gdates=list(g); gsc={'dates':gdates,'clicks':[g[k][0] for k in gdates],'impressions':[g[k][1] for k in gdates],'ctr':[g[k][2] for k in gdates],'position':[g[k][3] for k in gdates]}
gc=lambda a,c:sum(g[k][0] for k in gdates if a<=k<=c)
G12,G12p=gc('2025-10','2026-09'),gc('2024-10','2025-09')
Q=['2026-07','2026-08','2026-09'];Qp=['2025-07','2025-08','2025-09']
qb=sum(gm['brand'][k][0] for k in Q);qbp=sum(gm['brand'][k][0] for k in Qp)
qa=sum(gm['all'][k][0] for k in Q);qap=sum(gm['all'][k][0] for k in Qp)
# Trends
gd=gt['dates'];GB=gt['brands']
gw=lambda k,a,c:(lambda xs:sum(xs)/len(xs))([v for d,v in zip(gd,GB[k]) if a<=d<=c])
g1=lambda k:gw(k,'2025-10-01','2026-09-30');g0=lambda k:gw(k,'2024-10-01','2025-09-30')
gyoy=lambda k:100*(g1(k)-g0(k))/g0(k)
gsl=sum(g1(k) for k in GB);gsp=sum(g0(k) for k in GB)
gq=lambda k:100*(gw(k,'2026-07-01','2026-09-30')-gw(k,'2025-07-01','2025-09-30'))/gw(k,'2025-07-01','2025-09-30')
# snapshot
sn=[r for r in raw if r['tool']=='batch-analysis'][0]
snd=json.JSONDecoder().raw_decode(sn['text'].lstrip())[0]['targets']
d2id={}
for x in old['brands']: d2id[x['domain']]=x['id']
d2id['modivo.cz']='modivo';d2id['sqvele.com']='sqvele'
snapshot={d2id[t['url'].rstrip('/')]:{'orgTraffic':t['org_traffic'],'orgKeywords':t['org_keywords'],'orgKeywords1_3':t['org_keywords_1_3'],'dr':t['domain_rating'],'refdomains':t['refdomains']} for t in snd}
# asociace z matching terms
assoc={}
HEAD={'sinsay':['sinsay'],'shein':['shein','shein cz'],'aboutyou':['about you','aboutyou','about you cz'],'bonprix':['bonprix'],'zalando':['zalando'],'mohito':['mohito'],'lelosi':['lelosi'],'reserved':['reserved'],'glami':['glami'],'orsay':['orsay'],'modivo':['modivo'],'sqvele':['sqvele'],'miadresses':['mia dresses','miadresses'],'erikafashion':['erikafashion','erika fashion']}
MT={'sinsay':'sinsay','shein':'shein','about you,aboutyou':'aboutyou','bonprix':'bonprix','zalando':'zalando','mohito':'mohito','lelosi':'lelosi','reserved':'reserved','glami':'glami','orsay':'orsay','modivo':'modivo','sqvele':'sqvele','miadresses,mia dresses':'miadresses','erikafashion,erika fashion':'erikafashion'}
terms=[]
for r in raw:
    if r['tool']=='keywords-explorer-matching-terms':
        k=r['input']['keywords']
        if k not in MT: continue
        rows=json.JSONDecoder().raw_decode(r['text'].lstrip())[0]['keywords']
        if MT[k]=='erikafashion': terms=rows
        assoc[MT[k]]=[{'kw':x['keyword'],'vol':x['volume']} for x in rows if x['keyword'] not in HEAD[MT[k]] and x['volume']>0][:8]
# varianty s průměrem 12 měsíců
vs=lambda kwn:round(sum(kw[kwn].get(m,0) for m in ms[L])/12)
variants={}
src=dict(old['brandVariants']);src['modivo']=[{'kw':k} for k in('modivo','modivo.cz','modivo cz')];src['sqvele']=[{'kw':'sqvele'}]
for k,v in src.items():
    fix=[x['kw'].replace('�aty','šaty').replace('�esko','česko') for x in v]
    variants[k]=sorted([{'kw':n,'vol':vs(n)} for n in fix],key=lambda x:-x['vol'])
brands=[dict(x) for x in old['brands']]
brands.append({'id':'modivo','label':'Modivo','domain':'modivo.cz','color':'#3F51B5','tier':2,'isTarget':False})
brands.append({'id':'sqvele','label':'Sqvele','domain':'sqvele.com','color':'#AD1457','tier':3,'isTarget':False})
moves=[{'id':k,'now':round(sos(k,L,TL),2),'prev':round(sos(k,P,TP),2),'yoy':round(yoy(k),1),'gtYoy':round(gyoy(k),1) if k in GB else None,'avg':round(sm(k,L)/12)} for k in ids]
moves.sort(key=lambda x:-x['now'])
# tři zdroje, index průměr 7 až 9/2025 = 100
tm=[m for m in gm['months'] if '2025-07'<=m<='2026-09']
def monthly_gt(m):
    xs=[v for d,v in zip(gd,GB['erikafashion']) if d[:7]==m]; return sum(xs)/len(xs)
base=lambda f:sum(f(m) for m in Qp)/3
A=lambda m:bs['erikafashion'][i(m)];C=lambda m:gm['brand'][m][0];T=monthly_gt
tri={'months':tm,'ahrefs':[round(100*A(m)/base(A),1) for m in tm],'gsc':[round(100*C(m)/base(C),1) for m in tm],'trends':[round(100*T(m)/base(T),1) for m in tm]}
# podíl Eriky po kalendářních měsících, poslední dva roky
sh=collections.defaultdict(list)
for k,m in enumerate(ms):
    if m>='2024-10':
        t=sum(bs[x][k] for x in ids); sh[m[5:]].append(100*bs['erikafashion'][k]/t)
season=[round(sum(sh[f"{x:02d}"])/len(sh[f"{x:02d}"]),2) for x in range(1,13)]
ret_a,ret_b=2834,1402; rec_a,rec_b=621,217; eli_a,eli_b=1074,49; mus_a,mus_b=1562,142
OTL=sum(sum(organic[k][L]) for k in ORG_CZ);OTP=sum(sum(organic[k][P]) for k in ORG_CZ)
osh=lambda k,s,T:100*sum(organic[k][s])/T
ae=lambda m:organic['erikafashion'][i(m)]
oq=sum(organic['erikafashion'][i(m)] for m in Q);oqp=sum(organic['erikafashion'][i(m)] for m in Qp)
okq=sum(sum(organic[k][i(m)] for m in Q) for k in ORG_CZ);okqp=sum(sum(organic[k][i(m)] for m in Qp) for k in ORG_CZ)
shs=lambda k:n1(sos(k,L,TL))
print('kontrola',dict(TL=TL,TP=TP,G12=G12,G12p=G12p,qb=qb,qbp=qbp,qa=qa,qap=qap,oq=oq,oqp=oqp,okq=okq,okqp=okqp,season=season))
print('organik podil',{k:(round(osh(k,L,OTL),1),round(osh(k,P,OTP),1)) for k in ORG_CZ})
print('tri',tri)
exsh=lambda l,p:100*(l-p)/p
noShein=(TL-sm('shein',L),TP-sm('shein',P))
gainers=sum(sm(k,L)-sm(k,P) for k in('sinsay','aboutyou','reserved','modivo'))
S=lambda t,li:{'title':t,'li':li}
sections=[
 {'id':'chart1','type':'line','data':'brandShare','title':'Share of Search, brandové hledání v ČR',
  'methodology':True,'explanation':'Podíl každé značky na hledání všech sledovaných značek v jednotlivých měsících. Sezónní výkyvy tu jsou vidět, trend lépe ukazuje graf klouzavého roku níže.',
  'note':'Čísla jsou přepočítaná z jednoho stažení 30. 10. 2026, Ahrefs zpětně upravuje i starší měsíce. Proto se liší od archivu z dubna. Nově přibyly značky Modivo a Sqvele, data končí zářím 2026.',
  'findings':S('Klíčová zjištění',[
   f"Shein ztratil {n1(sos('shein',P,TP)-sos('shein',L,TL))} procentního bodu, z {n1(sos('shein',P,TP))} % na {n1(sos('shein',L,TL))} %. Hledání kleslo o {abs(round(yoy('shein')))} %, Google Trends ukazuje skoro totéž ({sg0(gyoy('shein'))} %). Pád zrychlil v červenci 2026, kdy v EU začalo platit clo 3 EUR na levné zásilky.",
   f"Novou jedničkou je Sinsay s {shs('sinsay')} %, těsně za ním About You s {shs('aboutyou')} %. Reserved si polepšil na {shs('reserved')} %.",
   f"Erika Fashion má podle Ahrefs {n2(sos('erikafashion',L,TL))} % proti {n2(sos('erikafashion',P,TP))} % o rok dřív. Search Console a Google Trends ale ukazují růst, proč se zdroje rozcházejí, je v záložce Shrnutí a doporučení.",
   f"Modivo roste nejrychleji ({sg0(yoy('modivo'))} %) a v absolutním hledání předběhlo Lelosi i Eriku.",
   f"Celá kategorie klesla o {n1(abs(exsh(TL,TP)))} %, bez Sheinu ale vyrostla o {n1(exsh(*noShein))} %. Trh se nezmenšuje, přelévá se.",
   f"Glami ztratilo {abs(round(yoy('glami')))} % hledání a podobně i na Trends ({sg0(gyoy('glami'))} %). Lidé ho stále méně hledají jménem."])},
 {'id':'chartRolling','type':'line','data':'rolling','title':'Klouzavý rok, podíl bez sezónnosti',
  'explanation':'Každý bod je podíl značky za posledních 12 měsíců. Sezónní výkyvy tím zmizí, zůstane skutečný trend. První bod je březen 2025, dřív nemáme celý rok dat.',
  'findings':S('Klíčová zjištění',[
   f"Křížení Sinsay a Sheinu je tu vidět nejčistěji. Sinsay drží {shs('sinsay')} %, Shein {shs('shein')} %.",
   f"Erika se drží v pásmu kolem 2 %, nejde dolů rychleji než konkurenti stejné velikosti (Lelosi {n1(sos('lelosi',P,TP))} % na {n1(sos('lelosi',L,TL))} %).",
   "Na tomhle grafu se dá poznat, jestli značková kampaň něco udělala, protože jedna špička nebo propad křivkou skoro nepohne."])},
 {'id':'chart1cz','type':'line','data':'czShare','title':'Share of Search, užší česká konkurenční skupina',
  'explanation':'Pohled bez mezinárodních obrů (Shein, Sinsay, Reserved, Mohito, Modivo) a bez tří nejsilnějších českých domén (Bonprix, About You, Zalando). Ukazuje skutečné konkurenční prostředí Erika Fashion.',
  'note':'Nově je ve skupině Sqvele. Modivo je mezinárodní hráč, do užší skupiny proto nepatří, sledujeme ho v hlavním grafu.',
  'findings':S('Klíčová zjištění, užší česká konkurenční skupina',[
   f"Erika Fashion má {n1(sos('erikafashion',L,NL))} % proti {n1(sos('erikafashion',P,NP))} % o rok dřív. Lelosi má {n1(sos('lelosi',L,NL))} % proti {n1(sos('lelosi',P,NP))} %.",
   f"Náskok Lelosi se zmenšil z {n1(sos('lelosi',P,NP)-sos('erikafashion',P,NP))} na {n1(sos('lelosi',L,NL)-sos('erikafashion',L,NL))} procentního bodu. Lelosi ztrácí rychleji ({sg0(yoy('lelosi'))} % proti {sg0(yoy('erikafashion'))} % u Eriky).",
   f"Buga si polepšila z {n1(sos('buga',P,NP))} % na {n1(sos('buga',L,NL))} %, je jediná z velké čtveřice, která v absolutním hledání roste ({sg0(yoy('buga'))} %).",
   f"Glami kleslo z {n1(sos('glami',P,NP))} % na {n1(sos('glami',L,NL))} %, Orsay se drží na {n1(sos('orsay',L,NL))} %.",
   f"MiaDresses, nejbližší soupeř v šatech na události, ztratila {abs(round(yoy('miadresses')))} % hledání. Sqvele má {n1(sos('sqvele',L,NL))} % a {n0(sm('sqvele',L)/12)} hledání měsíčně."])},
 {'id':'chart2','type':'line','data':'brandAbs','title':'Brandové hledání, absolutní objem',
  'explanation':'Měsíční objem brandového hledání v ČR podle Ahrefs. Ahrefs počítá modelem, čísla berte jako odhad a porovnávejte hlavně mezi značkami.','dogAfter':True,
  'findings':S('Klíčová zjištění',[
   f"Erika Fashion má průměrně {n0(sm('erikafashion',L)/12)} hledání měsíčně proti {n0(sm('erikafashion',P)/12)} o rok dřív. Search Console přitom hlásí na samotný dotaz „erikafashion“ kolem 37 tisíc zobrazení měsíčně, reálná poptávka je tedy vyšší, než Ahrefs odhaduje.",
   f"Špička většiny velkých značek je v listopadu. Sinsay měl v listopadu 2025 {n0(bs['sinsay'][i('2025-11')])} hledání, About You {n0(bs['aboutyou'][i('2025-11')])}, Reserved {n0(bs['reserved'][i('2025-11')])}.",
   f"Skok About You ze {n0(bs['aboutyou'][i('2026-08')])} v srpnu na {n0(bs['aboutyou'][i('2026-09')])} v září neberte vážně. Google Trends ve stejné době ukazuje růst jen o pětinu.",
   f"Shein klesl z {n0(sm('shein',P)/12)} na {n0(sm('shein',L)/12)} hledání měsíčně. Uvolnilo se tak {n0((sm('shein',P)-sm('shein',L))/12)} hledání měsíčně, přes trojnásobek celé Eriky.",
   f"Mohito ({sg0(yoy('mohito'))} %), Orsay ({sg0(yoy('orsay'))} %) a Lelosi ({sg0(yoy('lelosi'))} %) ztrácejí podobným tempem jako Erika podle Ahrefs."])},
 {'id':'chart3','type':'line','data':'orgShare','title':'Share of Search, organický traffic (odhad Ahrefs)',
  'explanation':'Podíl na odhadované organické návštěvnosti mezi českými doménami. Nově jsou v setu Modivo, Lelosi a Sqvele.',
  'note':'Od května 2026 Ahrefs odhaduje u většiny webů výrazně méně návštěv. U Eriky Search Console v té době hlásí růst, propad je tedy aspoň zčásti změna modelu Ahrefs. Podíly mezi weby jsou spolehlivější než absolutní čísla.',
  'findings':S('Klíčová zjištění',[
   f"Erika Fashion má {n1(osh('erikafashion',L,OTL))} % proti {n1(osh('erikafashion',P,OTP))} % o rok dřív.",
   f"Zalando zůstává největší s {n1(osh('zalando',L,OTL))} % proti {n1(osh('zalando',P,OTP))} % o rok dřív.",
   f"Glami kleslo z {n1(osh('glami',P,OTP))} % na {n1(osh('glami',L,OTL))} %. Srovnávače ztrácejí viditelnost ve výsledcích vyhledávání.",
   f"About You má {n1(osh('aboutyou',L,OTL))} %, Bonprix {n1(osh('bonprix',L,OTL))} %."])},
 {'id':'chart4','type':'line','data':'orgAbs','title':'Organický traffic, absolutní čísla (odhad Ahrefs)',
  'explanation':'Měsíční odhad organické návštěvnosti. Poprvé jsou v grafu i Sinsay, Shein, Reserved a Mohito, jejich české údaje máme od listopadu 2024.',
  'note':'Ahrefs u mezinárodních domén dává filtr na ČR jen dva roky zpět, proto jejich křivky začínají později. Čísla .cz domén jsou celosvětová, u nich je rozdíl proti ČR kolem 1 %.',
  'findings':S('Klíčová zjištění',[
   f"V září 2026 Ahrefs odhaduje Zalando na {n0(organic['zalando'][i('2026-09')])}, Sinsay na {n0(organicIntl['sinsay'][i('2026-09')])}, About You na {n0(organic['aboutyou'][i('2026-09')])} a Reserved na {n0(organicIntl['reserved'][i('2026-09')])} návštěv.",
   f"Erika Fashion má {n0(ae('2026-09'))} návštěv. Za červenec až září je to podle Ahrefs {sg0(exsh(oq,oqp))} % meziročně, Search Console za stejné období ukazuje {sg0(exsh(qa,qap))} %.",
   f"Poměr odhadu Ahrefs ke skutečným klikům u Eriky skáče od {n1(ae('2026-06')/g['2026-06'][0])}× v červnu do {n1(ae('2026-09')/g['2026-09'][0])}× v září. Absolutní čísla konkurence proto berte jako řád, ne jako přesnou hodnotu.",
   f"Celá česká část setu je za červenec až září podle Ahrefs o {abs(round(exsh(okq,okqp)))} % níž než před rokem. Tak plošný propad bez změny na trhu je spíš změna modelu."])},
 {'id':'chartGT','type':'line','data':'gt','title':'Google Trends, zájem o značku (CZ)',
  'explanation':'Relativní zájem na stupnici do 100, kde 100 je nejsilnější týden v celé skupině. Jde o nejbližší zdroj k původní metodice Lese Bineta, bez odhadů třetích stran.',
  'note':'Týdenní data pro ČR, skupiny dotazů ukotvené na Shein, nově i Modivo. Erika má v tomhle měřítku malé hodnoty (nejvýš 6 bodů), procentní změny u ní jsou proto méně přesné než u velkých značek.',
  'findings':S('Klíčová zjištění, Google Trends',[
   f"Erika Fashion má za poslední rok o {round(gyoy('erikafashion'))} % vyšší zájem než rok předtím, největší růst ve skupině po Modivu ({sg0(gyoy('modivo'))} %).",
   f"Podíl Eriky ve sledované skupině vzrostl z {n2(100*g0('erikafashion')/gsp)} % na {n2(100*g1('erikafashion')/gsl)} %.",
   f"Shein ztratil za červenec až září {abs(round(gq('shein')))} % zájmu oproti stejnému období loni. Tady je dopad nového cla vidět nejlépe.",
   f"Bonprix roste o {round(gyoy('bonprix'))} %, i když Ahrefs mu ukazuje {sg0(yoy('bonprix'))} %. Sinsay {sg0(gyoy('sinsay'))} %, Reserved {sg0(gyoy('reserved'))} %.",
   f"Glami ({sg0(gyoy('glami'))} %) a Orsay ({sg0(gyoy('orsay'))} %) potvrzují pokles, který ukazuje i Ahrefs."])},
 {'id':'chartGSC','type':'gsc','title':'Google Search Console, reálná data erikafashion.cz',
  'explanation':'Skutečné kliky a zobrazení z Google vyhledávání, ne odhad. Do června 2025 z napojení přes Ahrefs, od července 2025 přímo z Google přes Marketing Miner. V překryvu se čísla shodují na klik.',
  'note':'V září 2025 Google přestal nástrojům vracet 100 výsledků najednou. Zobrazení a průměrná pozice se tehdy změnily u všech webů, před a po tomhle datu je nesrovnávejte. Říjen 2026 ještě není uzavřený, proto v grafu není.',
  'findings':S('Klíčová zjištění',[
   f"Za posledních 12 měsíců přišlo z Google {n0(G12)} kliků proti {n0(G12p)} o rok dřív, tedy {sg0(exsh(G12,G12p))} %.",
   f"Rostou obě části stejně rychle. Brandové kliky za červenec až září {sg0(exsh(qb,qbp))} %, ostatní {sg0(exsh(qa-qb,qap-qbp))} %.",
   f"Rekordem zůstává leden 2026 s {n0(g['2026-01'][0])} kliky. Květen a červen 2026 měly přes 45 tisíc, o 25 a 31 % víc než o rok dřív.",
   f"Průměrná pozice se od října 2025, kdy je srovnatelná, zlepšila z {n1(g['2025-10'][3])} na {n1(g['2026-09'][3])}. Skok z 13 na 7 na podzim 2025 je ale hlavně změna měření, ne skutečné zlepšení.",
   f"Mušelínové šaty vyrostly z {mus_b} na {n0(mus_a)} kliků (květen až září), pozice z 15,8 na 3,7. Podobně rostou dotazy jako šaty na promoce a business casual ženy.",
   "Za prvních 27 dní října 2026 je denní průměr o 18 % nad loňským říjnem, růst tedy pokračuje, jen pomaleji než v létě."])},
]
summary={
 'kpis':[
  {'label':'Brandové kliky z Google','value':n0(qb),'delta':f"{sg0(exsh(qb,qbp))} %",'note':f"červenec až září, loni {n0(qbp)}",'src':'Search Console'},
  {'label':'Všechny kliky z Google','value':n0(G12),'delta':f"{sg0(exsh(G12,G12p))} %",'note':f"12 měsíců, předtím {n0(G12p)}",'src':'Search Console'},
  {'label':'Podíl v užší české skupině','value':n1(sos('erikafashion',L,NL))+' %','delta':f"{sg(sos('erikafashion',L,NL)-sos('erikafashion',P,NP))} p. b.",'note':f"Lelosi {n1(sos('lelosi',L,NL))} %, náskok se zmenšil",'src':'Ahrefs'},
  {'label':'Podíl na Google Trends','value':n2(100*g1('erikafashion')/gsl)+' %','delta':f"{sg0(gyoy('erikafashion'))} % zájmu",'note':f"o rok dřív {n2(100*g0('erikafashion')/gsp)} %",'src':'Google Trends'},
 ],
 'lead':f"Erika Fashion roste rychleji, než ukazoval hlavní zdroj tohoto dashboardu. Ahrefs odhaduje u značky za rok {sg0(yoy('erikafashion'))} %, Google Trends za stejnou dobu {sg0(gyoy('erikafashion'))} % a brandové kliky za poslední čtvrtletí rostou o {round(exsh(qb,qbp))} %. Největší změna trhu je pád Sheinu o {abs(round(yoy('shein')))} %, uvolněná poptávka míří hlavně k Sinsay, About You, Reserved a Modivu. Doporučení proto řeší, jak z rostoucího zájmu vytěžit víc a jak si z uvolněné poptávky vzít svůj díl.",
 'tri':tri,'season':season,'moves':moves,
 'triFindings':[
   "Tři pohledy na stejnou značku za stejnou dobu. Ahrefs modeluje hledanost z dat třetích stran, Trends a Search Console vycházejí přímo z Googlu.",
   "Pro Eriku proto v dalších měsících platí přímá data. U konkurence je Ahrefs jediný zdroj absolutních čísel, srovnání s nimi berte jako orientační a kontrolujte je přes Trends."],
 'recs':[
  {'prio':'Vysoká','area':'Google Ads','title':'Ověřit, kolik brandová reklama skutečně přináší',
   'why':'Na dotaz „erikafashion“ je web organicky na pozici 1,3, a přesto má jen 6 % prokliků. Dotazy na vrácení zboží mají 70 až 85 %. Podle exportu z Google Ads (březen až září 2026) jde na tenhle dotaz přes reklamu víc než desetkrát tolik kliků co přes organiku a zhruba třetina konverzí účtu je přiřazená dotazům na značku. Pětina těchto kliků navíc končí v kategoriových kampaních PMax a zlepšuje jejich vykázaný výsledek.',
   'what':'Nejdřív se v Aukčních statistikách podívat, kdo na značku přihazuje. Pak na 4 týdny vypnout brandovou kampaň v polovině krajů a druhou polovinu nechat beze změny. Značku vyloučit z kampaní PMax bez ohledu na výsledek testu.',
   'measure':'Součet placených a organických kliků na značku a počet objednávek v testovaných krajích proti kontrolním. Hlavní přínos není úspora, ale čistší čísla u ostatních kampaní.','effort':'Malá'},
  {'prio':'Vysoká','area':'Značka a kampaně','title':'Značkové kampaně plánovat na leden a červen, ne na Black Friday',
   'why':f"Erika má jiný kalendář než velcí hráči. V lednu má {n2(season[0])} % hledání ve sledované skupině, v červnu {n2(season[5])} %, v listopadu jen {n2(season[10])} %. Sinsay, About You, Reserved a Zalando mají špičku v listopadu, kdy je o každé hledání největší souboj.",
   'what':'Na Black Friday držet výkon a stávající zákaznice. Značkový rozpočet (video, Meta, PR) soustředit na prosinec a leden kvůli plesům a na květen a červen kvůli svatbám a promocím. Rozhodnutí pro plesovou sezónu je potřeba udělat teď.',
   'measure':f"Podíl na Trends a brandové kliky v lednu 2027 proti lednu 2026 ({n0(gm['brand']['2026-01'][0])} brandových kliků).",'effort':'Střední'},
  {'prio':'Vysoká','area':'Akvizice','title':'Vzít si díl z poptávky po šatech u jiných značek',
   'why':f"Shein přišel o {n0((sm('shein',P)-sm('shein',L))/12)} hledání měsíčně. Sinsay, About You, Reserved a Modivo získaly dohromady {n0(gainers/12)}, Erika podle Ahrefs nic. Lidé přitom hledají šaty konkrétních značek. „Mohito šaty“ mají 2 900 hledání měsíčně, „Reserved šaty“ 2 700, „Orsay šaty“ a „Bonprix šaty“ po 1 600, „Shein šaty“ 900. Dohromady kolem 10 tisíc měsíčně, přes desetkrát víc než Erika Fashion ve spojení se slovem šaty.",
   'what':'Samostatná kampaň na dotazy „značka + šaty“ vedoucí do výpisu šatů. Jméno konkurenta nesmí být v textu reklamy. Soutěžit výběrem a doručením do 2 dnů, ne cenou proti Sheinu.',
   'measure':'Cena za konverzi proti ostatním nebrandovým kampaním, podíl nových zákaznic, po 3 měsících rozhodnutí o rozšíření.','effort':'Malá'},
  {'prio':'Střední','area':'Značka a obsah','title':'Využít zájem o Eriku Eliášovou',
   'why':f"Dotazy na jméno zakladatelky vyrostly z {eli_b} na {n0(eli_a)} kliků (květen až září), pozice z 8 na 3. Stránka /muj-pribeh-erika-eliasova/ má 10 tisíc zobrazení za pět měsíců. Google navíc sám nabízí otázky „Kdo vlastní Erika Fashion?“ a „Kdo je Erika Fashion?“. Osobní příběh je něco, co Sinsay ani Shein nemají.",
   'what':'Zjistit, co zájem spustilo (rozhovor, sociální sítě, média). Odkázat na stránku z homepage a z kategorií šatů, doplnit strukturovaná data o osobě, přidat fotky a video. Do plánu PR dát rozhovory s Erikou před plesovou sezónou.',
   'measure':'Kliky na jméno zakladatelky a návazné brandové dotazy po každém výstupu v médiích.','effort':'Střední'},
  {'prio':'Střední','area':'Zákaznická zkušenost','title':'Ze stránky o vrácení zboží udělat stránku o výměně',
   'why':f"Kliky na dotazy o vrácení se zdvojnásobily, z {n0(ret_b)} na {n0(ret_a)} (květen až září). Je to 12 % všech brandových kliků. Část růstu vysvětluje víc objednávek, a není to jen téma Eriky („Lelosi vrácení zboží“ má 1 200 hledání, u Reserved 900). Stránka /vraceni-zbozi/ má 70% prokliky, čte ji tedy skoro každý, kdo hledá.",
   'what':'Na začátek stránky dát výměnu za jinou velikost nebo barvu, teprve pod ní vrácení. Přidat online formulář a nabídku k výměně, třeba doplnění outfitu.',
   'measure':'Poměr výměn k vrácením a podíl vrácených objednávek po dobu 3 měsíců proti stejnému období loni.','effort':'Střední'},
  {'prio':'Střední','area':'SEO','title':'Soustředit hledání recenzí na hlavní stránku hodnocení',
   'why':f"Kliky na „recenze“ se ztrojnásobily, z {rec_b} na {rec_a} (květen až září). Hlavní stránka /hodnoceni-obchodu/ má pozici 2,8, ale zobrazení se tříští mezi desítky stránkovaných adres (třeba /hodnoceni-obchodu/strana-41/ s pozicí 8,6 a prokliky 0,4 %). Podle snímku Ahrefs nad výsledky odpovídá AI přehled, který cituje hodnocení Eriky a Zboží.cz.",
   'what':'Na začátek hlavní stránky dát přehled (počet hodnocení, průměr, co zákaznice chválí a co se řeší), doplnit strukturovaná data a stránkování nastavit tak, aby se ve výsledcích ukazovala první strana. Adresy neměnit.',
   'measure':'Podíl kliků a pozice hlavní stránky, jestli ji cituje AI přehled.','effort':'Malá'},
  {'prio':'Sledovat','area':'Konkurence','title':'Hlídat Modivo a jeho věrnostní program',
   'why':f"Modivo roste o {round(yoy('modivo'))} % podle Ahrefs a o {round(gyoy('modivo'))} % podle Trends. V hledání předběhlo Lelosi i Eriku. Výrazný dotaz je „Modivo Club“ s 1 400 hledáními měsíčně, věrnostní program, který lidé hledají jménem.",
   'what':'Zatím jen sledovat. Pokud trend vydrží do jara, stojí za úvahu test věrnostního programu pro stálé zákaznice Eriky.',
   'measure':'Podíl Modiva v příští edici tohoto dashboardu.','effort':'Bez nákladů'},
 ],
 'reading':[
  ['Ahrefs počítá modelem a mění historii.',f"Shein za duben 2026 měl v dubnové edici {n0(old['brandSearch']['shein'][-1])} hledání, dnes je to {n0(bs['shein'][i('2026-04')])}. Archiv proto ukazuje čísla tak, jak byla, nová edice je přepočítaná celá."],
  ['Porovnávat rok k roku, ne duben s říjnem.','Móda je silně sezónní. Všechna srovnání tady jsou 12 měsíců proti předchozím 12, nebo stejné období loni.'],
  ['Jedna oprava proti dubnové edici.','V dubnu jsme psali, že se průměrná pozice zlepšila z 10 na 6,5. Velkou část toho skoku způsobila změna měření v Googlu v září 2025, ne skutečné zlepšení.'],
  ['Co v datech není.','Data končí zářím 2026. Trendy-obleceni.cz nesledujeme, skoro nikdo ho nehledá jménem (do 5 hledání měsíčně). Google Ads uvádíme jen v poměrech.'],
 ],
 'sources':[{'label':'Retail Gazette, clo EU na levné zásilky od 1. 7. 2026','url':'https://www.retailgazette.co.uk/blog/2026/07/shein-and-temu-hit-by-new-eu-customs-duty-on-cheap-parcels/'},{'label':'IPA, Les Binet a Share of Search','url':'https://ipa.co.uk/news/binet-presents-fast-cheap-predictive-share-of-search-metric/'},{'label':'Marketing Week, 83 % podílu na trhu','url':'https://www.marketingweek.com/share-of-search-market-share/'}],
}
content={'snapshotTitle':'Aktuální stav, 30. 10. 2026','sections':sections,'snapshotColumns':True,'czSet':NARROW,'snapshotFindings':[
  f"Erika Fashion má {n0(snapshot['erikafashion']['orgKeywords'])} klíčových slov v ČR proti 4 473 v dubnu a {n0(snapshot['erikafashion']['orgKeywords1_3'])} v top 3 proti 2 023. To je {sg0(exsh(snapshot['erikafashion']['orgKeywords1_3'],2023))} % za půl roku.",
  f"Doménová autorita Eriky je {round(snapshot['erikafashion']['dr'])}, u přímých konkurentů v šatech 11 (MiaDresses), 13 (Blanka Straka), 15 (Lelosi) a 18 (Sqvele)."],
 'method':[['Datový zdroj','Ahrefs (Keywords Explorer, Site Explorer), Google Search Console přes Ahrefs a Marketing Miner, Google Trends'],['Region','Česká republika'],['Období','Duben 2024 až září 2026 (30 měsíců), stav domén k 30. 10. 2026'],['Brandové hledání','Součet stejných variant značky jako v dubnu, pro Modivo a Sqvele nově. Jeden stažený výpis, historie je přepočítaná'],['Organický traffic','Odhad Ahrefs. Domény .cz bez filtru na zemi, mezinárodní domény s filtrem na ČR od 11/2024'],['Google Trends','Týdně, ČR, ukotvení na Shein, 13 značek'],['Aktualizace','Ručně přes Claude Code, každá edice se ukládá jako vlastní záložka'],['Kontrola','Rok k roku a tři zdroje vedle sebe, viz záložka Shrnutí a doporučení']]}
hist={'lastUpdated':'2026-10-30','edition':'2026-10','dates':ms,'brands':brands,'brandSearch':bs,'organicTraffic':organic,'organicIntl':organicIntl,'snapshot':snapshot,'gsc':gsc,
 'brandTerms':{'erikafashion':[{'kw':t['keyword'],'vol':t['volume']} for t in terms][:14]},'brandAssociations':assoc,'googleTrends':gt,'brandVariants':variants,'content':content,'summary':summary}
# dubnová edice beze změny dat, texty přesně z původní stránky
if not os.path.exists('data/editions/2026-04.json'):
    os.makedirs('data/editions',exist_ok=True)
    a=J('data/history.json')
    for v in a['brandVariants']['erikafashion']: v['kw']=v['kw'].replace('�aty','šaty')
    for v in a['brandVariants']['shein']: v['kw']=v['kw'].replace('�esko','česko')
    F=lambda n:af[n]
    a['edition']='2026-04'
    a['content']={'archive':True,'snapshotTitle':'Aktuální stav — duben 2026','legacyGsc':True,
     'noData':['buga','evona','miadresses','blankastraka','londonclub','coolboutique','bestmoda'],
     'sections':[
      {'id':'chart1','type':'line','data':'brandShare','title':'Share of Search — brandové hledání v ČR','methodology':True,'explanation':'Podíl brandového vyhledávání každé značky na celku. Tato metrika je nejsilnějším prediktorem tržního podílu — když Share of Search roste, tržní podíl typicky následuje za 6–12 měsíců (Les Binet, 2020).','findings':F('buildFindings1')},
      {'id':'chart1cz','type':'line','data':'czShare','title':'Share of Search — užší česká konkurenční skupina','explanation':'Alternativní pohled bez mezinárodních obrů (Shein, Sinsay, Reserved, Mohito) a bez tří nejsilnějších českých hráčů (Bonprix, About You, Zalando). Zobrazuje skutečné konkurenční prostředí Erika Fashion — středně velké české značky specializované na šaty a dámské oblečení.','note':'Pozn.: Vynechány jsou shein.com, sinsay.com, reserved.com, mohito.com (mezinárodní) a bonprix.cz, aboutyou.cz, zalando.cz (tři nejsilnější české domény).','findings':F('buildFindings1CZ')},
      {'id':'chart2','type':'line','data':'brandAbs','title':'Brandové hledání — absolutní objem','explanation':'Absolutní měsíční objem brandového vyhledávání v ČR ukazuje skutečnou velikost poptávky po každé značce.','findings':F('buildFindings2'),'dogAfter':True},
      {'id':'chart3','type':'line','data':'orgShare','title':'Share of Search — organický traffic (odhad Ahrefs)','explanation':'Organický traffic ukazuje, jak úspěšně značka přeměňuje brandovou poptávku a generické vyhledávání na skutečné návštěvy webu.','note':'Pozn.: Pro mezinárodní domény (shein.com, sinsay.com, mohito.com, reserved.com) historická data na úrovni ČR nejsou k dispozici.','findings':F('buildFindings3')},
      {'id':'chart4','type':'line','data':'orgAbs','title':'Organický traffic — absolutní čísla (ČR)','explanation':'Absolutní čísla organického trafficu (měsíční odhad Ahrefs) ukazují reálné objemy návštěv.','findings':F('buildFindings4')},
      {'id':'chartGT','type':'line','data':'gt','title':'Google Trends — zájem o značku (CZ)','explanation':'Google Trends ukazuje relativní zájem o značky na 100-bodové stupnici. Hodnota 100 odpovídá týdnu s nejvyšším zájmem v měřené skupině. Jde o klasickou definici Share of Search podle Lese Bineta, postavenou přímo na Google dávkových datech (ne odhadech).','note':'Data: Google Trends, region ČR, týdenní vzorkování. Značky jsou normalizovány pomocí ukotvení na Shein pro mezinárodní porovnatelnost. Zobrazeno top 12 značek.','findings':F('buildFindingsGT')},
      {'id':'chartGSC','type':'gsc','title':'Google Search Console — reálná data erikafashion.cz','explanation':'Na rozdíl od odhadů Ahrefs, Google Search Console ukazuje skutečné kliky a imprese z Google vyhledávání.','note':'Data: Google Search Console propojená přes Ahrefs projekt. Únor 2026 obsahuje pouze částečná data a je z grafu vyloučen.','findings':F('buildFindingsGSC')},
     ],
     'method':[['Datový zdroj','Ahrefs API (Keywords Explorer pro brandová data, Site Explorer pro organické metriky) + Google Search Console'],['Region','Česká republika'],['Období','Duben 2024 – duben 2026 (25 měsíců)'],['Brandové hledání','Součet objemu hlavních brandových variant (např. "erikafashion" + "erika fashion" + "erikafashion.cz")'],['Organický traffic','Měsíční odhad Ahrefs na základě pozic v SERPu a CTR modelu'],['Aktualizace','Měsíčně'],['Databáze','Historická data ukládána v data/history.json'],['Limitace','Pro mezinárodní domény historická ČR data nejsou k dispozici na Ahrefs Standard plánu']]}
    json.dump(a,open('data/editions/2026-04.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
json.dump(hist,open('data/history.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
json.dump({'current':'2026-10','tabs':[
 {'id':'shrnuti','label':'Shrnutí a doporučení','kind':'summary','file':'history.json'},
 {'id':'data-2026-10','label':'Data, říjen 2026','kind':'data','file':'history.json','badge':'Poslední aktualizace: 30. 10. 2026 | Data do září 2026'},
 {'id':'archiv-2026-04','label':'Archiv, duben 2026','kind':'data','file':'editions/2026-04.json','badge':'Archiv: stav z 19. 4. 2026, čísla ani závěry se nemění'}]},
 open('data/editions/index.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('hotovo')
