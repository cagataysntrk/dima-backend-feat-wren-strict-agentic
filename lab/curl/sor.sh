#!/bin/bash
SP="${DIMA_CURL_TMP:-/tmp/dima-curl}"; mkdir -p "$SP"
TOKEN=$(cat $SP/tok.txt)
Q="$1"; TH="$2"
BODY=$(python3 -c "import json,sys; d={'question':sys.argv[1]}; th=sys.argv[2] if len(sys.argv)>2 and sys.argv[2] else None
if th: d['thread_id']=th; d['session_id']=th
print(json.dumps(d,ensure_ascii=False))" "$Q" "$TH")
curl -s -X POST localhost:8001/ask -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' -d "$BODY" | python3 -c '
import sys,json
d=json.load(sys.stdin)
src=d.get("source"); rows=((d.get("result") or {}).get("rows")) or []
print("  source=%s rows=%d cube=%s" % (src, len(rows), (d.get("cube_query") or {}).get("cube") if d.get("cube_query") else None))
if rows: print("  ilk   =", json.dumps(rows[0],ensure_ascii=False)[:200])
n=(d.get("note") or "").replace("\n"," ")
if n: print("  note  =",n[:260])
a=(d.get("answer") or "").replace("\n"," ")
if a: print("  ans   =",a[:200])
t=d.get("trace")
if t: print("  trace =",json.dumps(t,ensure_ascii=False)[:330])
cq=d.get("cube_query")
if cq: print("  cq    =",json.dumps({k:v for k,v in cq.items() if k in ("cube","measures","dimensions","order","limit","filters","timeDimensions","pencere","turev")},ensure_ascii=False)[:260])
vh=d.get("view_hint")
if vh: print("  vhint =", vh)
v=d.get("viz") or {}
if v: print("  viz   =", json.dumps({k:v.get(k) for k in ("kind","time_col","dims","measures","y2","series") if v.get(k)},ensure_ascii=False)[:200])
ns=d.get("next_steps")
if ns: print("  next  =", json.dumps([x.get("label") if isinstance(x,dict) else x for x in ns],ensure_ascii=False)[:180])
s=d.get("suggestions")
if s: print("  chip  =",json.dumps(s,ensure_ascii=False)[:200])
'
