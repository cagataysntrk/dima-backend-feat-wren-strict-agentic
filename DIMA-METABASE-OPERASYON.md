# DIMA + METABASE — OPERASYON SÖZLEŞMESİ

> 🔴 Bu dosya `feat/dima-metabase-platform` geliştirme hattının çalışma protokolüdür.
> `feat/ask-v2-mvp` ayrı geliştirici tarafından yürütülen **READ-ONLY SOURCE REFERENCE**'tır.
> Bu operasyon kaynak branche hiçbir write yapmaz.

## 1. Otorite sırası

Çelişkide üstteki belge kazanır:

1. `backend/belgeler/metabase/DIMA_METABASE_NIHAI_FIZIBILITE_VE_MIMARI_RAPORU.md` — mühürlü normatif mimari.
2. `backend/belgeler/metabase/DIMA_METABASE_NIHAI_UYGULAMA_YOL_HARITASI.md` — mühürlü geliştirme/gate sırası.
3. `backend/belgeler/metabase/DIMA_METABASE_SOURCE_LOCK.md` — source/base/runtime pinleri.
4. `DIMA-METABASE-OPERASYON.md` — nasıl çalışılır.
5. `DIMA-METABASE-DENETIM.md` — zorunlu denetimler.
6. `DIMA-METABASE-DURUM.md` — nerede kaldık.
7. Failure/Decision receipts ve test/CI kanıtları.

Eski taslaklar veya ask-v2'nin hareketli living dokümanları bu branch için normatif değildir.

## 2. Mutlak branch izolasyonu

Her GitHub write işleminden önce hedef branch explicit olarak `feat/dima-metabase-platform` olmalıdır.

Yasak:
- `feat/ask-v2-mvp` branchine write;
- source branche merge/rebase/cherry-pick;
- source branch HEAD'ini otomatik çekip bu branche merge/rebase etmek;
- moving HEAD üzerinden taban değiştirmek;
- platform branchini source branchin devamı gibi kullanmak.

Source değişiklikleri yalnız **okunabilir**. Gerekli görülen delta için Decision Receipt açılır; owner, invariant, dosya kapsamı ve branch-local proof yazılmadan port edilmez.

## 3. P0 no-product-code kuralı

Bootstrap/gov altyapısı tamamlanmadan ürün geliştirmesi başlamaz.

P0 boyunca izinli:
- mühürlü belgeler,
- source lock,
- status/audit/receipt sistemi,
- branch guard / CI governance,
- yalnız baseline doğrulama araçları.

P1 başlamadan `app/v3/`, Metabase adapterı veya production request routing yazılmaz.

## 4. Her ticket döngüsü

```text
READ       → ilgili P* / M* maddesini ve atıflarını yeniden oku
SCOPE      → tek owner + files-to-touch + files-not-to-touch yaz
MEASURE    → kusuru/boşluğu önce kanıtla
DESIGN     → doğru abstraction; vaka/kelime yaması yok
IMPLEMENT  → yalnız izinli dosyalar
FOCUSED    → provider-free/focused proof
REAL       → gerekiyorsa workers=1 live/sentinel
CLASSIFY   → RED varsa patchten önce failure receipt
RECORD     → test/run/SHA/borç/sonraki adım
COMMIT     → tek coherent ticket
STATUS     → living status güncelle
```

Bir gate kapanmadan sonraki authority-changing milestone'a geçilmez.

## 5. Failure protocol

RED sonrası ürün/semantic patch **yasaktır**; önce:
```text
failure_class
single_owner
root_cause
failure_family
forbidden_patch_alternatives
allowed_files_to_touch
files_not_to_touch
focused_proof
family_proof
```
kaydedilir.

Top-level sınıflar:
`MODEL_COGNITION`, `CONTRACT/ARCHITECTURE`, `RESOLVER_TRUTH`, `EVAL_ORACLE`, `TRANSPORT/PROVIDER`.

Metabase failure_tag ikinci boyuttur; yeni top-level owner yaratmaz.

## 6. Mimari kırmızı çizgiler

- exactly-one semantic authority;
- same-turn Standard XOR Research;
- semantic surface silent loss = 0;
- semantic regex/fuzzy/morphology truth = 0;
- raw-user-language reparse substrate içinde = 0;
- Metabase label/name guessing = 0;
- unapproved implicit FK join = 0;
- raw SQL Manager capability = 0;
- authority/query mismatch = 0;
- silent fallback = 0;
- query handle durable provenance değildir;
- current viewer permission/lens revalidation zorunludur;
- runtime-only security binding lossy ise persistence/replay yasaktır;
- Wren removal yalnız WREN_ONLY_GAP release-critical = 0 veya explicit retain decision sonrası;
- production switch ile code deletion aynı commit olamaz.

## 7. Model ve deterministic plane

LLM:
- language understanding,
- bounded candidate decision,
- temporal language normalization,
- research cognition/orchestration,
- synthesis.

Dima deterministic plane:
- semantic authority,
- capability/security,
- accepted authority,
- relationship approval,
- provenance/evidence,
- completion,
- epistemic promotion.

Metabase:
- analytics/query/BI substrate.

DB:
- numeric truth.

## 8. Test disiplini

Normal geliştirme:
- focused/provider-free;
- gerekiyorsa exact-SHA workers=1 model A/B;
- family/metamorphic proof;
- real substrate sentinel.

Broad suites milestone/final gate'tir; debugging aracı değildir.
DEV80 tam yol haritasındaki final engineering gate'te **bir kez**.

## 9. Commit disiplini

Her commit:
- tek ticket/owner,
- ölçüm/kanıt,
- değişen dosyalar,
- gate sonucu,
- açık borç
ile izlenebilir olmalıdır.

Case-derived prompt, hidden example öğretme, keyword/regex patch veya "çalışıyor gibi" fallback kabul edilmez.

## 10. STOP-THE-LINE

Aşağıdakilerden biri görülürse ilerleme durur:
- ikinci semantic owner;
- silent wrong/silent requirement loss;
- cross-tenant leak;
- ambiguity auto-pick;
- raw schema fallback;
- unapproved implicit join;
- security lens bypass;
- source branch isolation ihlali;
- sealed belge drift'i;
- failure classify edilmeden patch.
