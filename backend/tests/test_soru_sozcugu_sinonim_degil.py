"""🔴🔴 `§K9-devam` — ÇIPLAK SORU SÖZCÜĞÜ BİR BOYUT SİNONİMİ OLAMAZ.

## Ölçülen kusur (canlı, 2026-08-26, `demo-boyahane`)

`isg.kok_neden` ve `kalite.sebep` boyutları, sinonim listelerinde ÇIPLAK
`"neden"`/`"sebep"` taşıyordu. Bu iki kelime Türkçe'de birer SORU SÖZCÜĞÜDÜR
("ram 3 neden böyle?"), bir ürün/olay adı değil. Bir cube'un sinonim listesine
girince ürünün **her** yerinde her nedensel takip sorusu
(`niyet.py::_kirilimlar` → `cube_router._match_dims`) bu dar alana yanlış
kırılım olarak eşleşiyordu — kullanıcının "neden böyle?" sorusu bir kök-neden
ANALİZİ yerine sessizce bir kırılım EKLEME isteğine dönüşüyordu (canlı kanıt:
`niyet: tür=kirilim · kırılım=kok_neden,sebep`, hiç analiz metni yok).

⚠ `followup.py`'nin `§NÇ` tarihçesi AYNI kusuru (çıplak "neden" bir alan adı
sanılması) zaten üç kez düzeltmişti — ama yalnız `followup.py` içinde. Bu
sinonim listesi (farklı bir eşleştirme yolu, `cube_router._match_dims`) o
dersi hiç görmemişti — aynı kök kusurun İKİNCİ, bağımsız bir vukuu.

## 🔴🔴 FAZ 3.2 — GENELLEŞTİRME (`§K9-devam`'ın kendisinin genişlemesi)

İlk yazım yalnız `followup._NEDEN`'e bakıyordu — ama `_NEDEN` `followup.py`'nin
**dokuz** konuşma-kalıbı sözlüğünden yalnız BİRİ. Aynı çakışma sınıfı (bir
konuşma-kalıbı kelimesinin bir cube sinonimi olarak da kayıtlı olması) ilke
gereği `_NORMAL`/`_NE_YAPMALI`/`_ISARET`/`_TAKIP`/`_PAYLAS`/`_MAKBUZ`/
`_ANLAT`/`_YAPISAL`'ın HERHANGİ birinde de olabilirdi — kapı yalnız `_NEDEN`'e
bakarken bu diğer sekizini hiç göremiyordu. Tur 2'nin kendi ölçtüğü örüntü
(*"KÖK NEDEN A — bir kelime iki görevde"*) burada birebir tekrar ediyordu:
kapı **KENDİ İÇİNDE** yalnız tek bir örneğine karşı korunmuştu.

⚠ `_ISARET_ZAMIRI` BİLEREK dışarıda bırakıldı: o bir konuşma-kalıbı sözlüğü
DEĞİL, bir ZAMİR/ÇAPA listesidir ("bu", "şu"...) — üyeleri zaten TEK harfli
kadar kısa ve YAYGIN olmaları GEREKİYOR (Türkçenin işaret zamirleri). Onu bu
kapıya katmak, gerçek bir kusur değil saf gürültü üretirdi (`ADR-0008`'in
"kapalı dilbilgisi sınıfı" ayrımı — zamirler kapalı sınıftır, konuşma-kalıbı
FRAZLARI değildir). O ailenin KENDİ sorunu (çıplak `"bu"` temporal ifadelerle
karışması) ayrı, FAZ 3.4'te izleniyor — burada KARIŞTIRILMADI.

## Bu kapı ne yapar

Tekil bir cube'u yamalamak yerine, **hiçbir cube'un** (bugünkü ya da
gelecekteki) bu hatayı tekrarlayamayacağı bir yapısal sınır çizer: hiçbir
`dimension_synonyms`/`measure_synonyms` girdisi, `followup.py`'nin dokuz
konuşma-kalıbı sözlüğünden HERHANGİ BİRİNİN ÇIPLAK bir üyesiyle (tam eşit,
alt dize değil) birebir aynı olamaz. Çok kelimeli, spesifik ifadeler ("kaza
nedeni", "hata sebebi") serbesttir — onlar gerçekten o alana özgüdür ve bir
soru cümlesinde tek başına nadiren belirir.

⚠ `ADR-0008` ile çelişmez: yeni bir sözlük İCAT EDİLMİYOR, `followup.py`'nin
ZATEN var olan, ölçümle büyütülmüş dokuz sözlüğü TEK KAYNAK olarak okunuyor
(`KAT-1`) — bu test onları bir de KATALOG tarafında zorunlu kılıyor.
"""

