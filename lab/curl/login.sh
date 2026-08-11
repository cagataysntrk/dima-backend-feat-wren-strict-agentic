#!/bin/bash
SP="${DIMA_CURL_TMP:-/tmp/dima-curl}"; mkdir -p "$SP"
curl -s -X POST localhost:8001/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"demo-boyahane@usedima.com","password":"dima-demo-1234"}' \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])' > $SP/tok.txt
