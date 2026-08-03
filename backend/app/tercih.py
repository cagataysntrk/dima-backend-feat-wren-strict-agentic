"""KALICI SUNUM TERCİHİ — *"hep aylık göster"* (FAZ E, "Memories"in daraltılmış hâli).

## Kapsam neden DAR

Araştırma raporu genel bir *"Memories"* katmanı öneriyordu. İki yarısından biri bu depoda
**zaten var**: terminoloji tercihi (*"biz fire'yi kg konuşuruz"*) `SynonymOverride`'dır ve
katalog katmanında yaşar. Eksik olan yalnız **sunum** yarısıydı — ve ölçüldü:

    "hep aylık göster"                    → *"Bu takip mesajını ilişkilendiremedim"*
    "bundan sonra hep tablo olarak göster" → *"«bundan» yerine «unvan» mi demek istedin?"*

Yani kullanıcı tercihini söylüyor, sistem onu **anlamıyor bile**.

## Üç değişmez

1. **Tercih ÖLÇÜ/CUBE seçimine karışmaz.** Saklanan şey bir *görünüm* kararıdır
   (granülerlik, tablo/grafik). Bir tercihin *hangi ölçü* sorusuna karışması,
   kullanıcının sormadığı bir raporu **onun kendi ayarı gibi** göstermek olurdu — sessiz
   yanlışın en sinsi hâli, çünkü kaynağı kullanıcının kendi geçmiş cümlesidir.
2. **Tercih SESSİZ uygulanmaz.** Uygulandığı her turda cevap bunu söyler ve nasıl
   kaldırılacağını yazar. Sessiz bir tercih, aylar sonra *"bu rapor neden aylık?"*
   sorusunu cevapsız bırakır.
3. **Tercih YAZMAK bir yazmadır** → Faz H'nin onay kademesinden geçer. Bir faz önce
   *"onaysız hiçbir yazma"* denip burada muafiyet açmak, bu deponun tekrar tekrar
   ölçtüğü kusur sınıfı olurdu: **beyan var, kod onu tanımıyor.**

## Hedef DEĞERLER buranın malı DEĞİL

`granularity` `cube_router._time_gran`'dan, `view` çağıranın `_viz_hint`'inden gelir.
Bu modül yalnız **KALICILIK İŞARETİNİ** (*"hep"*, *"bundan sonra"*) sahiplenir; hedefi
yeniden çözmeye kalksaydı, aynı kuralın ikinci sahibi doğardı.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.cube_router import _time_gran, kalip_spanlari, span_ayikla

#: Kapalı anahtar kümesi — serbest metin DEĞİL. Aksi hâlde depo, tanımsız bir "model
#: belleği"ne dönüşür ve *"orada ne yazıyor?"* sorusu cevaplanamaz olurdu.
ANAHTAR_GRAN = "granularity"
ANAHTAR_GORUNUM = "view"
ANAHTARLAR = (ANAHTAR_GRAN, ANAHTAR_GORUNUM)

#: KALICILIK İŞARETİ. Tek başına yetmez — hedef de gerekir (iki kanatlı kapı, `eylem.py`
#: ile aynı disiplin): *"hep"* geçen ama görünüm hedefi olmayan bir cümle tercih değildir.
_KALICI_ISARET = ("hep", "her zaman", "bundan sonra", "bundan boyle", "surekli",
                  "artik hep", "varsayilan olarak", "varsayilan olsun", "hep boyle")

#: İnsan-okur etiketler — kullanıcı NEYİ onayladığını okumalı (`ort_oee` gibi iç ad yok).
_GRAN_ETIKET = {"day": "günlük", "week": "haftalık", "month": "aylık",
                "quarter": "çeyreklik", "year": "yıllık"}
_GORUNUM_ETIKET = {"table": "tablo", "pivot": "pivot tablo", "chart": "grafik",
                   "line": "çizgi grafik", "bar": "sütun grafik", "pie": "pasta grafik",
                   "heatmap": "ısı haritası"}


@dataclass(frozen=True)
class Tercih:
    anahtar: str
    deger: str
    etiket: str            # insan-okur ("aylık")


def kalici_isaret_var(q_norm: str) -> bool:
    """Tek gerçek kaynak `kalip_spanlari` — `tespit` ile AYNI eşleşme. İki ayrı
    eşleştirici (biri `_syn_hit`, biri span) zamanla ayrışır ve *"işaret var mı?"*
    sorusuna iki farklı cevap üretirdi."""
    return bool(kalip_spanlari(q_norm, _KALICI_ISARET))


def tespit(q_norm: str, *, gorunum: str | None = None) -> Tercih | None:
    """Bu cümle KALICI bir sunum tercihi mi? — deterministik, sıfır LLM.

    `None` = tercih değil (akış değişmez). Kapı dar: kalıcılık işareti **ve** hedef
    birlikte gerekir. Yalnız işaret aransaydı *"hep en yüksek fire"* bir tercih
    sanılırdı; yalnız hedef aransaydı **her** aylık soru bir tercihe dönüşürdü.
    """
    spanlar = kalip_spanlari(q_norm, _KALICI_ISARET)
    if not spanlar:
        return None
    # İŞARETİ ÖNCE AYIKLA, SONRA HEDEFİ SOR (D1'in "tam kaplama" ilkesi; ölçüldü):
    # *"her zaman çalışan makineler"* → `_time_gran` işaretin kendi `zaman` sözcüğünü
    # bir zaman kovası sanıp granülerlik üretiyor ve meşru bir soru KALICI TERCİH
    # sanılıyordu. Kalıp ifadenin parçaları hedef anlamı taşımaz.
    kalan = span_ayikla(q_norm, spanlar)
    gran = _time_gran(kalan)
    if gran and gran in _GRAN_ETIKET:
        return Tercih(ANAHTAR_GRAN, gran, _GRAN_ETIKET[gran])
    if gorunum:
        return Tercih(ANAHTAR_GORUNUM, gorunum,
                      _GORUNUM_ETIKET.get(gorunum, gorunum))
    return None


def ozet(t: Tercih) -> str:
    if t.anahtar == ANAHTAR_GRAN:
        return f"Bundan sonra raporları **{t.etiket}** göstereyim mi?"
    return f"Bundan sonra raporları **{t.etiket}** olarak göstereyim mi?"


def etiketle(anahtar: str, deger: str) -> str:
    """Depodaki bir kaydın insan-okur karşılığı (liste ucu + uygulama notu için)."""
    if anahtar == ANAHTAR_GRAN:
        return _GRAN_ETIKET.get(deger, deger)
    return _GORUNUM_ETIKET.get(deger, deger)


def uygula(cq: dict | None, q_norm: str, tercihler: dict[str, str],
           *, gorunum: str | None,
           zaman_boyutu: str | None = None) -> tuple[dict | None, str | None, str | None]:
    """Saklı tercihi rapora uygular. Döner: (cube_query, view_hint, NOT).

    **Sessiz değil**: uygulandıysa üçüncü değer kullanıcıya gösterilecek cümledir.

    **Sormadığını ezmez**: soru kendi granülerliğini/görünümünü söylüyorsa tercih
    DEVREYE GİRMEZ. Tercihin açık isteği ezmesi, kullanıcının o turda yazdığı şeyi
    görmezden gelmek olurdu.
    """
    notlar: list[str] = []
    gran_tercih = tercihler.get(ANAHTAR_GRAN)
    if (gran_tercih and cq and not cq.get("timeDimensions")
            and _time_gran(q_norm) is None):
        # Zaman boyutunun adı BURANIN malı değil — `yoy.time_dim_of` sahibidir ve
        # çağıran onu verir. Burada "tarih" diye varsaymak, cube'a göre değişen bir
        # gerçeği sabitlemek olurdu.
        cq = {**cq, "timeDimensions": [{"dimension": zaman_boyutu or "tarih",
                                        "granularity": gran_tercih}]}
        notlar.append(f"“{etiketle(ANAHTAR_GRAN, gran_tercih)} göster” tercihiniz uygulandı")
    gorunum_tercih = tercihler.get(ANAHTAR_GORUNUM)
    if gorunum_tercih and not gorunum:
        gorunum = gorunum_tercih
        notlar.append(f"“{etiketle(ANAHTAR_GORUNUM, gorunum_tercih)} göster” tercihiniz uygulandı")
    if not notlar:
        return cq, gorunum, None
    return cq, gorunum, " · ".join(notlar) + " (kaldırmak için: ayarlar › tercihler)"
