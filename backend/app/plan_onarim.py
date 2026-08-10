"""PLAN ONARIMI — modelin **mekanik olarak tek anlamlı** kaymalarını sessizce değil,
**beyan ederek** düzeltir (FAZ O-15).

## Neden bir katman daha: üç seviye, ve her biri ötekinden ucuz

Kullanıcı kararı (2026-08-09): *"bu tarz kararsızlıkları kontrol edecek denetleyecek
engelleyecek vs bir şeyler düşün geliştir — mükemmelce; bunu LLM'e bırakmak riskli,
LLM'in de işini kolaylaştır."*

Bugüne kadar iki seviye vardı ve **aralarında boşluk** vardı:

| # | seviye | maliyeti | neyi çözer |
|---|---|---|---|
| 1 | **İSTEM** — modele doğrusunu öğret | bir kez, sıfır çalışma zamanı | genel eğilim |
| — | 🔴 *(boşluk)* | | **mekanik kayma** |
| 2 | **DOĞRULAYICI** — reddet, bir düzeltme turu iste | bir LLM çağrısı + gecikme | gerçek belirsizlik |

⊙ Ölçüldü (canlı `II` turu, 20 senaryo): reddedilen planların **üçte biri** bir
belirsizlikten değil, **tek anlamlı bir alan kaymasından** düşüyordu:

* `parti` küpünün zaman ekseni `tarih`; model onu `dimensions`'a yazdı → `II19`, `II20`
* dönem ifadesi `timeDimensions`'a **düz metin** olarak yazıldı (*"This month"*) → `II8`

Bu ikisinin **başka bir okuması yoktur**. `dimensions:["tarih"]` yazan bir model, o
küpte `tarih` diye bir *boyut* olmadığı için, **kesinlikle** zaman eksenini kastediyor.
Bunu bir düzeltme turuna havale etmek, bilinen bir cevabı ikinci kez satın almaktır.

*Bir kaymayı düzeltmek ile bir belirsizliği çözmek aynı iş değildir: birincisi bir
eşleme, ikincisi bir karar. Eşlemeyi karar merciine göndermek, karar merciini
meşgul eder ve kararı ucuzlatır.*

## 🔴 SESSİZ ONARIM YOKTUR — her onarım BEYAN EDİLİR

Bu modülün her düzeltmesi bir **metin** üretir ve o metin cevabın izine (`trace`)
düşer. Gerekçe `MIMARI`'nin değişmezidir: kullanıcının gördüğü sayı, kendisinin
yazmadığı bir varsayımla üretildiyse, o varsayım **görünür** olmalıdır.

⚠ Ve bu, onarımı bir **ölçüm aletine** de çevirir: izde bir onarım sık görünüyorsa
istem (seviye 1) yetersiz demektir. *Sessiz bir onarım, düzeltilmesi gereken bir
istemi süresiz olarak gizler.*

## 🔴 SINIR: yalnız TEK ANLAMLI kayma

Bir onarım ancak şu üç şartın **hepsi** sağlanırsa yazılır:

1. yazılan değer, yazıldığı alanda **geçersiz** (yoksa dokunulmaz — meşru bir kullanım
   olabilir),
2. aynı değerin **başka tam olarak bir** geçerli yeri var,
3. taşıma sonucu sorgunun **anlamını değiştirmiyor**, yalnız ifade ediliş biçimini.

Üçüncü şart sağlanmıyorsa onarım **yazılmaz** — reddedip sormak doğrudur. `§101.1`:
*yanlış pozitif üreten bir yordam, kapattığı kusurdan pahalıdır.*
"""

from __future__ import annotations

#: Zaman ekseninin geçerli granülerlikleri — motorun tanıdıkları. Kapalı bir küme;
#: genişletilmesi motor sözleşmesinin değişmesini gerektirir.
GRANULERLIKLER = ("day", "week", "month", "quarter", "year")

#: Bir zaman ekseni istendiğinde granülerlik yazılmamışsa varsayılan. ⊙ Ölçüldü:
#: `II20`/`II19`'da model *«aylık fire»* / *«aylara göre»* diyordu ve route'un niyet
#: okuması da `granülerlik=month` veriyordu. Aya düşmek en az sürpriz üreten seçim.
VARSAYILAN_GRANULERLIK = "month"

