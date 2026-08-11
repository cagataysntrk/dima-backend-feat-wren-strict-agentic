"""FAZ 3.4 — **APACHE OSSIE İTHALİ.** Müşterinin semantik modeli bir `packs/` katmanı olur.

## Neden

Sektörün fiili standardı (eski adı **OSI**, Haziran 2026'da **ASF**'e bağışlandı —
Snowflake · dbt Labs · Databricks · Google · AWS · Cube · AtScale · Qlik + 50 kurum).
YAML üst-yapıları **bizim `packs/` yapımızla neredeyse birebir**.

⚠ **MIMARI §3.4 çelişkisi bilinçli olarak geri alındı:** *"Bilerek ALINMAYANLAR: `osi` —
bugün müşteri senaryosu yok"* deniyordu. Standart o tarihten sonra ASF'e geçti ve ithal
tarafı, **kapsam tavanına küratörlük emeği olmadan saldıran tek kaldıraç**.

## 🔴 ÇEVİRİCİ YAZILIR, MOTOR YAZILMAZ

Hedef şekil **zaten bizimki**. Bu modül bir **eşlemedir**, ikinci bir semantik motor değil:

| Ossie | biz |
|---|---|
| `datasets` | `models` |
| `metrics` | `measures` |
| `fields` (`dimension`) | `dimensions` |
| `relationships` | `relationships.yml` |
| **`ai_context`** | **`synonyms`** |

## 🔴 İTHAL EDİLEN HER ŞEY `olculmedi` DAMGASIYLA GELİR

*İthal bir ilişki, sessiz **"sağlıklı"** değildir.* Fan-out sertifikası **ölçülmediği**
sürece `certified: "olculmedi"` taşır — çünkü bir başkasının modelinin doğru olduğunu
**varsaymak**, bu deponun en pahalı hatasının (sessiz-yanlış) ithal edilmiş hâli olurdu.

## ⚠ ÇEKİRDEK KATMANA İNER, ERP KATMANINA DEĞİL

Aksi hâlde `cari`/`ticaret`'in **dördüncü kopyası** doğardı (FAZ 2.1'in ölçtüğü kusur).

> **Karar kaydı: `ADR-0030`** — Apache Ossie ithal/ihraç — çevirici yazılır, motor yazılmaz.
> ⚠ Atıf, kararın **yaşadığı yere** yazılır: kayıt ile kod birbirini ancak
> böyle doğrulayabilir (`tests/test_adr_dosyalari.py` iki yönü de kilitler).
"""

from __future__ import annotations

from typing import Any

#: Ossie sürümleri — okuduğumuz şema. Bilinmeyen sürüm **reddedilmez**, `uyari` taşır:
#: bir standardın ilerlemesini ithal kapısını kapatarak karşılamak, kapsamı dondururdu.
DESTEKLENEN_SURUMLER = ("0.1", "0.1.1", "0.2")

#: 🔴 **CUSTOM EXTENSIONS ANAHTARI.** Standart, satıcıya özgü alanları burada taşır.
#: *Farkımızı standarda uyarken KAYBETMEK, ithal/ihracın bedeli olamaz:* fan-out
#: sertifikası · `always_filter` · `additive:` · `dimension_origin` — dördü de bizde
#: **sessiz-yanlışı önleyen** alanlar ve hiçbirinin Ossie'de karşılığı yok.
UZANTI = "x-dima"

#: Ossie'nin **kendi** alanlarına eşlenmeyen, ama SQL'i BELİRLEYEN cube alanları.
#: 🔴 Round-trip kapısının tuttuğu liste budur: biri düşerse ihraç edilen model geri
#: ithal edildiğinde **başka bir SQL** üretir ve `ossie_ihrac` açılamaz.
SQL_BELIRLEYEN = ("base_object", "always_filter")

