# -*- coding: utf-8 -*-
import json,re,collections
raw=json.load(open('zdroje/2026-10/raw.json',encoding='utf-8'))
old=json.load(open('data/history.json',encoding='utf-8'))
ms=[f"{y}-{m:02d}" for y in (2024,2025,2026) for m in range(1,13)]
ms=ms[ms.index('2024-04'):ms.index('2026-09')+1]
kw={}
for r in raw:
    if r['tool']=='keywords-explorer-overview' and 'volume_monthly_history' in r['input'].get('select',''):
        t=r['text']
        if 'HTTP 400' in t[:60]: continue
        if t.lstrip().startswith('['): t=json.loads(t)[0]['text']
        d=json.JSONDecoder().raw_decode(t.lstrip())[0]
        for k in d['keywords']:
            kw[k['keyword']]={h['date'][:7]:h['volume'] for h in k['volume_monthly_history']}
V=dict(old['brandVariants'])
V['erikafashion']=[{'kw':x['kw'].replace('�aty','šaty')} for x in V['erikafashion']]
V['shein']=[{'kw':x['kw'].replace('�esko','česko')} for x in V['shein']]
V['modivo']=[{'kw':k} for k in ('modivo','modivo.cz','modivo cz')]
V['sqvele']=[{'kw':'sqvele'}]
bs={}
for b,vs in V.items():
    miss=[v['kw'] for v in vs if v['kw'] not in kw]
    if miss: print('CHYBI',b,miss)
    bs[b]=[sum(kw.get(v['kw'],{}).get(m,0) for v in vs) for m in ms]
json.dump({'months':ms,'brandSearch':bs,'kw':kw},open('zdroje/2026-10/brand.json','w',encoding='utf-8'),ensure_ascii=False)
i=lambda m:ms.index(m)
L=slice(i('2025-10'),i('2026-09')+1); P=slice(i('2024-10'),i('2025-09')+1)
tot=lambda s,ids:sum(sum(bs[b][s]) for b in ids)
allids=list(bs); orig=[b for b in allids if b not in('modivo','sqvele')]
print('brand  12m_now 12m_prev yoy% | SoS now prev (new set) | SoS old set | Sep26 Sep25')
for b in sorted(allids,key=lambda b:-sum(bs[b][L])):
    n,p=sum(bs[b][L]),sum(bs[b][P])
    print(f"{b:13} {n:8} {p:8} {100*(n-p)/p:6.1f} | {100*n/tot(L,allids):5.2f} {100*p/tot(P,allids):5.2f} | {100*n/tot(L,orig) if b in orig else 0:5.2f} {100*p/tot(P,orig) if b in orig else 0:5.2f} | {bs[b][i('2026-09')]} {bs[b][i('2025-09')]}")
print('total',tot(L,allids),tot(P,allids),100*(tot(L,allids)-tot(P,allids))/tot(P,allids))
cz=['erikafashion','lelosi','glami','orsay','buga','evona','miadresses','blankastraka','londonclub','coolboutique','bestmoda','sqvele']
print('NARROW')
for b in sorted(cz,key=lambda b:-sum(bs[b][L])):
    print(f"{b:13} {100*sum(bs[b][L])/tot(L,cz):5.1f} {100*sum(bs[b][P])/tot(P,cz):5.1f}")
print('Erika monthly',bs['erikafashion'])
print('old erika    ',old['brandSearch']['erikafashion'])
for b in ('erikafashion','aboutyou','sinsay','shein'):
    print(b,'revize apr26 stare/nove',old['brandSearch'][b][-1],bs[b][i('2026-04')],'apr24',old['brandSearch'][b][0],bs[b][0])
print('about you Aug/Sep26 skok',kw['about you']['2026-07'],kw['about you']['2026-08'],kw['about you']['2026-09'],kw['about you']['2026-10'])
# organic
org={}
for r in raw:
    if r['tool']=='site-explorer-metrics-history':
        t=r['text']; dom=r['input']['target']; c=r['input'].get('country')
        if 'Insufficient' in t: continue
        rows=re.findall(r'(\d{4}-\d{2})-01T[^,]+,(\d+)',t) or re.findall(r'"date":\s*"(\d{4}-\d{2})-01T[^"]+",\s*"org_traffic":\s*(\d+)',t)
        if not rows: continue
        key=(dom,c)
        cur=org.setdefault(key,{})
        cur.update({m:int(v) for m,v in rows})
for k,v in org.items(): print(k,len(v),min(v),max(v))
json.dump({f"{k[0]}|{k[1]}":v for k,v in org.items()},open('zdroje/2026-10/organic.json','w',encoding='utf-8'))
cz=[('erikafashion.cz',None),('glami.cz',None),('aboutyou.cz',None),('bonprix.cz',None),('orsay.cz',None),('londonclub.cz',None),('miadresses.cz',None),('zalando.cz',None),('modivo.cz',None),('lelosi.cz',None),('sqvele.com',None)]
def s(k,a,b):
    return sum(org[k].get(m,0) for m in ms[i(a):i(b)+1])
print('organic: Jan-Apr26 vs Jun-Sep26, a 12m')
for k in cz+[('sinsay.com','CZ'),('shein.com','CZ'),('reserved.com','CZ'),('mohito.com','CZ')]:
    print(f"{k[0]:18} sep26 {org[k]['2026-09']:7} sep25 {org[k]['2025-09']:7} yoy {100*(org[k]['2026-09']-org[k]['2025-09'])/org[k]['2025-09']:6.1f} | 3m(jul-sep) {s(k,'2026-07','2026-09'):7} vs {s(k,'2025-07','2025-09'):7} {100*(s(k,'2026-07','2026-09')-s(k,'2025-07','2025-09'))/s(k,'2025-07','2025-09'):6.1f}")
t=lambda a,b:sum(s(k,a,b) for k in cz)
print('cz set total 3m',t('2026-07','2026-09'),t('2025-07','2025-09'))
