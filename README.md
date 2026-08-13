# DİMA — depoya giriş

> **Bu dosya bir referans değil, bir YÖN TABELASIDIR.** Amacı tek şey: buraya ilk kez
> bakan birinin **yarım saat içinde** ne olduğunu, nasıl koşturulacağını ve nereye
> bakacağını bilmesi. Derinlik başka dosyalarda ve hepsine buradan gidilir.

---

## 1 · Bu nedir

**Türkçe soru → sayı.** Kullanıcı *«geçen ay RAM-3'te fire ne kadar?»* yazar; sistem
cevabı **semantik katmandaki küplerden** üretir.

🔴 **Ürünün bel kemiği tek cümle:** *sayıyı **her zaman küp** koyar, LLM koymaz.* LLM iki
yerde kullanılır ve **güven dereceleri zıttır**:

| rol | kim | tutum |
|---|---|---|
| 🗣 **GARSON** | Intent-LLM — kullanıcının sözünü **sistem diline çevirir** | ✅ güvendiğimiz hakem |
| 🍳 **AŞÇI** | küpler + `route()` — sayıyı **her zaman o** koyar | ✅ mutfakta LLM'e güven yok |
| 🥡 **YAN DÜKKÂN** | Discovery (ham SQL) | ⚠ istemediğimiz son çare |

⊙ *Discovery'nin her ateşlenmesi bir **mutfak eksikliği raporudur**.* Gerekçeler
`backend/CLAUDE.md`'nin en üst kuralında.

---

## 2 · Depo haritası — hangi dizin ne

| yol | ne | kime |
|---|---|---|
| **`backend/`** | FastAPI + küp yönlendirici + orkestratör. **Asıl iş burada.** | herkese |
| `backend/app/` | ürün kodu (`cube_router` · `oneri` · `plan_*` · `routers/`) | geliştirici |
| `backend/tests/` | **5.100+** test — bu depoda kapılar **gerekçe taşır**, okunur | geliştirici |
| `backend/lab/` | ölçüm araçları: korpus · kapı koşucusu · öneri ölçümü | ölçüm yapan |
| `backend/demo/` | kendi kendine yeten DuckDB demo verisi + pack'ler | herkese |
| **`dima-frontend-demo-master/`** | Next.js arayüz (`pnpm dev`) | FE geliştirici |
| **`belgeler/`** | tüm belgeler — [**`belgeler/00-INDEKS.md`**](belgeler/00-INDEKS.md) yerleşim kuralını anlatır | herkese |
| `WrenAI-main/` | üst-akım Wren kaynağı (referans) | nadiren |
| `lab/` · `logs/` | müşteri DB laboratuvarı · koşum kütükleri | duruma göre |

⚠ **`demo/wren-project` SİLİNMEZ** — adı eski Docker motorunu çağrıştırır ama **yeni,
in-process motorun** semantik model dizinidir; silinirse **her cevap düşer**.

---

## 3 · Ayağa kaldır

**Backend** (kaynak konteynere bind-mount **edilmez** — kod değişince **yeniden derle**):

```bash
cd <repo>
ETIKET="s$(( $(docker images --format '{{.Tag}}' dima-backend-temiz \
              | sed 's/^s//' | sort -n | tail -1) + 1 ))"
docker build -t "dima-backend-temiz:$ETIKET" backend/ || exit 1   # ← ÖNCE derle
docker rm -f dima-oneri-8002                                      # ← SONRA değiştir
docker run -d --name dima-oneri-8002 -p 8002:8000 --env-file .env \
  -v dima-backend-feat-wren-strict-agentic_dima_logs:/app/logs \
  -v dima-backend-feat-wren-strict-agentic_dima_hf_cache:/tmp/fastembed_cache \
  "dima-backend-temiz:$ETIKET"
curl --retry 60 --retry-delay 2 --retry-all-errors --retry-connrefused \
     -s -o /dev/null -w '%{http_code}\n' localhost:8002/health      # → 200
```

