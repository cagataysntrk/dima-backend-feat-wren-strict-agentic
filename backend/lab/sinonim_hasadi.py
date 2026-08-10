"""🔴🔴 `C2` — **ÇEVRİMDIŞI SİNONİM HASADI**: liste elle yazılmaz, **kullanımdan** toplanır.

    python lab/sinonim_hasadi.py            # aday kuyruğu üret (SIFIR LLM, sıfır API)
    python lab/sinonim_hasadi.py --kapi     # C5 şartları korunuyor mu

## Kullanıcının kuralı, ve neden bu alet onun uygulaması

> *"Tek tek sinonim yazmak aptallık."*

Doğru — ama ters yön *"hiç yazma"* değil: **LLM Türkçeyi bilir, senin şirketini bilmez.**
`fire`ye burada `zayiat` denmesi bir **dil** olgusu değil bir **yerel sözleşmedir**; daha
nettir `iade → şikâyet`, ki o bir eşanlam bile değil bir **iş kuralıdır**. Ölçülmüş
bedeli var: sözlüksüz dönemde *"verimlilik"* soran bir kullanıcı için **9/9 Intent
çağrısı `{"cube":null}`** döndü — oylama uyuşmazlığı değil **aday yokluğu**.

⊙ Bu yüzden doğru iş listeyi **kaldırmak** değil, **kim yazacağını** değiştirmek:

| ❌ bugün | ✅ burada |
|---|---|
| insan katalogda oturup eşanlam üretir | sistem **kendi bilmediği kelimeleri** biriktirir |
| tahmin edilen kelimeler | **kullanılan** kelimeler, sıklık sıralı |
| her soruda LLM | 🔴 **sıcak yolda SIFIR** — bu alet çevrimdışı koşar |

## Neden sıcak yolda sıfır

Girdi **zaten yazılıyor**: `interaction_log.uncovered_words` her turda
`cube_router.partial_unknowns()` çıktısını kaydediyor. Yani *"sistemin bilmediği
kelimeler"* listesi **kullanım tarafından** ve **bedava** üretiliyor; bu alet onu
yalnız **okur**.

⚠ Ve `§4d`'nin sert sınırı: aday kuyruğu **canlıya inmez**. `_apply_synonym_overlays`
yalnız `approved=True` satırları uygular — bir LLM hatası kataloğu **sessizce**
değiştiremez.

## 🔴 `C5` — üç sert şart, ve üçü de burada KOD

| şart | neden |
|---|---|
| **çok eşleşme → kuyruğa GİRMEZ** | ≥2 katalog terimine işaret eden kelime bir sinonim değil bir **belirsizliktir**; sinonim yazmak `bakiye`nin ₺11,86 milyonluk seçimini **kalıcı** yapardı |
| **onaysız canlıya inmez** | mekanizma zaten kurulu; bu alet yalnız **kuyruk** yazar |
| **«hiçbiri» bir başarısızlık değildir** | kelime gerçekten hiçbir şeyin eşanlamı değilse doğru cevap *«hiçbiri»*dir ve o bir **menü boşluğu** sinyalidir (`B-6`), sinonim borcu değil |

*Bir sözlüğü kullanımdan yazmak, onu tahminden yazmaktan yalnız ucuz değil, **daha
doğrudur**: kullanılmayan bir eşanlam hiçbir zaman ölçülemez.*
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

KUYRUK_YOLU = pathlib.Path(__file__).resolve().parent / "reports" / "sinonim_adaylari.md"

#: Bir kelimenin kuyruğa girmesi için asgari görülme sayısı. **Tek görülen bir kelime
#: bir örüntü değil bir olaydır** — ve tek olaydan sözlük yazmak, gürültüyü kalıcı kılar.
ASGARI_SIKLIK = 2

#: 🔴 `C5/1` — bu sayıdan çok sahibi olan kelime **belirsizliktir**, sinonim değil.
AZAMI_SAHIP = 1

#: 🔴🔴 **KAYDEDİLMİŞ KELİMEYE GÜVENİLMEZ — SORU YENİDEN ÇÖZÜLÜR.**
#:
#: İlk hasat canlı kütükten şunları getirdi: `nda` **38** · `baz` **29** · `duru` **16**.
#: Bunlar kelime değil **PARÇA**dır; kaynağı `partial_unknowns`'ın eski, Türkçe
#: harflerden bölen hâli (`§M7` düzeltti). Yani hasat, düzeltilmiş bir sistemin
#: **düzeltilmeden önceki** çıktısını okuyordu.
#:
#: ⊙ İlk çözümüm bir **tarih penceresiydi** — ve yanlıştı: parçalar pencereden sonra da
#: sürdü, ve pencereyi sayılar güzelleşene kadar kaydırmak **ölçümü cevaba uydurmak**
#: olurdu. Tarih tahmin etmek, bilinmeyeni bilinir sanmaktır.
#:
#: 🔴 Doğru kök: kütük **soruyu da** saklıyor. Kaydedilmiş kelimeye güvenmek yerine
#: `partial_unknowns` **bugünkü kuralla yeniden koşulur**. Böylece hasat her zaman
#: sistemin **bugününü** ölçer, geçmişini değil — ve bir sonraki morfoloji düzeltmesi
#: bu aleti kendiliğinden düzeltir.
#:
#: *Bir kaydı yeniden hesaplayabiliyorsan, ona güvenmek bir tercihtir — ve bayat
#: olabilecek bir tercihtir.*
#:
#: İlk hasat canlı kütükten şunları getirdi: `nda` **38** · `baz` **29** · `duru` **16**
#: · `nas` **13** · `ster` **10**. Bunlar kelime değil **PARÇA**dır ve kaynağı bilinen
#: bir kusurdur: `partial_unknowns` eskiden Türkçe harflerden bölüyordu ve 769 turluk
#: bir ölçümde **196 satırın 115'i (%58,7)** parçaydı. `§M7` bunu **düzeltti** — ama
#: kütükteki eski satırlar **olduğu yerde duruyor**.
#:
#: ⊙ Yani hasat, düzeltilmiş bir sistemin **düzeltilmeden önceki** çıktısını okuyordu.
#: Bu, bu deponun üç kez ödediği sınıfın aynısı (*"ölçüm aracı bayat şemadan okuyordu"*)
#: ve buradaki kılığı daha sinsi: veri bayat değil, **veriyi üreten kural** bayat.
#:
#: ⚠ Çözüm parçaları elemek DEĞİL — bir kelimenin parça olup olmadığına karar veren bir
#: liste yazmak, `§M7`'nin çözdüğü işi ikinci kez ve daha kötü yapmak olurdu. Çözüm
#: **pencereyi beyan etmek**: yalnız düzeltmeden SONRAKİ satırlar okunur.
#:
#: *Bir ölçümün penceresi yoksa, ölçtüğü şey sistemin bugünü değil bütün geçmişidir.*



def _sorulari_oku() -> list[str]:
    """`interaction_log.question` → ham sorular. Tablo yoksa boş.

    ⚠ `uncovered_words` sütunu **okunMAZ**: o, kaydedildiği günün kuralının çıktısıdır.
    """
    try:
        from sqlmodel import select

        from control_plane.db import get_session
        from control_plane.models import InteractionLog
    except Exception:                                        # noqa: BLE001
        return []
    with next(get_session()) as oturum:                      # type: ignore[call-overload]
        return [str(q) for q in oturum.exec(select(InteractionLog.question)).all() if q]


def eslesmeleri_oku() -> dict[str, dict[str, int]]:
    """🔴🔴 `C3-D` — **KANITLI ADAYLAR: garsonun ÇÖZDÜĞÜ eşlemeler.**

    Hasadın bugüne kadarki tek girdisi *"hangi kelime bilinmiyordu"*ydu — yani bir
    **eksiklik listesi**. Ama sistem her turda eksikliğin **karşılığını da** buluyor:
    garson `zayiat`ı `toplam_fire_kg`'ye çeviriyor ve `§C3-D` bunu **çıkarıp ize
    yazıyor** (`ters-yön eşlemesi: «zayiat» → `toplam_fire_kg``).

    ⊙ Fark büyük: *"`zayiat` bilinmiyor"* bir **soru**dur; *"`zayiat` = `toplam_fire_kg`
    ve bu 14 kez böyle çözüldü"* bir **cevaptır**. İlki bir insanın oturup düşünmesini
    ister, ikincisi yalnız **onay** ister.

    ⚠ Kaynak `trace_json` ve sütun **zaten var** — bir göç (migration) gerekmedi. İz bu
    deponun makbuzudur; makbuzu okumak yeni bir depo kurmaktan iyidir.

    Döner: `{kelime: {katalog_adi: kaç_kez}}`.
    """
    import json as _json
    import re as _re

    try:
        from sqlmodel import select

        from control_plane.db import get_session
        from control_plane.models import InteractionLog
    except Exception:                                        # noqa: BLE001
        return {}
    from app.cube_router import TERIM_IZ_ONEKI

    desen = _re.compile(_re.escape(TERIM_IZ_ONEKI) + r"«(.+?)» → `(.+?)`")
    out: dict[str, dict[str, int]] = {}
    with next(get_session()) as oturum:                      # type: ignore[call-overload]
        for ham in oturum.exec(select(InteractionLog.trace_json)).all():
            if not ham or TERIM_IZ_ONEKI not in str(ham):
                continue
            try:
                izler = _json.loads(ham)
            except Exception:                                # noqa: BLE001
                continue
            for iz in izler if isinstance(izler, list) else []:
                m = desen.search(str(iz))
                if m:
                    out.setdefault(m.group(1), {})
                    out[m.group(1)][m.group(2)] = out[m.group(1)].get(m.group(2), 0) + 1
    return out


def eslesme_sinifi(kelime: str, hedefler: dict[str, int], schema: dict) -> str:
    """Kanıtlı bir eşlemenin sınıfı — ve `C5`'in üç sert kuralı **burada da** geçerli.

    * 🔴 **çelişkili**: aynı kelime farklı turlarda farklı adlara çözülmüşse bu bir
      sinonim değil bir **belirsizliktir**. Onu sözlüğe yazmak, `bakiye`'nin ₺11,86
      milyonluk seçimini **kalıcı** yapmakla aynı hatadır.
    * ⚠ **seyrek**: tek görülen bir eşleme bir örüntü değil bir **olaydır**.
    * ✅ **aday**: tutarlı ve yeterince görülmüş → onaya hazır.

    ⚠ Ve `siniflandir` yine sorulur: kelimenin katalogda **≥2 sahibi** varsa eşleme
    tutarlı görünse bile kuyruğa **girmez**.
    """
    if len(hedefler) > 1:
        return "celiskili"
    if sum(hedefler.values()) < ASGARI_SIKLIK:
        return "seyrek"
    sinif, _sahipler = siniflandir(kelime, schema)
    return "aday" if sinif == "aday" else sinif


def siniflandir(kelime: str, schema: dict) -> tuple[str, list[str]]:
    """Kelime **aday** mı, **belirsizlik** mi, **menü boşluğu** mu? → `(sınıf, sahipler)`.

    🔴 `C5`'in üç şartının karar noktası burasıdır ve üçü de bir **sınıf** üretir —
    hiçbiri sessizce elenmez. *Elenen bir kelime, elendiği söylenmediği sürece
    kaybolmuş bir sinyaldir.*
    """
    from app import cube_router

    sahipler = [str(c.get("name")) for c, _m in
                cube_router.measure_cube_candidates(kelime, schema)]
    if len(sahipler) > AZAMI_SAHIP:
        return "belirsizlik", sahipler          # `C5/1` — kuyruğa GİRMEZ
    if sahipler:
        return "zaten_var", sahipler            # route zaten çözüyor; borç değil
    return "aday", []                           # kapalı seçime gidecek tek sınıf


def hasat(schema: dict) -> dict[str, list[tuple[str, int, list[str]]]]:
    """Kütükten sıklık sıralı, sınıflandırılmış hasat. **Sıfır LLM.**"""
    from app import cube_router

    sayac: collections.Counter[str] = collections.Counter()
    for soru in _sorulari_oku():
        # 🔴 BUGÜNKÜ kuralla yeniden çözülür — kaydedilmiş kelime okunmaz.
        bilinmeyen, _ = cube_router.partial_unknowns(soru, schema)
        sayac.update(str(k) for k in bilinmeyen if str(k).strip())
    out: dict[str, list[tuple[str, int, list[str]]]] = collections.defaultdict(list)
    for kelime, n in sayac.most_common():
        if n < ASGARI_SIKLIK:
            out["seyrek"].append((kelime, n, []))
            continue
        sinif, sahipler = siniflandir(kelime, schema)
        out[sinif].append((kelime, n, sahipler))
    return dict(out)


def rapor(h: dict) -> str:
    sat = ["# Sinonim aday kuyruğu — **çevrimdışı hasat** (`C2`)", "",
           "⏱ Sorular kütükten okunur, **bilinmeyen kelimeler BUGÜNKÜ kuralla yeniden "
           "hesaplanır** — kaydedilmiş `uncovered_words` sütunu okunmaz, çünkü o "
           "kaydedildiği günün kuralının çıktısıdır.",
           "",
           "🔴 Bu bir **kuyruktur**, bir katalog değil: hiçbir satır onaylanmadan "
           "canlıya inmez (`_apply_synonym_overlays` yalnız `approved=True` uygular).",
           ""]
    baslik = {
        "aday": ("🟢 ADAY — kapalı seçime gidecek", "route çözemiyor, tek sahip de yok"),
        "belirsizlik": ("🔴 BELİRSİZLİK — kuyruğa GİRMEZ (`C5/1`)",
                        "≥2 sahip: sinonim yazmak seçimi KALICI yapardı"),
        "zaten_var": ("⚪ ZATEN ÇÖZÜLÜYOR", "route bunu buluyor — borç değil"),
        "seyrek": (f"⚪ SEYREK (n<{ASGARI_SIKLIK})",
                   "tek görülen bir kelime bir örüntü değil bir OLAYDIR"),
    }
    for anahtar in ("aday", "belirsizlik", "zaten_var", "seyrek"):
        satirlar = h.get(anahtar) or []
        b, aciklama = baslik[anahtar]
        sat += [f"## {b} — {len(satirlar)}", "", f"*{aciklama}*", ""]
        if satirlar:
            sat += ["| kelime | sıklık | sahipler |", "|---|---|---|"]
            sat += [f"| `{k}` | {n} | {', '.join(s) or '—'} |" for k, n, s in satirlar[:40]]
            if len(satirlar) > 40:
                sat.append(f"| … | | +{len(satirlar) - 40} satır daha (kırpıldı) |")
        sat.append("")
    return "\n".join(sat)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--kapi", action="store_true")
    a = ap.parse_args()

    from app.compose import compose_and_build            # noqa: F401 — şema için
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    # ⚠ İmza `gercek_dunya.py` ile aynı — ölçüm araçları şemayı **aynı** yoldan alır;
    # ikinci bir kuruluş biçimi bir gün ikisini farklı katalogla koşturur.
    schema = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                         connection_info=s.connection_dict()).schema()
    h = hasat(schema)
    KUYRUK_YOLU.parent.mkdir(parents=True, exist_ok=True)
    KUYRUK_YOLU.write_text(rapor(h), encoding="utf-8")
    print(f"Kuyruk: {KUYRUK_YOLU}")
    for k in ("aday", "belirsizlik", "zaten_var", "seyrek"):
        print(f"  {k:12} {len(h.get(k) or [])}")
    if a.kapi and (h.get("belirsizlik") and
                   any(len(s) <= AZAMI_SAHIP for _k, _n, s in h["belirsizlik"])):
        print("🔴 belirsizlik sınıfında tek sahipli kayıt var — sınıflandırma bozuk")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
