# `lab/curl` — canlı doğrulama araçları

> §14.0'ın *«curl asıl kanıttır»* protokolünün somut hâli. Kapı gerilemeyi ölçer;
> **doğru çalıştığını curl gösterir.**

## Kullanım

```bash
bash lab/curl/login.sh            # token al (tok.txt'e yazar)
bash lab/curl/kontrol.sh          # hat sağlam mı (401 kör noktasını kapatır)
bash lab/curl/sor.sh "bu yıl toplam ciro"          # taze soru
bash lab/curl/thread.sh "neden" /tmp/th.json       # thread'li takip
```

⚠ **`kontrol.sh` her turdan ÖNCE koşulur.** Ölçülmüş kör nokta: süresi dolmuş token
`source=None` gibi görünür ve **sahte bir ürün kusuru** olarak loglanır.

## Ortam

```bash
export DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0
docker-compose build dima-backend
docker rm -f dima-backend-core && docker-compose up -d dima-backend
```

API **8001**'de (konteyner içinde 8000). Demo kimlik:
`demo-boyahane@usedima.com` / `dima-demo-1234`

## Kural

🔴 **Tek tek sor, logu oku.** Toplu bombardıman yok — bu depoda ölçülmüş bir kuraldır:
her tur **≥20 özgün senaryo**, tek tek, sonra **TÜM** teşhisler, sonra **TÜM** düzeltmeler,
sonra **BİR** tazeleme + **BİR** curl + **BİR** kapı.