from __future__ import annotations

from app.followup import (
    _ANLAT,
    _MAKBUZ,
    _NE_YAPMALI,
    _NEDEN,
    _NORMAL,
    _ISARET,
    _PAYLAS,
    _TAKIP,
    _YAPISAL,
)

# 🔴🔴 FAZ 3.2 — dokuz konuşma-kalıbı sözlüğünün TAMAMI, adıyla. `_ISARET_ZAMIRI`
# bilerek DIŞARIDA (yukarıdaki docstring — kapalı dilbilgisi sınıfı, ayrı kusur
# ailesi, FAZ 3.4).
_SOZLUKLER: dict[str, tuple[str, ...]] = {
    "_NEDEN": _NEDEN,
    "_NORMAL": _NORMAL,
    "_NE_YAPMALI": _NE_YAPMALI,
    "_ISARET": _ISARET,
    "_TAKIP": _TAKIP,
    "_PAYLAS": _PAYLAS,
    "_MAKBUZ": _MAKBUZ,
    "_ANLAT": _ANLAT,
    "_YAPISAL": _YAPISAL,
}


def _ciplak(sozluk: tuple[str, ...]) -> set[str]:
    """Tek kelimelik ilkel biçimler — çok kelimeli FRAZLAR (`"yol acti"`,
    `"nasil hesaplandi"`) hariç. ⚠ `strip()` ÖNCE: `_YAPISAL`'daki `"ilk "`/
    `"top "` gibi SONDA boşluklu tek-kelime girdileri (eşleşme sınırı için
    böyle yazılmış) çok-kelimeli sanıp kaçırmamak için — ölçülen ilk yazım
    hatası buydu, boşluk kırpılmadan `" " not in s` her ikisini de "frazmış"
    gibi eledi."""
    return {s.strip() for s in sozluk if " " not in s.strip()}


# Çıplak soru sözcükleri: tam eşitlik yasak. Çok-kelimeli türevleri
# (`_NEDEN` içindeki "yol acti" gibi) zaten birer FRAZ'dır, bir cube sinonimi
# olarak görülmesi beklenmez — yalnız TEK KELİMELİK ilkel biçimler kontrol
# edilir (asıl ölçülen kusurun şekli buydu).
_CIPLAK_SORU_SOZCUKLERI = _ciplak(_NEDEN)

# 🔴🔴 FAZ 3.2 — TÜM sözlüklerin birleşimi, HANGİ sözlükten geldiği bilgisiyle
# (bir çakışma bulununca kullanıcıya/geliştiriciye "hangi konuşma türünü
# çaldığını" söylemek için — yalnız "bir yerde çakışma var" demek yetmez).
_CIPLAK_KAYNAKLI: dict[str, str] = {}
for _ad, _soz in _SOZLUKLER.items():
    for _kelime in _ciplak(_soz):
        _CIPLAK_KAYNAKLI.setdefault(_kelime, _ad)