#: 🔴 İthal ilişkilerin fan-out damgası. `test_iliski_sertifikasi`'nin sözlüğüyle **aynı**
#: ad — ikinci bir sertifika sözlüğü yazmak, iki damganın ayrışması demekti.
SERTIFIKA_OLCULMEDI = "olculmedi"


class OssieIthalHatasi(ValueError):
    """İthal **fail-closed** reddedildi. Yarım ithal edilmiş bir model, ithal edilmemiş
    bir modelden **kötüdür**: katalogda görünür ama sayıları kimse doğrulamamıştır."""


def surum_uyarisi(belge: dict[str, Any]) -> str | None:
    """Bilinmeyen sürüm → **uyarı**, ret değil.

    ⚠ Bir standardın ilerlemesini ithal kapısını **kapatarak** karşılamak, kapsamı
    dondururdu. Ama sessiz kalmak da yanlış: eşleme eksik kalabilir ve kullanıcı bunu
    **bilmeli**.
    """
    s = str(belge.get("version") or belge.get("spec_version") or "").strip()
    if not s:
        return "Ossie sürümü belirtilmemiş — eşleme eksik olabilir."
    if not any(s.startswith(v) for v in DESTEKLENEN_SURUMLER):
        return f"Ossie sürümü `{s}` denenmedi (bilinen: {', '.join(DESTEKLENEN_SURUMLER)})."
    return None


def _syn(alan: dict[str, Any]) -> list[str]:
    """`ai_context` → `synonyms`. **Standardın en değerli alanı budur**: kullanıcı
    kelimeleri, küratörlük emeği olmadan gelir.

    ⚠ Serbest metin bir sinonim **değildir**: `ai_context` bir cümle taşıyorsa (boşluklu,
    uzun) sinonim listesine atılmaz — atılsaydı katalog, eşleşmeyen çöp kelimelerle şişer
    ve `_uncovered` kapısı her soruda çekilirdi.
    """
    ham = alan.get("ai_context") or alan.get("aiContext") or []
    if isinstance(ham, str):
        ham = [ham]
    out: list[str] = []
    for x in ham or []:
        s = str(x).strip()
        if s and len(s) <= 40 and s.count(" ") <= 3:
            out.append(s)
    return out


