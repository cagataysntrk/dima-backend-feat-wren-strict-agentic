#!/bin/bash
# 🔴 ÖLÇÜM ARACININ KÖR NOKTASI: 401 `source=None` gibi görünüyordu ve sahte bir ürün
# kusuru olarak loglanabilirdi. Her turdan önce koşulur.
SP="${DIMA_CURL_TMP:-/tmp/dima-curl}"; mkdir -p "$SP"
K=$(curl -s -o /dev/null -w '%{http_code}' -X POST localhost:8001/ask \
    -H "Authorization: Bearer $(cat $SP/tok.txt)" -H 'Content-Type: application/json' \
    -d '{"question":"bu yıl toplam ciro"}')
if [ "$K" != "200" ]; then
  echo "⚠ HTTP $K → token tazeleniyor"; bash "$(dirname "$0")/login.sh"
  K=$(curl -s -o /dev/null -w '%{http_code}' -X POST localhost:8001/ask \
      -H "Authorization: Bearer $(cat $SP/tok.txt)" -H 'Content-Type: application/json' \
      -d '{"question":"bu yıl toplam ciro"}')
fi
echo "ölçüm hattı: HTTP $K"
