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