def cevir(belge: dict[str, Any]) -> dict[str, Any]:
    """Ossie belgesi → `packs/` katman sözlüğü. **Saf fonksiyon** — dosya yazmaz.

    Döner: `{"cubes": [...], "relationships": [...], "uyarilar": [...]}`

    🔴 **Fail-closed:** adı olmayan bir dataset/metric **atlanmaz, REDDEDİLİR**. Adsız bir
    şeyi *"varsayılan"* bir adla içeri almak, katalogda kimsenin arayamayacağı bir kayıt
    bırakırdı — ve o kayıt bir gün bir soruya cevap olurdu.
    """
    uyarilar: list[str] = []
    u = surum_uyarisi(belge)
    if u:
        uyarilar.append(u)

    cubes: list[dict[str, Any]] = []
    for ds in belge.get("datasets") or []:
        ad = str((ds or {}).get("name") or "").strip()
        if not ad:
            raise OssieIthalHatasi(
                "adsız `dataset` — ithal REDDEDİLDİ. Adsız bir kaydı 'varsayılan' bir adla "
                "içeri almak, katalogda kimsenin arayamayacağı bir satır bırakırdı.")
        olculer, boyutlar, zamanlar = [], [], []
        for m in ds.get("metrics") or []:
            m_ad = str((m or {}).get("name") or "").strip()
            if not m_ad:
                raise OssieIthalHatasi(f"`{ad}`: adsız `metric` — ithal REDDEDİLDİ.")
            olcu: dict[str, Any] = {"name": m_ad}
            if m.get("expression") or m.get("sql"):
                olcu["expression"] = str(m.get("expression") or m.get("sql"))
            if m.get("label") or m.get("display_name"):
                olcu["label"] = str(m.get("label") or m.get("display_name"))
            if _syn(m):
                olcu["synonyms"] = _syn(m)
            # 🔴 **ROUND-TRIP:** `x-dima` geri okunmazsa ihraç edilen model geri ithal
            # edildiğinde `additive: semi` DÜŞER — ve bir bakiye düz `SUM` edilir. Bu,
            # "sessiz-yanlışı standarda uyarken kaybetmek"in tam tanımıdır.
            for k, v in _uzanti(m).items():
                if v is not None:
                    olcu[k] = v
            olculer.append(olcu)
        for f in ds.get("fields") or []:
            if str((f or {}).get("type") or "").lower() not in ("dimension", "", "field"):
                continue
            f_ad = str((f or {}).get("name") or "").strip()
            if not f_ad:
                raise OssieIthalHatasi(f"`{ad}`: adsız `field` — ithal REDDEDİLDİ.")
            boyut: dict[str, Any] = {"name": f_ad}
            if _syn(f):
                boyut["synonyms"] = _syn(f)
            if f.get("label"):
                boyut["label"] = str(f["label"])
            ek = _uzanti(f)
            # ⚠ `veri_tipi` → `type`: Ossie'de `type` zaten "dimension|metric" ayrımını
            # tutuyor; ikisini aynı anahtara yazmak boyutu `VARCHAR` yerine `dimension`
            # tipli sanmak demekti (round-trip kapısı bunu yakalar).
            if ek.get("veri_tipi") is not None:
                boyut["type"] = ek.pop("veri_tipi")
            rol = ek.pop("rol", None)
            for k, v in ek.items():
                if v is not None:
                    boyut[k] = v
            # ⚠ Rol `x-dima`'dan geri okunur; okunmazsa cube derlenir ama **zaman
            # sorgusu çalışmaz** — sessiz değil ama GEÇ patlayan bir kusur.
            (zamanlar if rol == "time" else boyutlar).append(boyut)
        cube: dict[str, Any] = {
            "name": ad,
            "base_object": str(ds.get("table") or ds.get("source") or ad),
            "measures": olculer,
            "dimensions": boyutlar,
            # 🔴 İTHAL DAMGASI — kaynağı gizlemek, bir gün "bu cube nereden geldi"
            # sorusunu cevapsız bırakırdı.
            "ithal_kaynak": "ossie",
        }
        if zamanlar:
            cube["time_dimensions"] = zamanlar
        if _syn(ds):
            cube["synonyms"] = _syn(ds)
        if ds.get("label"):
            cube["label"] = str(ds["label"])
        for k, v in _uzanti(ds).items():
            if v is not None:
                cube[k] = v
        cubes.append(cube)

    iliskiler = []
    for r in belge.get("relationships") or []:
        ad = str((r or {}).get("name") or "").strip()
        if not ad:
            raise OssieIthalHatasi("adsız `relationship` — ithal REDDEDİLDİ.")
        iliskiler.append({
            "name": ad,
            "models": list(r.get("datasets") or r.get("models") or []),
            "join_type": str(r.get("type") or r.get("join_type") or "MANY_TO_ONE"),
            "condition": str(r.get("condition") or r.get("on") or ""),
            # 🔴 FAN-OUT SERTİFİKASI **ÖLÇÜLMEDİ**. İthal bir ilişki, sessiz "sağlıklı"
            # DEĞİLDİR: bir başkasının modelinin doğru olduğunu VARSAYMAK, bu deponun en
            # pahalı hatasının (sessiz-yanlış) ithal edilmiş hâli olurdu.
            # ⚠ Belge bir sertifika BEYAN ediyorsa o taşınır (round-trip); beyan YOKSA
            # `olculmedi` — varsayılanı "ok" yapmak, sessiz-yanlışı ithal etmek olurdu.
            "certified": _uzanti(r).get("certified") or r.get("certified")
                         or SERTIFIKA_OLCULMEDI,
        })

    return {"cubes": cubes, "relationships": iliskiler, "uyarilar": uyarilar}


