"""Evrensel çıktı yorumlama — her grafik/tablo/rapor/KPI için data-güdümlü yorum.

İLKE (min-LLM + veri egemenliği): analiz TAMAMEN DETERMİNİSTİK (Python) — en yüksek/düşük,
% değişim, trend yönü, pay, tepe/dip dönem. LLM aritmetik YAPMAZ; opsiyonel anlatım katmanı
yalnız buradaki küçük FACT sözlüğünü cümleye döker (ham satırlar LLM'e GİTMEZ → KVKK).

Çıktı tipini result'ın kolonlarından çıkarır (cube_query/kpi ipucu varsa kullanır); böylece
cube raporu, blend, serbest-SQL, KPI — hepsi aynı motordan geçer. Şablon-tabanlı Türkçe özet
LLM'siz üretilir; LLM sonradan "cilalama" olarak eklenebilir (interpret_llm hook)."""

from __future__ import annotations

import datetime as _dt
from typing import Any

_DATE_NAMES = {"tarih", "ay", "yil", "yıl", "hafta", "gun", "gün", "ceyrek", "çeyrek",
               "donem", "dönem", "date", "month", "year", "week", "day", "quarter", "period"}
_MONTHS_TR = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def _is_num(v: Any) -> bool:
    """Gövdesi `app/result_shape.py`'de (Faz C2) — yedi kopya, üç farklı semantik vardı."""
    from app.result_shape import is_num

    return is_num(v)


def _num(v: Any) -> float:
    s = str(v).strip()
    return float(s.replace(".", "").replace(",", ".") if "," in s else s)


def _fmt(v: Any, unit: str | None = None) -> str:
    """Gövdesi `app/fmt.py`'de (Faz C2). Eskiden `abs(n) >= 100` iken ondalığı ATIYORDU —
    `150,5 → "150"`. Aynı sayı e-postada `150,50` görünüyordu; kullanıcı aynı raporu iki
    yüzeyde farklı okuyordu. Kesirli kısmı sessizce atmak, "gösterilen sayı gerçek sayıdır"
    garantisini bozar."""
    from app.fmt import olcu

    return olcu(v, unit)


def _fmt_bucket(v: Any) -> str:
    """Gövdesi `app/fmt.py`'de (Faz C2) — ay kısaltmaları üç yerde ayrı tanımlıydı."""
    from app.fmt import kova

    return kova(v)


def _classify(columns: list[str], rows: list[dict],
              cube_query: dict | None = None) -> tuple[list[str], list[str], str | None]:
    """Kolon rolleri — gövdesi `app/result_shape.py`'de (Faz C1).

    ÖNEMLİ DEĞİŞİKLİK: artık `cube_query` OTORİTESİNİ kullanıyor. Eskiden saf değer-tabanlıydı
    ve `interpret()` `cube_query`'yi alıyor olmasına rağmen yalnız `measures` süzgeci için
    kullanıyordu; `dimensions`/`timeDimensions` bilgisini GÖRMEZDEN geliyordu. Sonuç:
    sayısal değerli bir boyut (ay numarası, vardiya no, yıl) ÖLÇÜ sanılıyor ve anlatım
    onun "ortalamasını" bir metrik gibi sunuyordu.
    """
    from app.result_shape import authority_from_cube_query, classify as _rol

    dim_cols, time_hint = authority_from_cube_query(cube_query)
    return _rol(columns, rows, dim_cols=dim_cols, time_col_hint=time_hint)


def _tone(pct: float, lib: bool) -> str:
    """Değer yargısı — YALNIZ yönü BİLİNEN (lower_is_better işaretli) ölçüde. Aksi halde
    boş (adet gibi nötr ölçüde 'yüksek=iyi' varsaymayız → yanıltmayız). lib=düşük iyi:
    artış olumsuz, azalış iyileşme."""
    if not lib or -1 <= pct <= 1:
        return ""
    return " — olumsuz (yükseldi)" if pct > 1 else " — iyileşti (düştü)"