🔴 **Sıra bağlayıcıdır:** `docker rm -f` **derlemeden sonra** gelir. Ters sırada bir kez
backend **çöktü** (derleme düştü, kap yine de silindi). Tam reçete ve kurtarma:
[`belgeler/kilavuz/SERVER_COMMANDS.md`](belgeler/kilavuz/SERVER_COMMANDS.md).

⚠ **`docker-compose up` DENENMEZ** — bu makinedeki compose v1 yeni imaj biçiminde
düşerken **çalışan kabı da durduruyor** (ölçüldü: 40 sn kesinti).

**Frontend:**

```bash
cd dima-frontend-demo-master && pnpm dev      # :3000, hot-reload — tazeleme gerekmez
```

⚠ **Portlar:** `:8002` öngörü/geliştirme kabı · `:8001` ikinci bir kap
(`dima-backend-temiz`). **Bu depo iki geliştirici tarafından paylaşılıyor olabilir** — bir
kabı yeniden başlatmadan önce `docker ps` ile kimin ne koşturduğuna bak.

---

## 4 · İlk gün: okuma sırası

| # | dosya | ne öğrenirsin | süre |
|---|---|---|---|
| 1 | **`backend/CLAUDE.md`** | en üst kural (garson devri) · değişmezler · **test kapısı politikası** | 20 dk |
| 2 | **`backend/MIMARI.md` `§0`** | cevaplama merdiveni · katmanlar · **ne YAPILMAYACAĞI** · ADR listesi | 30 dk |
| 3 | [`belgeler/00-INDEKS.md`](belgeler/00-INDEKS.md) | belgelerin **yerleşim kuralı** — nerede ne durur | 5 dk |
| 4 | **nerede kaldık** (§5) | açık işler, ölçüm tabanı, borçlar | 15 dk |
| 5 | [`belgeler/kilavuz/TEST-ORTAMI-KILAVUZU.md`](belgeler/kilavuz/TEST-ORTAMI-KILAVUZU.md) | testi **nasıl** koşarsın (süre kuralları!) | 10 dk |

⚠ **Çelişkide `backend/MIMARI.md` kazanır.** `belgeler/devir/*` tarihsel kayıttır,
`belgeler/urun/*` şartnamedir — **mimari otorite değildirler**.

---

## 5 · «Nerede kaldık» hangi dosyada

Bu depoda **operasyon** denen şey, tek plana bağlı bir çalışma dönemidir; her operasyonun
bir **durum** dosyası vardır ve bağlam sıfırlansa bile iş oradan devam eder.

| operasyon | plan | durum (**nerede kaldık**) |
|---|---|---|
| 🔴 **öngörü katmanı** *(en son çalışılan)* | `belgeler/plan/2026-08-12_ONGORU-KATMANI-KARARI.md` | **`belgeler/plan/ONGORU-DURUM.md`** |
| ⟳ v1 yol haritası *(kapandı, kayıt)* | `belgeler/plan/DIMA-V1-YOL-HARITASI.md` | `OPERASYON-DURUM.md` |

⚠ Kök `OPERASYON*.md` üçlüsü **önceki** operasyonundur ve hâlâ oradadır (*kapananlar
işaretlenir, silinmez*). En son durumu arıyorsan **`ONGORU-DURUM.md`**'ye bak; teslim
özeti için `belgeler/devir/` altındaki **en yeni** `HANDOFF_*`.

---

## 6 · Dokunulmazlar — bunlara dokunmadan önce sor

`MIMARI §38.4`'ün listesi; her biri **ölçülmüş bir kazadan** doğdu:

