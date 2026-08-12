"""🔴 `§B10` / `§19` — **SKILLS: metodoloji markdown'ları.**

## Neden var — ölçülmüş gerekçe (canlı, 2026-08-12)

    «geçen yıla göre ciro»               → toplam_ciro · toplam_ciro_gecen ·
                                           toplam_ciro_degisim_yuzde: 9.7   ✅ source=cube
    «geçen yıla göre ciro BÜYÜME ORANI»  → 🔴 CEVAPSIZ
    iz: garson çağrıldı — kullanılabilir bir karar dönmedi
        niyet: tür=kirilim+kiyas+trend · 🔴temsil-yok=kiyas · bilinmeyen=buyume,orani

⊙ **Oran zaten hesaplanıyordu**; garson onun *adını* bilmiyordu. Ve niyet nesnesi isteği
doğru okumuştu (`kiyas+trend`, `granülerlik=year`) — eksik olan bilgi değil **bağlamdı**.

## Neden route'a değil GARSONA

`CLAUDE.md`'nin en üst kuralı: *«route'a dil kuralı EKLEME… bir cümle anlaşılmıyorsa
çözüm route'u genişletmek değil devri tetiklemektir»*. Rapor aynı yeri gösteriyor
(`§36.1-5`): *«Skills (markdown) — kapalı fiil listesinin ilacı, **kod yazmadan**»*.

⚠ Ve `§38.4` dokunulmazı korunur: **fiil kümesi büyümez**. Skill yeni bir yetenek
tanımlamaz; sistemin **zaten ürettiği** bir çıktının adını söyler.

## Neden BAYRAKLI ve varsayılan KAPALI

Garsonun doğruluk ölçümü **yok** (`§26`, park edilmiş). Kazancı ölçemediğimiz bir bağlam
eklemesini varsayılan açmak, `motor_rls` ve `ossie_ithal` için **reddettiğimiz** şeyin
aynısı olurdu.

> *Ölçülemeyen bir kazancı varsayılan açmak, ölçümü bir törene çevirir.*
"""

from __future__ import annotations

import pathlib

import yaml

_KOK = pathlib.Path(__file__).parent.parent
_SKILLS = _KOK / "demo" / "skills"


def _bayrak(ad: str) -> str:
    d = yaml.safe_load((_KOK / "demo" / "packs" / "features.yml").read_text(encoding="utf-8"))
    return str(((d or {}).get("features") or {}).get(ad, ""))


def test_SKILL_DOSYASI_VAR_ve_METODOLOJI_ANLATIYOR():
    """Skill bir **iş akışıdır**, bir kelime listesi değil."""
    f = _SKILLS / "yoy-orani.md"
    assert f.is_file(), "🔴 `demo/skills/yoy-orani.md` yok"
    m = f.read_text(encoding="utf-8")
    assert "_degisim_yuzde" in m, "skill, sistemin ÜRETTİĞİ kolonu adlandırmıyor"
    assert "ölçü" in m.lower(), "skill hangi yapıyla karşılanacağını söylemiyor"
    # 🔴 Ölçülen vakanın kendisi skill'de **kanıtıyla** duruyor.
    assert "9.7" in m or "9,7" in m, (
        "skill'in gerekçesi ÖLÇÜLMÜŞ bir vakaya dayanmalı — sayısı yazılmayan bir "
        "gerekçe bir tahmindir")


def test_SKILL_YENI_FIIL_TANIMLAMIYOR():
    """🔴 `§38.4` dokunulmazı: **kapalı fiil kümesi**. Skill bir yetenek EKLEMEZ.

    ⚠ Yüklem yapısal: skill metni `plan_semasi.FIIL_ANLAMI`'nda **olmayan** büyük-harfli
    bir fiil adı ilan ediyorsa, metodoloji anlatmaktan çıkıp kayıt kurmuş demektir.
    """
    import re

    from app.plan_semasi import FIIL_ANLAMI

    m = (_SKILLS / "yoy-orani.md").read_text(encoding="utf-8")
    # `FIIL:` kalıbı — bir skill'in fiil ilan edebileceği tek biçim.
    ilan = set(re.findall(r"^\s*([A-ZÇĞİÖŞÜ]{3,}):", m, re.M))
    kacak = ilan - set(FIIL_ANLAMI)
    assert not kacak, (
        f"🔴 skill kayıtta OLMAYAN fiil ilan ediyor: {sorted(kacak)}. Skill metodoloji "
        "anlatır, yetenek tanımlamaz — fiil kümesi `§38.4` dokunulmazıdır.")