def _series_facts(rows: list[dict], time_col: str, measure: str, unit: str | None,
                  lib: bool = False, _ad=lambda k: k) -> list[dict]:
    """Zaman serisi: ilk→son % değişim, yön (+lower_is_better ise iyi/kötü çerçeve), tepe/dip."""
    pts = [(str(r[time_col]), _num(r[measure])) for r in rows
           if r.get(time_col) is not None and r.get(measure) is not None]
    pts.sort(key=lambda p: p[0])
    if len(pts) < 2:
        return []
    first, last = pts[0], pts[-1]
    hi = max(pts, key=lambda p: p[1])
    lo = min(pts, key=lambda p: p[1])
    facts = []
    if first[1]:
        pct = (last[1] - first[1]) / abs(first[1]) * 100
        yon = "arttı" if pct > 1 else "azaldı" if pct < -1 else "yatay seyretti"
        facts.append({"type": "trend", "measure": measure, "pct": round(pct, 1),
                      "favorable": (None if not lib or -1 <= pct <= 1 else pct < -1),
                      "text": f"{_ad(measure)}: {_fmt_bucket(first[0])}→{_fmt_bucket(last[0])} "
                              f"%{abs(round(pct, 1))} {yon} "
                              f"({_fmt(first[1], unit)} → {_fmt(last[1], unit)}){_tone(pct, lib)}"})
    facts.append({"type": "peak", "measure": measure,
                  "text": f"En yüksek {_fmt_bucket(hi[0])} ({_fmt(hi[1], unit)}), "
                          f"en düşük {_fmt_bucket(lo[0])} ({_fmt(lo[1], unit)})"})

    # 🔴 FAZ 5.5 — **DELTA (mutlak + %)**. `trend` yalnız **yüzde** taşıyordu; mutlak
    # fark başlıkta hiç görünmüyordu. *"%12 arttı"* bir yön verir, **"+1,4 milyon ₺"**
    # bir büyüklük verir — ve iş kararı büyüklükle alınır. İkisi ayrı fact'tir çünkü
    # `trend` bir **anlatı** cümlesidir, `delta` bir **başlık kartıdır**.
    facts.append({"type": "delta", "measure": measure,
                  "mutlak": round(last[1] - first[1], 4),
                  "pct": round((last[1] - first[1]) / abs(first[1]) * 100, 1)
                         if first[1] else None,
                  "favorable": (None if not lib else (last[1] - first[1]) < 0),
                  "text": f"Δ {_ad(measure)}: {_fmt(last[1] - first[1], unit)}"
                          + (f" (%{abs(round((last[1] - first[1]) / abs(first[1]) * 100, 1))})"
                             if first[1] else "")})

    st = _streak(pts, lib)
    if st:
        facts.append(st | {"measure": measure})
    return facts


def _streak(pts: list[tuple[str, float]], lib: bool = False) -> dict | None:
    """🔴 FAZ 5.5 — **ARDIŞIK AYNI-YÖNLÜ DÖNEM (streak).**

    ## Ölçülen boşluk

    `_series_facts` yalnız **ilk↔son** kıyaslıyordu; **aradaki zikzak görünmüyordu**.
    *"Ocak 100 → Haziran 110"* ile *"Ocak 100 → beş ay boyunca düşüş → Haziran 110"*
    aynı fact'i üretiyordu. Oysa ikincisi **bambaşka bir hikâyedir**: *"3 aydır
    düşüyor"* bir yön değil bir **kalıptır** ve iş kararını o kalıp verir.

    ## 🔴 `n < 3` → ÜRETİLMEZ

    İki dönemlik bir "seri" bir kalıp değildir, bir **farktır** — ve onu `delta` zaten
    söylüyor. Üçün altında streak yazmak, gürültüyü kalıp diye satmak olurdu.

    ## ⚠ KISMİ SON DÖNEM DIŞLANIR (Tableau *"Ignore Last"*)

    İçinde bulunduğumuz ay **henüz bitmedi**: 5 Ağustos'ta Ağustos kovası ayın yalnız
    beşte birini taşır ve **her zaman düşük** görünür. Onu seriye katmak, her raporda
    sahte bir *"düşüyor"* streak'i üretirdi — **sistematik ve sessiz** bir yanlış.
    Bu yüzden son nokta, seri **bugünü içeren dönemdeyse** düşürülür.

    ⚠ Dışlama **son noktayı silmez, streak'ten çıkarır**: `trend`/`peak`/`delta` onu
    görmeye devam eder. *Bir kuralı bir fact'e uygulamak, hepsine uygulamak demek
    değildir.*
    """
    seri = _kismi_donemi_dus(pts)
    if len(seri) < 3:
        return None
    # ⚠ **SONDAN GERİYE** sayılır, baştan değil: kullanıcı **şu anki** kalıbı sorar
    # (*"3 aydır düşüyor"*), tarihin başındakini değil. Baştan saymak, altı ay önce
    # bitmiş bir eğilimi bugünün hikâyesi gibi anlatırdı.
    uzunluk, son_yon = 1, 0
    for onceki, simdi in zip(reversed(seri[:-1]), reversed(seri[1:])):
        d = simdi[1] - onceki[1]
        adim = 1 if d > 0 else -1 if d < 0 else 0
        # ⚠ Düz (`d == 0`) bir adım zinciri **kırar**: *"3 dönemdir düşüyor"* derken
        # aradaki yatay bir dönemi saymak, olmayan bir kalıp anlatmaktır.
        if adim == 0 or (son_yon and adim != son_yon):
            break
        son_yon = adim
        uzunluk += 1
    # 🔴 `n < 3` → üretilmez: iki dönemlik bir "seri" bir kalıp değil bir **farktır**
    # ve onu `delta` zaten söylüyor.
    if uzunluk < 3 or son_yon == 0:
        return None
    artiyor = son_yon > 0
    return {
        "type": "streak", "donem": uzunluk, "artiyor": artiyor,
        "favorable": (None if not lib else not artiyor),
        "text": f"{uzunluk} dönemdir aralıksız "
                + ("artıyor" if artiyor else "düşüyor"),
    }