def test_CIPLAK_SORU_SOZCUGU_SINONIM_DEGIL(schema):
    ihlaller: list[str] = []
    for c in schema["cubes"]:
        for kaynak in ("dimension_synonyms", "measure_synonyms"):
            for alan, syns in (c.get(kaynak) or {}).items():
                for s in syns or []:
                    plain = str(s).rstrip("!").strip().lower()
                    if plain in _CIPLAK_SORU_SOZCUKLERI:
                        ihlaller.append(f"{c['name']}.{alan} ← {s!r}")
    assert not ihlaller, (
        "🔴 Çıplak soru sözcüğü (neden/sebep/niye/…) bir cube sinonimi olarak "
        f"kayıtlı — ürün genelinde nedensel takip sorularını çalar: {ihlaller}"
    )


def test_HICBIR_KONUSMA_KALIBI_SOZLUGU_SINONIM_DEGIL(schema):
    """🔴🔴 FAZ 3.2 — ASIL GENELLEŞTİRİLMİŞ KAPI. `_NEDEN` tek örnek; bu test
    `followup.py`'nin DOKUZ konuşma-kalıbı sözlüğünün TAMAMını tarar. Bir cube
    sinonimi bunlardan HERHANGİ BİRİNİN çıplak üyesiyle çakışırsa, o konuşma
    türünün TAMAMI o küpte/o alanda sessizce bir kırılım isteğine döner —
    `_NEDEN`'de ölçülen kusurun AYNISI, yalnız başka bir sözlükte."""
    ihlaller: list[str] = []
    for c in schema["cubes"]:
        for kaynak in ("dimension_synonyms", "measure_synonyms"):
            for alan, syns in (c.get(kaynak) or {}).items():
                for s in syns or []:
                    plain = str(s).rstrip("!").strip().lower()
                    kaynak_sozluk = _CIPLAK_KAYNAKLI.get(plain)
                    if kaynak_sozluk:
                        ihlaller.append(
                            f"{c['name']}.{alan} ← {s!r} (followup.{kaynak_sozluk})")
    assert not ihlaller, (
        "🔴 Bir konuşma-kalıbı sözlüğünün çıplak üyesi bir cube sinonimi olarak "
        f"kayıtlı — o konuşma türü ürün genelinde çalınıyor: {ihlaller}"
    )


def test_KAPININ_KENDISI_BOS_DEGIL():
    """⚠ Ölçüm önce: blocklist gerçekten dolu mu — boşsa kapı sessizce her şeyi geçirirdi."""
    assert len(_CIPLAK_SORU_SOZCUKLERI) >= 5, (
        f"⊘ `followup._NEDEN`'den türeyen çıplak sözcük kümesi beklenenden küçük: "
        f"{_CIPLAK_SORU_SOZCUKLERI}"
    )


def test_GENELLESTIRILMIS_KAPI_DOKUZ_SOZLUGU_TASIR():
    """⚠ FAZ 3.2'nin kendi ölçümü: birleşim kümesi `_NEDEN`'den KESİNLİKLE daha
    büyük olmalı — değilse `_SOZLUKLER` sessizce daralmış ya da genişleme hiç
    işlememiş demektir (kapı kendi genişlediğini KANITLAMALI, varsaymamalı)."""
    assert len(_SOZLUKLER) == 9, f"⊘ Sözlük sayısı beklenenden farklı: {sorted(_SOZLUKLER)}"
    assert len(_CIPLAK_KAYNAKLI) > len(_CIPLAK_SORU_SOZCUKLERI), (
        "⊘ Birleşim kümesi yalnız `_NEDEN` kadar — genelleştirme etkisiz kalmış")
    # Her sözlükten en az bir çıplak kelime KATKI VERMELİ — biri hiç katkı
    # vermiyorsa (ör. tamamı çok-kelimeli fraz), kapı o sözlüğü hiç GÖRMÜYOR
    # demektir ve bu sessizce olmamalı.
    kaynaklar = set(_CIPLAK_KAYNAKLI.values())
    eksik = set(_SOZLUKLER) - kaynaklar
    assert not eksik, (
        f"⊘ Şu sözlükler hiç tek-kelimelik girdi katmadı — kapı onları göremiyor "
        f"(gerçek bir boşluk mu, yoksa hepsi çok-kelimeli mi kontrol edilmeli): {eksik}")
