#!/bin/bash
# §D3 — CEVAP BİÇİMİ ÖLÇÜM ALETİ (raporun §18 tablosunun birebir sütunları)
#
# 🔴 Neden ayrı bir alet: `sor.sh` biçim kararının GEREKÇESİNİ (`viz.cizilmedi`) ve
# olgu sayısını hiç basmıyor. Basılmayan bir alan "yok" gibi okunur ve olmayan bir
# kusur icat ettirir (bu operasyonda dört kez oldu). §18'in sütunları: viz · satır ·
# not(karakter) · olgu · chip — hepsi burada, kırpılmadan sayılır.
SP="${DIMA_CURL_TMP:-/tmp/dima-curl}"; mkdir -p "$SP"
TOKEN=$(cat $SP/tok.txt)
Q="$1"; TH="$2"
BODY=$(python3 -c "import json,sys; d={'question':sys.argv[1]}; th=sys.argv[2] if len(sys.argv)>2 and sys.argv[2] else None
if th: d['thread_id']=th; d['session_id']=th
print(json.dumps(d,ensure_ascii=False))" "$Q" "$TH")
echo "── $Q"
# 🔴 401'i sessizce `source=None` diye okumak bu operasyonda ölçülmüş bir kör noktadır
# (süresi dolmuş token sahte bir ürün kusuru ürettirdi). Tur ORTASINDA da düşebilir —
# bu yüzden kontrol her istekte, `kontrol.sh`'a ek olarak burada da yapılır.
_Y=$(curl -s -w '\n%{http_code}' -X POST localhost:8001/ask -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' -d "$BODY")
_K=$(printf '%s' "$_Y" | tail -n1)
if [ "$_K" = "401" ]; then
  echo "  ⚠ HTTP 401 — token düştü, tazeleniyor ve TEKRAR soruluyor"
  bash "$(dirname "$0")/login.sh" >/dev/null 2>&1
  TOKEN=$(cat $SP/tok.txt)
  _Y=$(curl -s -w '\n%{http_code}' -X POST localhost:8001/ask -H "Authorization: Bearer $TOKEN" \
       -H 'Content-Type: application/json' -d "$BODY")
  _K=$(printf '%s' "$_Y" | tail -n1)
fi
if [ "$_K" != "200" ]; then echo "  🔴 HTTP $_K — ÖLÇÜM GEÇERSİZ"; printf '%s\n' "$_Y" | head -c 300; exit 1; fi
printf '%s' "$_Y" | sed '$d' | python3 -c '
import sys, json
d = json.load(sys.stdin)
rows = ((d.get("result") or {}).get("rows")) or []
viz = d.get("viz") or {}
yorum = d.get("interpretation") or {}
olgu = yorum.get("facts") or []
chip = d.get("suggestions") or []
nxt = d.get("next_steps") or []
note = d.get("note") or ""
ans = d.get("answer") or ""
anlati = yorum.get("narration") or ""
print("  viz=%-8s satır=%-5d not=%-4d ans=%-4d anlatı=%-4d olgu=%-2d chip=%-2d next=%d"
      % (viz.get("kind"), len(rows), len(note), len(ans), len(anlati),
         len(olgu), len(chip), len(nxt)))
print("  source=%s cube=%s ölçü=%s boyut=%s"
      % (d.get("source"), (d.get("cube_query") or {}).get("cube"),
         viz.get("measures"), viz.get("dims")))
for t in (d.get("trace") or []):
    if str(t).startswith("niyet:"): print("  NİYET     =", t)
print("  özet      =", repr((yorum.get("summary") or ""))[:180])
if viz.get("cizilmedi"): print("  çizilmedi =", viz["cizilmedi"])
if viz.get("neden"): print("  neden     =", viz["neden"])
if note: print("  note      =", note.replace("\n", " ")[:200])
if ans: print("  ans       =", ans.replace("\n", " ")[:200])
if anlati: print("  anlatı    =", anlati.replace("\n", " ")[:200])
for f in olgu[:4]:
    print("  olgu      =", json.dumps(f, ensure_ascii=False)[:160])
if chip: print("  chip      =", json.dumps(chip, ensure_ascii=False)[:220])
'