def _kismi_donemi_dus(pts: list[tuple[str, float]]) -> list[tuple[str, float]]:
    """⚠ **Tableau *"Ignore Last"*.** Son kova **bugünü içeriyorsa** düşürülür.

    🔴 Karşılaştırma **metin öneki** üzerinden yapılır (`2026-08` ⊂ `2026-08-05`) çünkü
    kova etiketi granülerliğe göre değişir (`2026`, `2026-08`, `2026-08-05`, `2026-W32`).
    Tarih ayrıştırmak, ay/hafta kovasını **gün** sanmaya açık olurdu.
    """
    from datetime import date

    if not pts:
        return []
    bugun = date.today().isoformat()
    son = str(pts[-1][0])[:10]
    if son and bugun.startswith(son[:len(son)]):
        return pts[:-1]
    return pts


def _donem_bazinda_topla(rows: list[dict], time_col: str, measure: str) -> list[dict]:
    """Pivot satırlarını **döneme göre** toplar → dönem başına TEK satır.

    🔴 Bu fonksiyon canlı bir kullanıcı turunda bulunan bir **sessiz-yanlıştan** doğdu.
    `_series_facts` satır başına bir nokta alıyordu; `makine × ay` pivotunda aynı ay
    onlarca kez tekrarlanıyor ve *"ilk→son"* aslında **rastgele iki makinenin** değerini
    kıyaslıyordu. Sonuç: aynı veri için üç ayrı tur → **+%88,1 · −%72,3 «iyileşti» ·
    +%98,3**. Kullanıcının kendi cümlesi: *"o andan sonra özet satırını okumayı bıraktım,
    ki bu ürünün en değerli parçası olmalıydı."*

    Trend bir **dönem** ifadesidir; dönemin içindeki kırılım önce toplanmalıdır.
    """
    toplam: dict[str, float] = {}
    for r in rows:
        d = r.get(time_col)
        if d is None or r.get(measure) is None:
            continue
        toplam[str(d)] = toplam.get(str(d), 0.0) + _num(r[measure])
    return [{time_col: d, measure: v} for d, v in sorted(toplam.items())]


