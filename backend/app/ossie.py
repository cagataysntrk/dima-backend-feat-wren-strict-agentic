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
"""

from __future__ import annotations

from typing import Any

#: Ossie sürümleri — okuduğumuz şema. Bilinmeyen sürüm **reddedilmez**, `uyari` taşır:
#: bir standardın ilerlemesini ithal kapısını kapatarak karşılamak, kapsamı dondururdu.
DESTEKLENEN_SURUMLER = ("0.1", "0.1.1", "0.2")

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
        olculer, boyutlar = [], []
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
            boyutlar.append(boyut)
        cube: dict[str, Any] = {
            "name": ad,
            "base_object": str(ds.get("table") or ds.get("source") or ad),
            "measures": olculer,
            "dimensions": boyutlar,
            # 🔴 İTHAL DAMGASI — kaynağı gizlemek, bir gün "bu cube nereden geldi"
            # sorusunu cevapsız bırakırdı.
            "ithal_kaynak": "ossie",
        }
        if _syn(ds):
            cube["synonyms"] = _syn(ds)
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
            "certified": SERTIFIKA_OLCULMEDI,
        })

    return {"cubes": cubes, "relationships": iliskiler, "uyarilar": uyarilar}