def _uzanti(x: dict[str, Any]) -> dict[str, Any]:
    """`x-dima` bloğunu okur — hem `x-dima` hem `x_dima` yazımını kabul eder.

    ⚠ Yokluğu bir hata **değildir**: başka bir satıcının ürettiği Ossie belgesinde bu blok
    olmaz ve olmaması ithali engellememeli. *Standardın tamamını isteyen bir ithal kapısı,
    standardı olan hiç kimseyi içeri almaz.*
    """
    return dict(x.get(UZANTI) or x.get("x_dima") or {})


def _pack_sekline_getir(cube: dict[str, Any]) -> dict[str, Any]:
    """🔴 `§F6` — **İKİ ŞEKİL VARDI VE İHRAÇ UCU YANLIŞ OLANI BESLİYORDU.**

    ## Ölçülen kusur (2026-08-11, canlı katalog)

    `GET /connections/{cid}/ossie` gövdesi şunu yapar:

        sema = wren_for_request(request).schema()
        return {..., **belge(sema.get("cubes") or [], ...)}

    Ama `schema()` cube'ları **düzleştirir** — `measures: ["ort_oee", …]` (dizeler),
    sözlükler ise `measure_synonyms` / `measure_expressions` / `measure_labels`
    anahtarlarında **ayrı** durur. `disa_aktar` ise `packs/` şeklini bekliyordu:
    `measures: [{name, expression, synonyms}, …]`. Sonuç, canlı şemada:

        AttributeError: 'str' object has no attribute 'get'   → HTTP 500

    🔴 **Ve round-trip kapısı bunu GÖREMEDİ**, çünkü fikstürü `packs/` şeklinde yazılmış:
    yani kural yazılmış, uç bağlanmış, kapı kurulmuş — **ve kapı, ucun hiç görmediği bir
    şekli sınıyordu.** Bu deponun avladığı sınıfın en sinsi biçimi: *beyan ile kodun
    ayrışması*, üstelik bir testin arkasına saklanmış hâli.

    ## Neden NORMALİZE, ikinci bir ihracatçı değil

    İki `disa_aktar` yazmak (biri pack, biri şema) `KAT-1` ihlali olurdu ve iki ihracat
    zamanla iki farklı Ossie belgesi üretirdi. Şekil çevirisi **tek yerde**, ihracatın
    kapısında durur; `disa_aktar`ın gövdesi **hiç değişmedi**.

    ⚠ Zaten-pack olan girdi **dokunulmadan** geçer (idempotent): ölçü listesi sözlük
    taşıyorsa çeviri yapılmaz. *Bir normalleştirici, normalleştirdiğini bozmamalıdır.*
    """
    olculer = cube.get("measures") or []
    if not olculer or not all(isinstance(m, str) for m in olculer):
        return cube                      # zaten `packs/` şekli (ya da boş) → dokunma

    # ⚠ Anahtar adları **ölçüldü, tahmin edilmedi** (canlı `schema()` dökümü, 2026-08-11):
    # üç tahminim yanlıştı — `measure_labels` **yok** (etiket `measure_synonyms_display`
    # altında), küp etiketi `label` değil **`display`**, ve `non_additive` `semi_additive`ten
    # **ayrı bir liste**. *Bir şema çevirisi, şemayı okumadan yazılamaz.*
    syn = cube.get("measure_synonyms") or {}
    ifade = cube.get("measure_expressions") or {}
    birim = cube.get("units") or {}
    yari, toplanamaz = set(cube.get("semi_additive") or []), set(cube.get("non_additive") or [])
    kiyaslanamaz = set(cube.get("kiyaslanamaz") or [])

    def _olcu(ad: str) -> dict[str, Any]:
        k: dict[str, Any] = {"name": ad}
        for anahtar, kaynak in (("expression", ifade), ("unit", birim), ("synonyms", syn)):
            if kaynak.get(ad):
                k[anahtar] = kaynak[ad]
        # ⚠ `semi`/`non` DÜŞÜRÜLEMEZ: bir bakiyeyi düz `SUM` etmek, bir oranı toplamak
        # **güvenle yanlış** sayı üretir ve Ossie'de karşılığı yok — `x-dima` şart.
        if ad in yari:
            k["additive"] = "semi"
        elif ad in toplanamaz:
            k["additive"] = "non"
        if ad in kiyaslanamaz:
            k["kiyaslanamaz"] = True
        return k

    d_syn = cube.get("dimension_synonyms") or {}
    d_etiket = cube.get("dimension_labels") or {}
    koken = cube.get("dimension_origin") or {}
    z_ifade = cube.get("time_dimension_expressions") or {}

    def _boyut(ad: str, zaman: bool = False) -> dict[str, Any]:
        k: dict[str, Any] = {"name": ad}
        if d_etiket.get(ad):
            k["label"] = d_etiket[ad]
        if d_syn.get(ad):
            k["synonyms"] = d_syn[ad]
        if zaman and z_ifade.get(ad):
            k["expression"] = z_ifade[ad]
        if koken.get(ad):
            # `dimension_origin` fan-out riskinin tek kanıtı — ihraçta düşemez (`§F3`).
            k["properties"] = {"origin": koken[ad]}
        return k

    out = {**cube,
           "measures": [_olcu(m) for m in olculer],
           "dimensions": [_boyut(d) for d in (cube.get("dimensions") or [])
                          if isinstance(d, str)],
           "time_dimensions": [_boyut(t, zaman=True)
                               for t in (cube.get("time_dimensions") or [])
                               if isinstance(t, str)]}
    if not out.get("label") and cube.get("display"):
        out["label"] = str(cube["display"])
    return out