#: 🔴 `§AR/S(4)` — **OPERATÖR TAKMA ADLARI: mekanik, tek anlamlı, kapalı.**
#: Modelin İngilizce/matematiksel makul tahminleri ↔ motorun adları. Her satır
#: **tek anlamlıdır**: `equals`ın kastedebileceği tam olarak bir operatör var.
#: ⚠ Hedefler `MOTOR_OPERATORLERI`'ne karşı **kapıda** doğrulanır — uydurma bir hedef
#: buraya yazılırsa kapı kırmızı verir.
OPERATOR_TAKMA_ADLARI: dict[str, str] = {
    "equals": "eq", "equal": "eq", "=": "eq", "==": "eq", "is": "eq",
    "not_equals": "neq", "not_equal": "neq", "ne": "neq", "!=": "neq", "<>": "neq",
    ">": "gt", ">=": "gte", "<": "lt", "<=": "lte",
    "greater_than": "gt", "greater_than_or_equal": "gte",
    "less_than": "lt", "less_than_or_equal": "lte",
    "like": "contains", "includes": "contains", "icerir": "contains",
    "in_list": "in", "one_of": "in", "not_one_of": "not_in",
    "isnull": "is_null", "is_none": "is_null", "isnotnull": "is_not_null",
    "begins_with": "starts_with", "startswith": "starts_with",
}


