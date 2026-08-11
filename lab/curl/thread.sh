#!/bin/bash
# $1 = soru, $2 = thread durum dosyası (boşsa taze soru)
SP="${DIMA_CURL_TMP:-/tmp/dima-curl}"; mkdir -p "$SP"
TOKEN=$(cat $SP/tok.txt); Q="$1"; ST="$2"
python3 -c "
import json,sys,os
q,st=sys.argv[1],sys.argv[2]
d={'question':q}
if st and os.path.exists(st):
    s=json.load(open(st))
    d['history']=s.get('history',[])
    if s.get('cube_query'): d['cube_query']=s['cube_query']
    if s.get('diyalog_durumu'): d['diyalog_durumu']=s['diyalog_durumu']
    if s.get('sql'): d['prev_sql']=s['sql']
    if s.get('rapor'):
        r=dict(s['rapor'])
        r['pages']=[[{**b,'result':None,'viz':None} for b in (sf or [])] for sf in (r.get('pages') or [])]
        d['previous_rapor']=r
print(json.dumps(d,ensure_ascii=False))" "$Q" "$ST" > $SP/.gonder.json
curl -s -X POST localhost:8001/ask -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' --data-binary @$SP/.gonder.json > $SP/.son.json
python3 -c "
import json,sys,os
d=json.load(open('$SP/.son.json')); st='$ST'; q='''$Q'''
rows=((d.get('result') or {}).get('rows')) or []
cq=d.get('cube_query')
print('  source=%s rows=%d cube=%s' % (d.get('source'), len(rows), (cq or {}).get('cube')))
if rows: print('  ilk   =', json.dumps(rows[0],ensure_ascii=False)[:200])
for k,lab,n in (('note','note',260),('answer','ans',220)):
    v=(d.get(k) or '').replace('\n',' ')
    if v: print('  %s  =' % lab, v[:n])
t=d.get('trace')
if t: print('  trace =', json.dumps(t,ensure_ascii=False)[:340])
if cq: print('  cq    =', json.dumps({k:v for k,v in cq.items() if k in ('cube','measures','dimensions','order','limit','filters','timeDimensions')},ensure_ascii=False)[:300])
r_=d.get('rapor') or {}
for _p in (r_.get('pages') or []):
    for _b in (_p or []):
        _oz=_b.get('ozet_degil')
        print('  blok  =', (_b.get('title') or '')[:60], '| ozet_degil=%s' % ('VAR(%d satır/%d boyut)' % (_oz.get('satir',0), _oz.get('boyut',0)) if _oz else 'yok'))
vh=d.get('view_hint')
if vh: print('  vhint =', vh)
v=d.get('viz') or {}
if v: print('  viz   =', json.dumps({k:v.get(k) for k in ('kind','time_col','dims','measures','y2','series') if v.get(k)},ensure_ascii=False)[:200])
ns=d.get('next_steps')
if ns: print('  next  =', json.dumps([x.get('label') if isinstance(x,dict) else x for x in ns],ensure_ascii=False)[:180])
s=d.get('suggestions')
if s: print('  chip  =', json.dumps([x.get('label') for x in s],ensure_ascii=False)[:200])
if st:
    old=json.load(open(st)) if os.path.exists(st) else {'history':[]}
    h=old.get('history',[]); h.append(q)
    json.dump({'history':h,'rapor':d.get('rapor') or old.get('rapor'),'cube_query':cq or old.get('cube_query'),
               'diyalog_durumu':d.get('diyalog_durumu') or old.get('diyalog_durumu'),
               'sql':d.get('sql') or old.get('sql')}, open(st,'w'), ensure_ascii=False)
"