def _rank_facts(rows: list[dict], dim: str, measure: str, unit: str | None,
                toplanabilir: bool = True, _ad=lambda k: k) -> list[dict]:
    """Kategorik top-N: en yüksek varlık + (toplanabilirse) payı, en düşük, kalem sayısı.

    🔴 **Toplanamayan ölçüde TOPLAMA YAPILMAZ.** İlk düzeltme yalnız *"toplamın %X'i"*
    payını susturmuştu ama gövde **hâlâ topluyordu**: bir dim değeri için birden fazla
    satır varsa (ör. `makine × renk`, `dims[0]="makine"`) ekrana basılan
    *"En yüksek makine: RAM-1 (…)"* bir **oranlar toplamıydı** — payı susturulmuş ama
    kendisi yanlış bir sayı. Denetimde bulundu. Artık: toplanamayan ölçüde dim başına
    birden fazla satır varsa **sıralama hiç yazılmaz**, nedeni yazılır."""
    ham: dict[str, list[float]] = {}
    for r in rows:
        if r.get(dim) is not None and r.get(measure) is not None:
            ham.setdefault(str(r[dim]), []).append(_num(r[measure]))
    if not ham:
        return []
    if not toplanabilir and any(len(v) > 1 for v in ham.values()):
        return [{"type": "shape",
                 "text": f"{len(ham)} {dim} için birden fazla satır var — sıralama "
                         f"YAZILMADI: {measure} bu kırılım boyunca TOPLANAMAZ, "
                         "parçaların toplamı bütünü vermez"}]
    agg: dict[str, float] = {k: sum(v) for k, v in ham.items()}
    total = sum(agg.values())
    ranked = sorted(agg.items(), key=lambda kv: kv[1], reverse=True)
    # `pay_yaz=False` ise "toplamın %X'i" YAZILMAZ: yüzdeler/ortalamalar toplanmaz.
    # Canlı turda ölçüldü: bir oran ölçüsünde *"toplamın %10,2'si"* basılıyordu — sayı
    # matematiksel olarak anlamsız. Payı susturmak, yanlış pay yazmaktan iyidir.
    top, bot = ranked[0], ranked[-1]
    share = (top[1] / total * 100) if total else 0
    # ⚠ TEK KALEMDE PAY YAZILMAZ: canlı kullanıcı *"toplamın %100.0'i"* cümlesini gördü
    # ve *"boş laf — tek yıl tabii ki %100"* dedi. Bilgi taşımayan bir cümle, güveni
    # aşındırır: okuyan kişi cümlenin hesaplanmış mı yoksa doldurma mı olduğunu ayırt
    # edemez hâle gelir.
    pay = (f", toplamın %{round(share, 1)}'i)"
           if (total and toplanabilir and len(ranked) > 1) else ")")
    facts = [{"type": "top", "dim": dim, "measure": measure, "entity": top[0],
              "text": f"En yüksek {_ad(dim)}: {top[0]} ({_fmt(top[1], unit)}" + pay}]
    if len(ranked) > 1:
        facts.append({"type": "bottom", "dim": dim,
                      "text": f"En düşük: {bot[0]} ({_fmt(bot[1], unit)}); {len(ranked)} kalem"})
    return facts


def _segment_delta(rows: list[dict], dim: str, measure: str, unit: str | None,
                   lib: bool = False, _ad=lambda k: k) -> list[dict]:
    """🔴 FAZ 5.7 — **SEGMENT A↔B FARKI.**

    ## Ölçülen boşluk

    `in` filtresi **vardı** (*"RAM-2 ve RAM-3"* → `{"operator": "in", "value": [...]}`)
    ve iki segment **yan yana çiziliyordu** — ama *"aradaki fark ne?"* sorusunun cevabı
    hiçbir yerde **yazılı değildi**. Kullanıcı iki çubuğa bakıp farkı **kafadan
    çıkarıyordu**.

    ## ⚠ Neden bir KOLON değil, bir FACT

    Yol haritası *"Δ kolonu"* diyordu; ölçüldü ve şekil **yanlış** çıktı: `A − B` satır
    başına bir değer **değil**, iki satırın **arasındaki tek bir skalerdir**. Kolon
    olarak basmak, her satıra aynı sayıyı yazmak (ya da birine yazıp ötekini boş
    bırakmak) demekti. *Bir sayının şekli, onu nereye koyacağını belirler.*

    ## 🔴 TAM İKİ segmentte üretilir

    Üç segmentte *"A−B"* **hangi ikisi** olduğunu söylemez ve üç ayrı fark yazmak
    kullanıcının sormadığı bir tabloyu doğurur. Tek segmentte kıyaslanacak bir şey yok.
    *Belirsiz bir fark, farkın kendisinden kötüdür.*
    """
    ikili = [r for r in rows if r.get(dim) is not None and _is_num(r.get(measure))]
    if len(ikili) != 2:
        return []
    a, b = ikili[0], ikili[1]
    va, vb = _num(a[measure]), _num(b[measure])
    fark = va - vb
    pct = (fark / abs(vb) * 100) if vb else None
    return [{
        "type": "segment_delta", "dim": dim, "measure": measure,
        "a": str(a[dim]), "b": str(b[dim]),
        "mutlak": round(fark, 4),
        "pct": round(pct, 1) if pct is not None else None,
        # ⚠ `favorable` yalnız `lower_is_better` BEYAN EDİLMİŞSE yazılır — aksi hâlde
        # *"A daha yüksek"*in iyi mi kötü mü olduğunu **uydurmuş** olurduk.
        "favorable": (None if not lib else fark < 0),
        "text": f"{_ad(measure)}: {a[dim]} − {b[dim]} = {_fmt(fark, unit)}"
                + (f" (%{abs(round(pct, 1))})" if pct is not None else ""),
    }]