def onar(cq: dict, spec: dict) -> tuple[dict, list[str]]:
    """Bir `cube_query`'yi küp tanımına karşı **mekanik olarak** onarır.

    Döner: `(onarılmış_sorgu, beyanlar)`. `beyanlar` boşsa hiçbir şeye dokunulmadı ve
    dönen sözlük girdinin **kendisidir** (kopya bile değil — `KURAL B` disiplini: bir
    şey yapmıyorsa hiçbir iz bırakmaz).

    ⚠ `spec` bir **küp tanımıdır** (`index[cube]`), şemanın tamamı değil: onarımın
    bilmesi gereken tek şey o küpün ölçü/boyut/zaman adlarıdır.
    """
    if not isinstance(cq, dict) or not isinstance(spec, dict):
        return cq, []
    zamanlar = [str(z) for z in (spec.get("time_dimensions") or [])]
    boyutlar = {str(d) for d in (spec.get("dimensions") or [])}
    if not zamanlar:
        return cq, []
    beyan: list[str] = []
    out = dict(cq)

    # ── R1 · ZAMAN EKSENİ `dimensions`'a düşmüş ────────────────────────────────
    # Katalog satırı `…; dimensions[a, b]; time[tarih]` biçiminde yazılıyor: iki liste
    # **görsel olarak paralel**, ve model `tarih`i bir boyut adı sanıyor. İstem artık
    # bağı açıkça kuruyor (seviye 1); bu onarım geride kalanı yakalar.
    _dims = [str(d) for d in (out.get("dimensions") or [])]
    _kayan = [d for d in _dims if d in zamanlar and d not in boyutlar]
    if _kayan:
        _kalan = [d for d in _dims if d not in _kayan]
        _mevcut = {str((td or {}).get("dimension")) for td in (out.get("timeDimensions") or [])
                   if isinstance(td, dict)}
        _yeni = list(out.get("timeDimensions") or [])
        for d in _kayan:
            if d in _mevcut:
                continue
            _yeni.append({"dimension": d, "granularity": VARSAYILAN_GRANULERLIK})
            beyan.append(f"`{d}` bir zaman ekseni — kırılım olarak değil, "
                         f"`{VARSAYILAN_GRANULERLIK}` granülerliğinde zaman ekseni olarak okundu")
        if _kalan:
            out["dimensions"] = _kalan
        else:
            out.pop("dimensions", None)
        if _yeni:
            out["timeDimensions"] = _yeni

    # ── R1b · OPERATÖR TAKMA ADI — **mekanik, tek anlamlı** ────────────────────
    # 🔴 `§AR/S(4)` — `equals` motorun 12 operatöründen **tam olarak birini**
    # kastedebilir. Bunu bir LLM düzeltme turuna havale etmek, bu modülün kendi
    # cümlesiyle *«bilinen bir cevabı ikinci kez satın almaktır»*.
    # ⚠ Takma adlar **kapalı**: her biri motorun bir operatörüne birebir eşlenir;
    # eşlenmeyen bir ad **dokunulmadan** beyaz listeye gider ve orada dürüstçe düşer.
    _tf = out.get("filters")
    if isinstance(_tf, list):
        _yeni_f, _degisti = [], False
        for f in _tf:
            if not isinstance(f, dict):
                _yeni_f.append(f)
                continue
            _op = str(f.get("operator") or "").strip().lower()
            _hedef = OPERATOR_TAKMA_ADLARI.get(_op)
            if _hedef and _hedef != f.get("operator"):
                f = {**f, "operator": _hedef}
                beyan.append(f"`{_op}` operatörü motorda yok — `{_hedef}` olarak okundu")
                _degisti = True
            _yeni_f.append(f)
        if _degisti:
            out["filters"] = _yeni_f

    # ── R2 · `timeDimensions` bir METİN ────────────────────────────────────────
    # Ölçüldü (`II8`): `"timeDimensions": "This month"`. Motor bir **dizi** bekliyor ve
    # tip hatasıyla düşüyor — plan tamamen reddediliyor. Oysa yazılan şey tek anlamlı:
    # bir **dönemdir** ve dönemin evi `period_expr`'dir (istem bunu zaten söylüyor).
    _td = out.get("timeDimensions")
    if isinstance(_td, str) and _td.strip():
        _metin = _td.strip()
        out.pop("timeDimensions", None)
        if _metin.lower() in GRANULERLIKLER:
            out["timeDimensions"] = [{"dimension": zamanlar[0], "granularity": _metin.lower()}]
            beyan.append(f"`timeDimensions` metin olarak yazılmıştı → `{zamanlar[0]}` "
                         f"ekseninde `{_metin.lower()}` granülerliği olarak okundu")
        elif not out.get("period_expr"):
            out["period_expr"] = _metin[:120]
            beyan.append(f"«{_metin}» bir **dönem** — `timeDimensions`'dan alınıp "
                         f"dönem alanına taşındı")
        else:
            beyan.append(f"«{_metin}» `timeDimensions`'a yazılmıştı ve orada bir karşılığı "
                         f"yok — dönem zaten belirtilmiş olduğu için düşürüldü")

    # ── R3 · `timeDimensions` dizisinin İÇİNDE metin ───────────────────────────
    # Aynı kayma bir eleman düzeyinde de görülüyor: `["month"]` ya da `["tarih"]`.
    _td2 = out.get("timeDimensions")
    if isinstance(_td2, list) and any(isinstance(x, str) for x in _td2):
        _cikti: list[dict] = []
        for x in _td2:
            if isinstance(x, dict):
                _cikti.append(x)
                continue
            _s = str(x).strip()
            if _s.lower() in GRANULERLIKLER:
                _cikti.append({"dimension": zamanlar[0], "granularity": _s.lower()})
                beyan.append(f"zaman ekseni yalnız granülerlikle yazılmıştı → "
                             f"`{zamanlar[0]}` ekseni varsayıldı")
            elif _s in zamanlar:
                _cikti.append({"dimension": _s, "granularity": VARSAYILAN_GRANULERLIK})
                beyan.append(f"`{_s}` ekseni granülerliksiz yazılmıştı → "
                             f"`{VARSAYILAN_GRANULERLIK}` varsayıldı")
            # ⚠ Tanınmayan metin **atılmaz, bırakılmaz**: beyaz liste onu reddetsin ve
            # kullanıcı gerçek gerekçeyi görsün. Buradan sessizce düşürmek, bir kusuru
            # bir *"veri yok"*a çevirirdi.
            else:
                _cikti.append({"dimension": _s})
        out["timeDimensions"] = _cikti

    return (out, beyan) if beyan else (cq, [])


# ═══ TEŞHİS — *"neden geçmedi"* sorusunun tek sahibi ═══════════════════════════