def test_KURAL_B_bayrak_KAPALIYKEN_katalog_DEGISMEZ(schema):
    """🔴 `KURAL B`: bayrak kapalıyken katalog metnine **tek bayt** eklenmez."""
    from app import katalog_metni

    metin, _ = katalog_metni.metin_ve_indeks(schema, None)
    assert "METODOLOJİ" not in metin, (
        "🔴 bayrak kapalı ama skill metni kataloga girmiş — `KURAL B` ihlali")
    assert _bayrak("skills") == "off", (
        "bayrak açılmış — açılış şartı `§26` (garson doğruluk ölçümü) ve o PARK. "
        "Kazancı ölçülmeden açmak, `motor_rls`/`ossie_ithal` için reddettiğimiz şeydir.")


def test_YUKLEYICI_DOSYALARI_GERCEKTEN_OKUYOR():
    """⊘ **Boş yeşil avı:** yükleyici hiçbir şey bulamıyorsa yukarıdaki `KURAL B` testi
    de anlamsızlaşır. Bu test yükleyicinin **gerçekten** okuduğunu doğrular."""
    from app import katalog_metni

    # Gerçek proje kökünü taklit et: `<kok>/wren-project` → `.parent.parent/skills`
    sahte = _KOK / "demo" / "wren-project"
    m = katalog_metni.skills_metni(sahte)
    assert m, (
        "⊘ yükleyici boş döndü — `demo/skills/*.md` bulunamıyor demektir ve o hâlde "
        "`KURAL B` testi hiçbir şey ölçmüyor.")
    assert "_degisim_yuzde" in m


def test_INDEKSE_DOKUNULMUYOR(schema):
    """🔴 `indeks` bir **beyaz listedir** — plan doğrulamasının sınırı.

    Skill metni bir ölçü/boyut adı eklemez, metodoloji anlatır. İndekse dokunmak,
    doğrulama sınırını bir **anlatım tercihine** bağlamak olurdu (`§B1`'in aynı dersi).
    """
    from app import katalog_metni

    _, i1 = katalog_metni.metin_ve_indeks(schema, None)
    assert i1, "⊘ indeks boş — bu test hiçbir şey ölçmüyor"

    # ⚠ İlk sürümüm 260 baytlık bir **dilime** bakıyordu ve `return metin, indeks`
    # satırını yakalayıp yanlış-kırmızı verdi — bu oturumun kendi 6 numaralı dersi
    # (*kapıyı sabit dilime bağlama*), kapının kendisinde. Doğru ölçüm **gövdedir**:
    # `if _skl …` bloğunun içinde `indeks` adına ATAMA var mı.
    import ast

    agac = ast.parse((_KOK / "app" / "katalog_metni.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(agac)
              if isinstance(n, ast.FunctionDef) and n.name == "metin_ve_indeks")
    dallar = [n for n in ast.walk(fn) if isinstance(n, ast.If)
              and "_skl" in ast.dump(n.test)]
    assert dallar, "⊘ skill dalı bulunamadı — kapı hiçbir şey ölçmüyor"
    for d in dallar:
        for n in ast.walk(d):
            if isinstance(n, ast.Assign):
                for h in n.targets:
                    assert getattr(h, "id", "") != "indeks", (
                        "🔴 skill dalı `indeks`e ATIYOR — beyaz liste yalnız katalogdan "
                        "türer; doğrulama sınırını bir anlatım tercihine bağlamak olurdu.")


def test_ACILIS_SARTI_YAZILI():
    """Bir bayrağın kapalılığı, **şartı yazılıysa** bir karardır; yoksa bir unutmadır."""
    from app.features import FLAG_REGISTRY

    a = (FLAG_REGISTRY.get("skills") or {}).get("description", "")
    assert "§26" in a, "açılış şartı (garson doğruluk ölçümü) bayrak kaydında yazılı değil"
    assert "ölçülemez" in a or "ölçüm" in a