def _kpi_facts(kpi: dict) -> list[dict]:
    """KPI kartı: değer + iyi/kötü yönü + bileşen dökümü."""
    val, unit = kpi.get("value"), kpi.get("unit")
    label = kpi.get("label") or kpi.get("kpi")
    facts = [{"type": "kpi_value", "text": f"{label}: {_fmt(val, unit)}"}]
    comps = [c for c in (kpi.get("components") or []) if c.get("value") is not None]
    if comps:
        facts.append({"type": "kpi_components",
                      "text": "Bileşenler: "
                              + ", ".join(f"{c.get('label', c['key'])} {_fmt(c['value'], c.get('unit'))}"
                                          for c in comps)})
    return facts


def _signals(rows: list[dict], dims: list[str], time_col: str | None,
             m0: str, unit: str | None, lower_is_better: bool) -> list[dict]:
    """K3 (rehberli analitik) — PROAKTİF sinyaller: nötr FACTS'ten farklı olarak DİKKAT
    çekici durumları işaretler. (a) zaman serisinde ANOMALİ (z-score, detect_anomalies
    reuse), (b) YÖN endişesi (lower_is_better ölçü artıyor / normal ölçü düşüyor —
    "izlenmeli"), (c) YOĞUNLAŞMA (tek kalem payı ≥%50). Deterministik; ham veri LLM'e
    gitmez. severity: info | warning | critical."""
    out: list[dict] = []

    # (a) Zaman serisi anomalisi — schedules.detect_anomalies (aynı z-score motoru).
    if time_col and len(rows) >= 4:
        try:
            from app.schedules import detect_anomalies
            anoms = detect_anomalies({"rows": rows}, m0, k=2.0, unit=unit)
        except Exception:  # noqa: BLE001 - sinyal best-effort
            anoms = []
        if anoms:
            out.append({"severity": "warning", "kind": "anomaly",
                        "text": "Olağandışı değer — " + "; ".join(anoms[:2])})

    # (b) Trend yönü endişesi — ilk→son anlamlı (%10+) değişim, ölçü semantiğine göre kötüyse.
    if time_col and len(rows) > 1:
        try:
            first, last = _num(rows[0].get(m0)), _num(rows[-1].get(m0))
        except (ValueError, TypeError):
            first = last = None
        if first not in (None, 0) and last is not None:
            change = (last - first) / abs(first)
            rising = change > 0
            bad = (rising and lower_is_better) or (not rising and not lower_is_better)
            if abs(change) >= 0.10 and bad:
                yon = "arttı" if rising else "azaldı"
                out.append({"severity": "warning", "kind": "trend",
                            "text": f"{m0} dönem içinde %{abs(change) * 100:.0f} {yon} — izlenmeli"})

    # (c) Yoğunlaşma — kategorik dağılımda tek kalem toplamın ≥%50'si (risk/bağımlılık).
    if dims and not time_col and len(rows) > 2:
        vals = [(_num(r.get(m0)) if _is_num(r.get(m0)) else 0.0) for r in rows]
        tot = sum(vals)
        if tot > 0 and max(vals) / tot >= 0.50:
            out.append({"severity": "info", "kind": "concentration",
                        "text": f"Yoğunlaşma — en yüksek kalem toplamın "
                                f"%{max(vals) / tot * 100:.0f}'i"})
    return out