def gerekce(cq: dict, spec: dict | None, sema: dict | None = None) -> str:
    """Bir `cube_query` beyaz listeden **neden** geçmedi — adıyla.

    🔴 **Tek sahip.** Bu metin iki yerden isteniyor ve ikisi de aynı cümleyi kurmalı:
    `plan_kosucu.dogrula` (plan **kurulurken** — onarım turu bunu okur) ve
    `plan_tuketici` (plan **koşarken** — kullanıcı bunu okur). İki kopya yazmak,
    modele bir cümle kullanıcıya başka bir cümle söylemekti (`KAT-1`).

    ⚠ `parse_cube_query` bir **kapıdır**, bir tanıcı değil: `None` döner ve nedenini
    söylemez — söylememelidir. Neden bilgisi burada üretilir çünkü aynı küp tanımı
    burada da elde.

    ⊙ Ölçüldü (canlı `II14`·`D2`): *«`parti` sorgusu beyaz listeden geçmedi»* içeriksiz
    bir teşhisti ve **onarım turu da onu okuyordu** — model neyin olmadığını biliyor,
    neyin **olduğunu** bilmiyordu; ikinci deneme de düştü.
    """
    if not spec:
        return f"`{(cq or {}).get('cube') or '(cube yok)'}` diye bir cube YOK"
    _c = spec.get("name") or (cq or {}).get("cube")
    _o = set(spec.get("measures") or [])
    _b = {str(d) for d in (spec.get("dimensions") or [])}
    _z = {str(z) for z in (spec.get("time_dimensions") or [])}
    parca: list[str] = []
    _eksik_o = [m for m in ((cq or {}).get("measures") or []) if m not in _o]
    if _eksik_o:
        parca.append(f"`{_c}`'de şu ölçü(ler) yok: {', '.join(map(str, _eksik_o))}")
    _eksik_b = [d for d in ((cq or {}).get("dimensions") or []) if d not in _b]
    if _eksik_b:
        parca.append(f"`{_c}`'de şu boyut(lar) yok: {', '.join(map(str, _eksik_b))}"
                     + bilinen_boyutlar(spec, _eksik_b)
                     + _sahibini_soyle(_eksik_b, _c, sema))
    if not ((cq or {}).get("measures") or []):
        parca.append(f"`{_c}` için hiç ölçü yazılmamış")
    _bozuk_td = [td for td in ((cq or {}).get("timeDimensions") or [])
                 if not isinstance(td, dict) or td.get("dimension") not in _z]
    if _bozuk_td:
        parca.append(f"`{_c}`'nin zaman ekseni {sorted(_z) or '(yok)'} — şu yazılmış: "
                     + ", ".join(f"`{td.get('dimension') if isinstance(td, dict) else td}`"
                                 for td in _bozuk_td))
    # 🔴 `§AR/S(3)` — **`None` BİR ALAN ADI DEĞİLDİR.** Alan hiç yazılmadığında mesaj
    # *«süzülemeyecek alan(lar): `None`»* basıyordu ve model onu *«`None` diye bir alan
    # mı aramışım?»* diye okuyordu. Eksiklik ile geçersizlik **iki ayrı teşhistir**.
    _eksik_f = [f for f in ((cq or {}).get("filters") or [])
                if not isinstance(f, dict) or f.get("dimension") is None]
    if _eksik_f:
        parca.append(f"süzgeçte `dimension` alanı hiç yazılmamış ({len(_eksik_f)} süzgeç)"
                     + bilinen_boyutlar(spec))
    _bozuk_f = [f for f in ((cq or {}).get("filters") or [])
                if isinstance(f, dict) and f.get("dimension") is not None
                and f.get("dimension") not in (_b | _z)]
    if _bozuk_f:
        parca.append(f"`{_c}`'de süzülemeyecek alan(lar): "
                     + ", ".join(f"`{f.get('dimension')}`" for f in _bozuk_f)
                     + bilinen_boyutlar(spec))
    try:
        from app import cube_operatorleri as _ops
        _bozuk_op = [str(f.get("operator")) for f in ((cq or {}).get("filters") or [])
                     if isinstance(f, dict) and not _ops.gecerli(f.get("operator"))]
    except Exception:
        _bozuk_op = []
    if _bozuk_op:
        # 🔴 `§AR/S(2)` — **DOĞRUSUNU DA SÖYLE.** `bilinen_boyutlar()`'ın birebir
        # eşleniği: bu fonksiyonun kendi docstring'i *«model neyin olmadığını biliyor,
        # neyin OLDUĞUNU bilmiyordu; ikinci deneme de düştü»* diyordu — ders boyut
        # dalında uygulanmış, **operatör dalında uygulanmamıştı**.
        try:
            from app.cube_operatorleri import MOTOR_OPERATORLERI as _MO
            _kuyruk = " — geçerliler: " + ", ".join(_MO)
        except Exception:                      # noqa: BLE001 — teşhis turu düşmez
            _kuyruk = ""
        parca.append("tanınmayan süzgeç operatörü: "
                     + ", ".join(f"`{o}`" for o in _bozuk_op) + _kuyruk)
    return " · ".join(parca) or f"`{_c}` sorgusu beyaz listeden geçmedi"


