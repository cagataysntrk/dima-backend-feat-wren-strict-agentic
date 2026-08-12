#!/usr/bin/env python3
"""🔴 `§G.2` — **BELGE DİZİNİ: şişkinliğin çaresi silmek değil, GEZİNMEK.**

## Ölçülmüş şikâyet

Kullanıcı: *«`MIMARI.md` aşırı şişti, o yüzden kullanılamıyor.»* Ölçüldü (2026-08-12):

```
MIMARI.md  : 5.652 satır · 262 başlık  (h2 16 · h3 123)
CLAUDE.md  :   433 satır ·  21 başlık  (h2  8 · h3  10)
```

🆚 **Asıl sorun satır sayısı değil, `123` h3'ün TEK DÜZLEMDE durmasıdır.** 5.652 satır bir
mimari otorite için fazla değil; **123 eşit görünen başlık** arasında aradığını bulamamak
fazla. Bir okuyucu *«RLS kararı nerede»* diye sorduğunda cevabı **kaydırarak** arıyor.

## Neden SİLMİYORUZ

`MIMARI.md §10`: *«kapananlar işaretlenir, silinmez»*. Ve bu deponun kendi dersi:
㊿ **özeti korumak, özetlediğini korumaz** — bir mimari kararın gerekçesi kısaltılırsa
altı ay sonra o karar **yeniden tartışılır**. Şişkinliğin bedeli gezinmede; çaresi de
orada olmalı.

## Ne üretir

`## ` başlıklarını **satır numarasıyla** listeler ve her birinin altındaki `### ` sayısını
yazar. Böylece okuyucu **önce bölümü**, sonra bölüm içinde başlığı seçer — 123 eşit
seçenek yerine **16 seçenek + içinde arama**.

⚠ **Dizin ELLE YAZILMAZ.** Elle yazılan bir dizin, belgenin ilk düzenlemesinde bayatlar
ve *«burada yok»* diye yanlış yönlendirir — 🆍 *kendini temizlemeyen bir liste bir perdedir*.
Bu koşucu üretir, `test_g_belge_dizini_taze.py` **bayatlamasını yasaklar**.

## Kullanım

    python lab/belge_dizini.py                 # üretir, YAZMAZ (varsayılan)
    python lab/belge_dizini.py --yaz           # belgeye işler (işaretler arasına)
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

_KOK = pathlib.Path(__file__).resolve().parents[1]

#: Dizin bu iki işaret **arasına** yazılır; dışına dokunulmaz. İşaretler yoksa koşucu
#: yazmaz ve **söyler** — bir belgeye izinsiz yer açmak, onu düzenlemekle aynı şey değil.
BAS, SON = "<!-- DIZIN:BAS -->", "<!-- DIZIN:SON -->"

#: Dizinlenen belgeler. ⚠ `CLAUDE.md` **bilerek yok**: 21 başlıkla zaten gezilebiliyor
#: ve bir dizin orada **gürültü** olurdu. *Her şeyi işaretleyen bir ölçüt hiçbir şeyi
#: işaretlemez.*
BELGELER = (
    "MIMARI.md",
    # ⟳ 2026-08-13 — öngörü katmanı kararı **52 bölüme** ulaştı ve raporun KENDİ teşhis
    # ettiği hastalığa yakalandı (*«123 h3 tek düzlemde, o yüzden kullanılamıyor»*).
    # Kendi ilacımızı kendimize uyguluyoruz.
    "../belgeler/plan/2026-08-12_ONGORU-KATMANI-KARARI.md",
)

_H2 = re.compile(r"^## +(.+?)\s*$")
_H3 = re.compile(r"^### +(.+?)\s*$")


def _capa(baslik: str) -> str:
    """GitHub-uyumlu çapa: küçült, alfanümerik-dışını at, boşluk → tire.

    ⚠ ⑧ **TR büyük harf — ve ilk yazımım YANLIŞTI.** `ı`'yı `i`'ye çevirmiştim; oysa
    GitHub çapayı **yalnız küçültür**, `ı`'yı korur. Yani ürettiğim bağlantı
    (`…başliklar`) belgedeki çapaya (`…başlıklar`) **hiç gitmezdi** — dizin görünür
    olur, tıklanmazdı. *Bir dizinin bağlantısı da bir vaattir* 🆈.
    ⊙ `İ`.lower() birleşik nokta (`U+0307`) üretir; GitHub da öyle yapar, ama biz onu
    **atıyoruz** çünkü belgedeki çapa `İ`'siz yazılıyor.
    """
    s = baslik.lower().replace("̇", "")
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return re.sub(r"\s+", "-", s.strip())


def uret(metin: str) -> str:
    """Belge metninden dizin bloğunu üretir. **Saf fonksiyon** — dosya okumaz."""
    satirlar = metin.splitlines()
    bolumler: list[tuple[int, str, list[str]]] = []
    icinde = False
    for i, s in enumerate(satirlar, 1):
        # 🔴 ㉛ **DİZİN KENDİNİ SAYMAZ.** İlk yazımım blok içindeki `## 🧭 DİZİN`
        # başlığını da bölüm sanıyordu; her yazımda satır sayısı değişiyor, dizin
        # **hiçbir zaman tazelenmiş sayılmıyordu** — kendi kuyruğunu kovalayan bir kapı.
        if BAS in s:
            icinde = True
        if icinde:
            if SON in s:
                icinde = False
            continue
        m2 = _H2.match(s)
        if m2:
            bolumler.append((i, m2.group(1), []))
            continue
        m3 = _H3.match(s)
        if m3 and bolumler:
            bolumler[-1][2].append(m3.group(1))
    out = [BAS, "", "## 🧭 DİZİN — *üretilir, elle yazılmaz* (`lab/belge_dizini.py`)", ""]
    out.append(f"⊙ **{len(satirlar)} satır · {len(bolumler)} bölüm · "
               f"{sum(len(h) for _l, _b, h in bolumler)} alt başlık.** Şişkinliğin çaresi "
               "silmek değil **gezinmek**: önce bölümü seç, sonra bölüm içinde ara.")
    out.append("")
    out.append("| # | bölüm | satır | alt başlık |")
    out.append("|---|---|---|---|")
    for n, (satir, baslik, alt) in enumerate(bolumler, 1):
        temiz = baslik.replace("|", "\\|")
        out.append(f"| {n} | [{temiz}](#{_capa(baslik)}) | `{satir}` | {len(alt)} |")
    out += ["", SON]
    return "\n".join(out)


def kos(*, yaz: bool = False) -> dict:
    rapor: dict[str, dict] = {}
    for ad in BELGELER:
        p = _KOK / ad
        metin = p.read_text(encoding="utf-8")
        blok = uret(metin)
        if BAS not in metin or SON not in metin:
            rapor[ad] = {"durum": "işaret YOK", "yazildi": False, "satir": len(blok.splitlines())}
            continue
        # 🔴 **SABİT NOKTA.** Blok belgenin BAŞINDA durduğu için kendi uzunluğu
        # aşağıdaki her satır numarasını kaydırır. İki geçiş yeter (blok boyu yalnız
        # bölüm SAYISINA bağlı, o da geçişler arası değişmez), ama beşe kadar döneriz
        # ve **oturmazsa söyleriz** — sessizce yanlış numara basmaktansa.
        yeni = metin
        for _ in range(5):
            blok = uret(yeni)
            aday = re.sub(re.escape(BAS) + r".*?" + re.escape(SON), lambda _m: blok,
                          yeni, flags=re.S)
            if aday == yeni:
                break
            yeni = aday
        else:
            rapor[ad] = {"durum": "OTURMADI", "yazildi": False,
                         "satir": len(blok.splitlines())}
            continue
        rapor[ad] = {"durum": "taze" if yeni == metin else "BAYAT",
                     "yazildi": False, "satir": len(blok.splitlines())}
        if yaz and yeni != metin:
            p.write_text(yeni, encoding="utf-8")
            rapor[ad]["yazildi"] = True
    return rapor


def main(argv: list[str] | None = None) -> int:
    a = argparse.ArgumentParser(description="Belge dizini — üretir (§G.2)")
    a.add_argument("--yaz", action="store_true", help="belgeye işle (varsayılan: yalnız ölç)")
    ns = a.parse_args(argv)
    r = kos(yaz=ns.yaz)
    for ad, d in r.items():
        print(f"{ad}: {d['durum']} · dizin {d['satir']} satır · "
              f"{'YAZILDI' if d['yazildi'] else 'yazılmadı'}")
    if any(d["durum"] == "işaret YOK" for d in r.values()):
        print(f"\n⊙ Belgeye `{BAS}` / `{SON}` işaretleri konmalı; koşucu kendiliğinden "
              "yer açmaz.", file=sys.stderr)
    return 0


if __name__ == "__main__":                             # pragma: no cover
    raise SystemExit(main())