def interpret(result: dict | None, cube_query: dict | None = None,
              kpi: dict | None = None, units: dict[str, str] | None = None,
              lower_is_better: set[str] | None = None,
              esikler: list[dict] | None = None,
              cube_meta: dict | None = None,
              etiketler: dict[str, str] | None = None) -> dict | None:
    """Evrensel yorum: {facts:[...], summary:"Türkçe"} | None. TAMAMEN deterministik.

    result: {columns, rows, row_count}. cube_query/kpi ipucu (opsiyonel). units: ölçü→birim.
    lower_is_better: yönü DÜŞÜK=İYİ olan ölçü adları (DSO/CCC/fire…) — trend iyi/kötü çerçevesi.
    esikler: KULLANICININ KENDİ kurduğu sabit alarm eşikleri (Faz G3) — bkz.
      `schedules.kullanicinin_esikleri`. Cube metadata'sında `target:` diye bir beyan
      HİÇBİR cube'da yok (ölçüldü); demo için hedef uydurmak `pvm:` eşleştirmesinde
      reddedilen şeyin aynısı olurdu. Kullanıcı `fire_kg > 30` alarmını kurduğunda ise
      "benim için kritik sınır bu" demiş OLUR — bu uydurulmuş değil, beyan edilmiş bir
      hedeftir ve cevabın kendisinde görünmelidir."""
    units = units or {}
    lib_set = lower_is_better or set()
    # ⚠️ FAZ 0.10b — **GÖRÜNEN ADLAR.** Bu fonksiyon fact metnine **ham küp kolon adı**
    # koyuyordu (`toplam_fire_kg` · `tarih__year`) ve `OutputInsight` onu **aynen**
    # basıyordu. Canlı bir kullanıcı turu şunu gördü:
    #   *"En yüksek tarih__year: 2026-01-01 00:00:00 (454.477,90 …)"*
    # ve şöyle dedi: *"Ben yıl sordum, bana veritabanı sütun adı ve saat 00:00
    # gösteriliyor."*
    #
    # 🔴 **Kritik yan etki:** bu metin `answer.py::_anlati_ekle`'de LLM'e `gercekler`
    # **GİRDİSİ** oluyor → `t2_anlatici` açılırsa model `toplam_fire_kg` **etrafında
    # cümle kurar**. Akıcı ama iç adlı bir cümle robotikliği kaldırmaz, **üstüne para
    # ödetir**. Bu yüzden `0.10b`, `t2_anlatici`'nin **sert ön koşuludur**.
    #
    # 🔴 **İKİNCİ ETİKET KAYNAĞI AÇILMAZ.** Etiketler `build_catalog`'dan gelir —
    # `eylem._rapor_adi` ve `cube_router.next_step_chips` ile **aynı kaynak**.
    # `eylem.py`'nin kendi uyarısı: *"bu depoda «ikinci bir etiket kaynağı» deseni
    # **beş kez** ayrışmayla sonuçlandı."*
    #
    # `etiketler=None` → metin **birebir bugünkü** (geriye uyum, testle kilitli).
    _etiket = dict(etiketler or {})

    def _ad(k: str) -> str:
        """İç ad → görünen ad. Sözlükte yoksa **alt çizgiler boşluğa** çevrilir:
        `toplam_fire_kg` → `toplam fire kg`. Ham adı olduğu gibi basmak, kullanıcıya
        veritabanı şemasını okutmaktır."""
        if not _etiket:
            return k                                   # geriye uyum: BİREBİR bugünkü
        return _etiket.get(k) or k.replace("__", " · ").replace("_", " ")
    # 🔴 TOPLANABİLİRLİK — kural ZATEN TEK SAHİPTE: `contribution.ayristirilabilir_mi`.
    # Burada ikinci bir kopya YAZILMAZ, o sahip ÇAĞRILIR. `interpret` bugüne kadar onu
    # tanımıyordu (*"kimlik asimetrisi"*): katkı yolu *"`fire_orani_yuzde` bir ortalama/
    # oran — katkı payı tanımsız"* diye dürüstçe reddederken, aynı ölçü için yorum satırı
    # hem **toplamın payını** hem de toplanmış bir **trendi** yayımlıyordu.
    from app.contribution import BILINMIYOR, TAM, YARI, YOK, toplanabilirlik
    if kpi:
        facts = _kpi_facts(kpi)
        return {"facts": facts, "summary": " · ".join(f["text"] for f in facts)}
    # 🔴 `§35` — boşluk **satır sayısı değil ölçü değeri** meselesidir. `[{"ciro": null}]`
    # bir sonuç değil bir **yokluktur**; aşağıdaki yol onu *"1 satırlık sonuç."* diye
    # özetliyordu. Yüklem tek sahiptedir (`veri_araligi.bos_mu`) — burada ikinci bir
    # kopya yazmak, aynı boşluğun iki tanımı demekti.
    from app.veri_araligi import bos_mu
    # 🔴 **VE `None` BURADA DA AYRI — dersin ÜÇÜNCÜ tekrarı (`§38.2`).**
    #
    # `bos_mu(None, …)` bilerek `False` döner: *"ölçüm yapılmadı"* ile *"ölçüldü, boş"*
    # ayrı şeylerdir (`execute=false` yolu buna dayanıyor). Ama **bu** tüketici için
    # ikisinin de cevabı aynı: yorumlanacak bir şey yok. İki tüketicinin aynı yüklemden
    # farklı sonuç istemesi bir çelişki değil — yüklemin **doğru** ayrımı yapmasının
    # kanıtıdır; ayrım olmasaydı biri ötekinin davranışını taşımak zorunda kalırdı.
    #
    # *Bir ayrımın değeri, iki tarafın ondan farklı şeyler isteyebilmesidir.*
    if result is None or bos_mu(result, cube_query):
        return None
    rows, cols = result["rows"], result.get("columns") or list(result["rows"][0].keys())
    # OTORİTE GEÇİRİLİYOR (Faz C1): `cube_query` zaten elimizdeydi ama yalnız `measures`
    # süzgeci için kullanılıyordu; `dimensions`/`timeDimensions` görmezden geliniyordu.
    measures, dims, time_col = _classify(cols, rows, cube_query)
    if cube_query and cube_query.get("measures"):  # cube ipucu ölçü seçimini netleştirir
        measures = [m for m in cube_query["measures"] if m in measures] or measures
    if not measures:
        return {"facts": [{"type": "count", "text": f"{result.get('row_count', len(rows))} satır"}],
                "summary": f"{result.get('row_count', len(rows))} satırlık sonuç."}

    m0 = measures[0]
    unit = units.get(m0)
    facts: list[dict] = []
    # Tek satır tek ölçü → tek değer.
    if len(rows) == 1 and not dims:
        facts.append({"type": "single", "measure": m0,
                      "text": f"{_ad(m0)}: {_fmt(rows[0].get(m0), unit)}"})
    elif time_col and len(rows) > 1:              # zaman serisi → trend
        entity = next((d for d in dims if d != time_col), None)
        if entity is None:
            # ⚠ KIRILIMSIZ seri: dönem başına ZATEN tek satır var → **hiç toplama yok**,
            # dolayısıyla toplanabilirlik sorusu da yok. Bir oran serisinin trendi
            # (fire oranı Oca %10 → Haz %20) **tamamen meşrudur**. Denetim bu dalın
            # pivot dalıyla "asimetrik" göründüğünü işaretledi; asimetri gerçek ama
            # **doğru** — farkı yaratan şey toplama ihtiyacıdır, ölçünün kendisi değil.
            # (MIMARI metni bir süre bunu koşulsuz yasak gibi anlatıyordu; daraltıldı.)
            facts += _series_facts(rows, time_col, m0, unit, m0 in lib_set, _ad)
        else:
            # 🔴 PİVOT (varlık × dönem). Ham satırlarda *"ilk→son"* İKİ FARKLI VARLIĞI
            # kıyaslar — canlı turda ölçülen sessiz-yanlış tam buydu. Trend bir DÖNEM
            # ifadesidir: önce döneme göre toplanır. Ölçü toplanamıyorsa (oran/ortalama)
            # trend **hiç yayımlanmaz** — susmak, yanlış bir yüzdeden iyidir.
            n = len({str(r.get(entity)) for r in rows})
            # POLİTİKA: dönem trendi ZAMAN-DIŞI eksende toplama ister → `TAM` **ve `YARI`**
            # kabul edilir (bir bakiye müşteriler arasında toplanır; toplanamadığı eksen
            # zamandır). `BILINMIYOR` → **FAIL-CLOSED**: yanlış bir trend, hiç trend
            # olmamasından kötüdür. Bkz. `contribution.toplanabilirlik` tablosu.
            sinif, neden = toplanabilirlik(m0, cube_meta)
            # 🔴 GEREKÇE, TANIMSIZLIĞI DEĞİL **BU GÖRÜNÜMÜN** SINIRINI ANLATIR.
            # Canlı kullanıcı iki ekranı yan yana gördü: kırılımsız ekranda
            # *"%3,1 azaldı — iyileşti"*, kırılımlı ekranda *"bu ölçüde trend
            # matematiksel olarak TANIMSIZ"*. Kullanıcı: *"İkisi aynı anda doğru olamaz —
            # hangisine inanacağım?"* Haklı: mantık doğruydu ama **cümle yanlıştı**.
            # Tanımsız olan trend değil, **kırılım boyunca TOPLAMA**. Cümle artık bunu
            # söyler ve kullanıcıyı **çalışan görünüme** yönlendirir.
            if sinif == BILINMIYOR:
                neden = (f"{m0} için toplanabilirlik beyanı yok — bu kırılımlı görünümde "
                         "dönem trendi hesaplanamaz (yanlış bir yüzde, hiç yüzdeden kötüdür)")
            elif sinif not in (TAM, YARI):
                neden = (f"{neden.rstrip('. ')} — yani {entity} kırılımı boyunca "
                         "TOPLANAMAZ, bu yüzden dönem trendi BU GÖRÜNÜMDE hesaplanamıyor. "
                         "Kırılımsız (yalnız dönem) görünümde trend hesaplanır.")
            if sinif in (TAM, YARI):
                facts += _series_facts(_donem_bazinda_topla(rows, time_col, m0),
                                       time_col, m0, unit, m0 in lib_set, _ad)
                # ⚠ MARKDOWN YOK: `OutputInsight.tsx` `summary`'yi DÜZ METİN basar
                # (`shape` bilinçli olarak rozet sözlüğünün dışında). Canlı kullanıcı
                # ekranda `**dönem toplamları**` yıldızlarını **harfi harfine** gördü.
                facts.append({"type": "shape",
                              "text": f"{n} {_ad(entity)} × dönem kırılımı — trend dönem "
                                      "toplamları üzerinden"})
            else:
                facts.append({"type": "shape",
                              "text": f"{n} {_ad(entity)} × dönem kırılımı — dönem trendi "
                                      f"YAZILMADI: {neden}"})
    elif dims:                                     # kategorik → sıralama/pay
        # 🔴 **ASİMETRİ BİLİNÇLİDİR ve iki farklı riske dayanır.**
        # · **Trend (yukarıda)** `BILINMIYOR`'da **FAIL-CLOSED**: orada kanıtlanmış bir
        #   sessiz-yanlış vardı (aynı veriye üç farklı yüzde) ve yanlış bir trend
        #   doğrudan yanlış karar ürettiriyordu.
        # · **Sıralama/pay (burada)** `BILINMIYOR`'da **toplanabilir sayılır**, çünkü:
        #   (a) baskın yol `cube_meta=None`'dır (Discovery/LLM cevaplarında `cube_query`
        #       yoktur) — fail-close etmek kapsamı geniş biçimde kırpardı;
        #   (b) asıl riskli sınıf olan oran/ortalama adları **ad kalıbıyla** zaten
        #       yakalanıyor (`ort_` · `_yuzde` · `_orani` · `_pct` → `YOK`);
        #   (c) `_rank_facts` toplanamayan ölçüde **çok satırlı** durumda zaten
        #       sıralama yapmıyor.
        # Kapı bu asimetriyi iki yönlü kilitler; kaldırılırsa kapsam sessizce kırpılır.
        _sinif, _ = toplanabilirlik(m0, cube_meta)
        facts += _rank_facts(rows, dims[0], m0, unit,
                             toplanabilir=_sinif != YOK, _ad=_ad)
        # 🔴 FAZ 5.7 — SEGMENT A↔B FARKI. `in` filtresi ve yan yana çizim vardı; aradaki
        # farkın **sayısı** hiçbir yerde yazılı değildi ve kullanıcı onu kafadan
        # çıkarıyordu. Yalnız **tam iki** segmentte üretilir.
        facts += _segment_delta(rows, dims[0], m0, unit,
                               lib=m0 in (lower_is_better or set()), _ad=_ad)
    if len(measures) > 1:
        facts.append({"type": "measures", "text": f"{len(measures)} ölçü: " + ", ".join(measures)})
    if not facts:
        facts.append({"type": "count", "text": f"{len(rows)} satır"})
    out = {"facts": facts, "summary": " ".join(f["text"].rstrip(".") + "." for f in facts)}
    signals = _signals(rows, dims, time_col, m0, unit, m0 in lib_set)  # K3 proaktif sinyaller
    if esikler:
        # EŞİK KIYASI (Faz G3) — gövde `schedules.esik_sinyalleri`'nde: alarm koşumuyla
        # AYNI matematiği (`check_threshold`) kullanır. İkisi ayrı yazılsaydı, e-postada
        # uyarı gelirken ekranda gelmeyen bir gün gelirdi. Eşiğin ALTINDA kalmak SUSAR:
        # "eşiğin %40 altındasın" her cevaba eklenirse asıl uyarılar okunmaz olur.
        try:
            from app.schedules import esik_sinyalleri
            signals = esik_sinyalleri(rows, esikler, units) + signals
        except Exception:  # noqa: BLE001 - sinyal best-effort
            pass
    if signals:
        out["signals"] = signals
    return out