def _sahibini_soyle(eksik: list, kup: str | None, sema: dict | None) -> str:
    """🔴🔴 `§SB` — **«BU BOYUT YOK» YETMEZ: «ŞU KÜPTE VAR» DA SÖYLENMELİ.**

    ⊙ Ölçüldü (`A9` sayacı, ilk koşum): plan redlerinin **baskın sınıfı** `boyut_yok`
    ve üçünün **üçü de aynı**: `parti`'de `sebep` isteniyor. Kullanıcı *«fire neden
    arttı»* diyor; doğal kırılım **sebep**tir ve `parti` onu taşımıyor — ama
    `kalite.sebep` ve `makine_duruslari.neden` taşıyor.

    ⊙ Bu bir **mutfak eksikliği** değil bir **yönlendirme** eksikliğidir: veri var,
    başka küpte. Red *«yok»* deyip susunca düzeltme turu **aynı küpte** başka bir boyut
    arıyor; oysa doğru hamle **öteki küpe bir adım daha** yazmak — orkestratörün tam
    olarak var oluş sebebi.

    ⚠ Metin **şemadan üretilir**, elle liste yazılmaz: yeni bir küp eklendiğinde
    yönlendirme kendiliğinden doğru kalır. *Bir yönlendirmeyi elle yazmak, onu bir
    sonraki küpte yanlış yazmaktır.*
    """
    if not sema or not eksik:
        return ""
    sahip: dict[str, list[str]] = {}
    for c in (sema.get("cubes") or []):
        if c.get("name") == kup:
            continue
        _var = {str(d) for d in (c.get("dimensions") or [])}
        for d in eksik:
            if str(d) in _var:
                sahip.setdefault(str(d), []).append(str(c.get("name")))
    if not sahip:
        return ""
    return (" — ⊙ ama " + " · ".join(
        f"`{d}` şu küplerde VAR: {', '.join(k[:3])}" for d, k in sorted(sahip.items()))
        + ". O kırılım için **ayrı bir `SORGU` adımı** yaz (aynı küpte zorlama).")


def bilinen_boyutlar(spec: dict, eksik: list | None = None) -> str:
    """*«var olanlar: …»* kuyruğu — bir *«yok»* cümlesi yön göstermez.

    ⚠ Liste **12'de kırpılır**: bir küpün 17 boyutunu red mesajına dökmek, mesajı
    kataloğun kopyasına çevirir ve asıl teşhisi gömer.
    """
    _b = sorted(str(d) for d in (spec.get("dimensions") or []))
    if not _b:
        return ""
    kuyruk = f" (var olanlar: {', '.join(_b[:12])}"
    kuyruk += f" … +{len(_b) - 12})" if len(_b) > 12 else ")"
    _z = [str(z) for z in (spec.get("time_dimensions") or [])]
    _carpisan = [z for z in _z if z in (eksik or [])]
    if _carpisan:
        kuyruk += (f" — ⚠ `{', '.join(_carpisan)}` bir ZAMAN EKSENİdir: `dimensions`'a "
                   f"değil `timeDimensions`'a yazılır")
    return kuyruk
