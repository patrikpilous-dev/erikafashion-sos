# -*- coding: utf-8 -*-
"""Vytáhne výsledky volání Ahrefs a Marketing Miner ze záznamu session do zdroje/2026-10/raw.json.
MCP Ahrefs nejde volat ze skriptu, tohle je jediný způsob, jak čísla nepřepisovat ručně."""
import json,sys,glob,os,re
S=sys.argv[1]; OUT=sys.argv[2]
uses={}; res=[]
for line in open(S,encoding='utf-8'):
    try: o=json.loads(line)
    except: continue
    c=(o.get('message') or {}).get('content')
    if not isinstance(c,list): continue
    for b in c:
        if b.get('type')=='tool_use': uses[b['id']]=(b['name'],b['input'])
        if b.get('type')=='tool_result':
            t=b.get('content')
            if isinstance(t,list): t=''.join(x.get('text','') for x in t if isinstance(x,dict))
            res.append((b['tool_use_id'],t))
out=[]
for i,t in res:
    if i not in uses: continue
    n,a=uses[i]
    if not re.search(r'keywords-explorer|metrics-history|batch-analysis|gsc-performance|gsc_',n): continue
    if t and t.startswith('Error: result'):
        p=re.search(r'saved to (.+?\.txt)',t).group(1)
        t=open(p,encoding='utf-8').read()
    out.append({'tool':n.split('__')[-1],'input':a,'text':t})
json.dump(out,open(OUT,'w',encoding='utf-8'),ensure_ascii=False)
from collections import Counter
print(Counter(x['tool'] for x in out))