def disa_aktar(cube: dict[str, Any]) -> dict[str, Any]:
    """`packs/` cube'u → **Ossie `dataset`**. Saf fonksiyon — dosya yazmaz.

    ## 🔴 FARKIMIZ `Custom Extensions` İÇİNDE

    Ossie `metrics`/`fields`/`ai_context`'i taşır; **sessiz-yanlışı önleyen alanlarımızın
    hiçbirini taşımaz**. Onları `x-dima` altına koyuyoruz:

    | alan | neden kaybolamaz |
    |---|---|
    | `additive` | `semi` bir bakiyeyi düz `SUM` etmek **güvenle yanlış** sayı üretir |
    | `always_filter` | iptal kaydı sızıntısını **yapısal** önler; düşerse sayı sessizce şişer |
    | `dimension_origin` | boyut hangi join'den geldi — fan-out riskinin tek kanıtı |
    | `certified` | ilişki fan-out açısından ölçüldü mü; **varsayım = sessiz-yanlış** |

    ⚠ **İhraç bir OKUMA işlemidir** — `packs/` hiç etkilenmez. Geri alma (`ossie_ihrac=off`)
    yalnız ucu kapatır; bu fonksiyonun ürettiği belge zaten hiçbir yere yazılmaz.
    """
    cube = _pack_sekline_getir(cube)
    ad = str(cube.get("name") or "").strip()
    if not ad:
        raise OssieIthalHatasi(
            "adsız cube ihraç EDİLEMEZ — adsız bir dataset, geri ithal edildiğinde "
            "reddedilirdi (round-trip kapısı bunu yakalar).")

    metrics = []
    for m in cube.get("measures") or []:
        m_ad = str((m or {}).get("name") or "").strip()
        if not m_ad:
            raise OssieIthalHatasi(f"`{ad}`: adsız ölçü ihraç EDİLEMEZ.")
        kayit: dict[str, Any] = {"name": m_ad}
        if m.get("expression"):
            kayit["expression"] = str(m["expression"])
        if m.get("label"):
            kayit["label"] = str(m["label"])
        if m.get("synonyms"):
            kayit["ai_context"] = [str(x) for x in m["synonyms"]]
        ek = {k: m[k] for k in ("additive", "unit", "type", "kiyaslanamaz")
              if m.get(k) is not None}
        if ek:
            kayit[UZANTI] = ek
        metrics.append(kayit)

    fields = []
    # 🔴 **Kapı bunu yakaladı.** `time_dimensions` cube metadata'sında **AYRI bir üst-düzey
    # anahtardır** ve ilk sürüm onu hiç görmüyordu: round-trip'te zaman boyutu düşüyor,
    # motor *"Unknown time dimension"* diyor ve aynı `cube_query` **derlenemez** hâle
    # geliyordu. Ossie'de böyle bir ayrım yok → rol `x-dima`'da taşınır.
    zaman_adlari = {str((d or {}).get("name") or "")
                    for d in (cube.get("time_dimensions") or [])}
    for d in list(cube.get("dimensions") or []) + list(cube.get("time_dimensions") or []):
        d_ad = str((d or {}).get("name") or "").strip()
        if not d_ad:
            raise OssieIthalHatasi(f"`{ad}`: adsız boyut ihraç EDİLEMEZ.")
        kayit = {"name": d_ad, "type": "dimension"}
        if d.get("label"):
            kayit["label"] = str(d["label"])
        if d.get("synonyms"):
            kayit["ai_context"] = [str(x) for x in d["synonyms"]]
        ek = {k: d[k] for k in ("expression", "properties") if d.get(k) is not None}
        # ⚠ Boyutun VERİ TİPİ `type:` alanında değil uzantıda taşınır: Ossie'de `type`
        # zaten "dimension|metric" ayrımını tutuyor. İkisini aynı anahtara yazmak,
        # geri ithalde boyutu `VARCHAR` yerine `dimension` tipli sanmak demekti.
        if d.get("type"):
            ek["veri_tipi"] = d["type"]
        if d_ad in zaman_adlari:
            ek["rol"] = "time"
        if ek:
            kayit[UZANTI] = ek
        fields.append(kayit)

    ds: dict[str, Any] = {
        "name": ad,
        "table": str(cube.get("base_object") or ad),
        "metrics": metrics,
        "fields": fields,
    }
    if cube.get("label"):
        ds["label"] = str(cube["label"])
    if cube.get("synonyms"):
        ds["ai_context"] = [str(x) for x in cube["synonyms"]]
    ek_cube = {k: cube[k] for k in ("always_filter", "alwaysFilter", "pvm")
               if cube.get(k) is not None}
    if ek_cube:
        ds[UZANTI] = ek_cube
    return ds


def belge(cubes: list[dict[str, Any]], *,
          iliskiler: list[dict[str, Any]] | None = None,
          surum: str = "0.2") -> dict[str, Any]:
    """Cube listesi → tam **Ossie belgesi**. `cevir()`'in tersidir (round-trip)."""
    out: dict[str, Any] = {
        "version": surum,
        "datasets": [disa_aktar(c) for c in cubes or []],
    }
    if iliskiler:
        out["relationships"] = [
            {"name": str(r.get("name") or ""),
             "datasets": list(r.get("models") or r.get("datasets") or []),
             "type": str(r.get("join_type") or r.get("type") or "MANY_TO_ONE"),
             "condition": str(r.get("condition") or r.get("on") or ""),
             # ⚠ Sertifika damgası ihraçta da TAŞINIR: `olculmedi` bir eksiklik değil,
             # bir BEYANDIR — dışarı verirken düşürmek, karşı tarafa "ölçüldü" demektir.
             UZANTI: {"certified": r.get("certified") or SERTIFIKA_OLCULMEDI}}
            for r in iliskiler]
    return out