* **LLM küp yolunda SQL yazmaz** · **sayıyı küp koyar** · grafik kararı deterministik
* **kapalı fiil kümesi** (plan fiilleri bir `enum`'dur, serbest metin değil)
* `narration_guard` — eşleşmeyen sayı taşıyan cümle **yayımlanmaz**
* **beyan kültürü**: yapılamayan şey **söylenir** (sessiz yutma yok — `ADR-0020`)
* **Türkçe morfoloji** kuralları `cube_router`'a **eklenmez** — anlaşılmayan cümle
  garsona **devredilir**
* `KURAL B` (bayrak kapalıyken davranış **bayt bayt** aynı) · `KAT-1` (bir kararın **tek**
  sahibi) · motor **in-process** · `E-8` (sıcak yolda seri ikinci LLM turu yok)

---

## 7 · Test disiplini — üç seviye, başkası yok

| ne zaman | komut | süre |
|---|---|---|
| bir dosya düzenledin | `pytest -q tests/test_X.py` (hedefli, **kapı değil**) | 3-15 sn |
| **tüm** düzeltmeler bitti | `python lab/kapi.py --hizli --degisen <dosyalar>` | ~1-2 dk |
| demet sonu | `python lab/kapi.py --tam` → **korpus** | ~2 dk |

🔴 **Kapı TOPLU koşulur.** Ölçüldü: beş kök için beş ayrı kapı ≈ **35 dk**, aynı beşi tek
koşumla **7 dk** — *beş kat maliyet, sıfır ek bilgi*.

**Konteyner kalıbı** (repoya yazan her koşumda `--user` **zorunlu**):

```bash
docker run -d --name X$$ --network none \
  -v "$PWD/backend:/app" -v "$PWD/belgeler:/belgeler:ro" \
  -v "$PWD/dima-frontend-demo-master:/dima-frontend-demo-master:ro" \
  -w /app --user "$(id -u):$(id -g)" -e DIMA_VQR_EMBEDDER=off \
  dima-test python -m pytest -q -p no:randomly tests/test_X.py
docker wait X$$ && docker logs X$$ | grep -E 'passed|FAILED'   # sonra: docker rm -f
```

⚠ **`belgeler` mount'u olmadan iki yayın kapısı sessizce ATLANIR** (`skipped` diye, yani
*iyi haber* gibi). Belge düzeni kapısı ise **repo kökünü** ister:
`-v "$PWD:/repo" -w /repo/backend`.

---

## 8 · Yeni gelenin ilk gün çarpacağı beş şey

| # | tuzak | doğrusu |
|---|---|---|
| 1 | *«düzelttim ama değişmedi»* | kaynak konteynere bind-mount **edilmiyor** → **yeniden derle** |
| 2 | *«testler yeşil, ürün bozuk»* | korpus `route()`'u ölçer; **Discovery ve HTTP uçlarını görmez** — canlı `curl` asıl kanıttır |
| 3 | *«kapı yeşil»* ama `skipped` | mount eksikse kapı **atlar**; `skipped` bir onay değildir |
| 4 | ilk istek çok yavaş | öneri indeksi açılışta **~50 sn** ısınır; o pencerede leksik cevap verilir (bir arıza değil) |
| 5 | belge nereye yazılır | [`belgeler/00-INDEKS.md`](belgeler/00-INDEKS.md) — *yeri belli olmayan bir belge kökte birikir* |

---

## 9 · Bir şey bozulduğunda

```bash
docker logs dima-oneri-8002 2>&1 | tail -40                      # ne oldu
docker logs dima-oneri-8002 2>&1 | grep -A 12 'best-effort'      # YUTULMUŞ istisna
```

🔴 Bu depoda ölçülmüş bir kusur sınıfı var: *«koşar · log basar · **hiçbir şey yapmaz**»* —
bir dal ateşlenir, kütüğe yazar, ama dış `except` istisnayı yutar ve kullanıcı eski
davranışı görür. **Kütüğün yazması, işin yapıldığı anlamına gelmez.**

---

*Daha fazlası: `backend/README.md` (uç listesi ve kurulum ayrıntısı) ·
`backend/MIMARI.md` (mimari otorite) · [`belgeler/00-INDEKS.md`](belgeler/00-INDEKS.md)
(tüm belgeler).*
