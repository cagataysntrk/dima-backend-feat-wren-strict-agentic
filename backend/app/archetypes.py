"""Ölçü arketip sözlüğü (ADR-0018 kaldıraç b): platform-semantiği, pack değil.

Bir metrik-arketipinin ZENGİN Türkçe eşanlamlı seti BİR KEZ burada tanımlanır; ölçü
ADI arketip anahtarıdır (`satis_tutari` → satış/ciro/gelir/hasılat/net satış…). Hangi
kaynak pack'i (mikro/logo/netsis/egemen) bu ölçüyü kullanırsa kullansın aynı zengin
sözlüğü MİRAS alır — "her pack'i sıfırdan cilalama" vergisini kaldırır (korpus kanıtı:
etiket kuralı taze pack'leri %19→%38'e çıkardı; arketipler ikinci sıçramayı hedefler).

Kural: buradaki sinonimler pack YAML'ındaki `synonyms` + display etiketiyle BİRLEŞİR
(üzerine yazmaz). Yeni bir ölçü adı standardı çıktığında buraya eklenir; tek nokta.
Sinonimler normalize EDİLMEDEN yazılır (wren_service `_norm`'lar).
"""

from __future__ import annotations

from functools import lru_cache

# Anahtar = ölçü adı (tüm kaynak pack'lerinde ortak isimlendirme). Değer = ek TR sinonimler.
MEASURE_ARCHETYPES: dict[str, list[str]] = {
    # --- Satış / gelir tarafı ---
    "satis_tutari": [
        # DİKKAT: "net satış" BURAYA GİRMEZ — o ayrı bir ölçüdür (net_satis = satış − iade).
        # Kirlilik router'ı yanlış ölçüye/yanlış veriye götürüyordu (canlı 2026-07-25 accuracy).
        "satış", "satis", "ciro", "gelir", "hasılat", "hasilat",
        "satışlar", "satislar", "satış tutarı", "satış cirosu",
        "ne sattık", "ne sattim", "satış geliri", "toplam satış", "satıştan gelen",
    ],
    "brut_satis": ["brüt satış", "brut satis", "brüt", "brut", "brüt ciro", "kdvli satış"],
    "satis_miktari": [
        "satış miktarı", "satis miktari", "satılan", "satilan", "satılan miktar",
        "kaç adet satıldı", "satış adedi", "sevk edilen", "çıkış miktarı", "satılan mal",
        # bare "miktar": "satış miktarLARI" (çoğul) "miktarı"ya uymuyordu → satis_tutari'nin
        # "satış"ı (5) kazanıyordu; "miktar" (6) altdizisi çoğul/iyelik hepsini kapsar (panel).
        "miktar",
    ],
    "satis_kdv": ["satış kdv", "satis kdv", "kdv", "hesaplanan kdv", "satış vergisi"],
    "satis_fatura_sayisi": [
        "fatura sayısı", "kaç fatura", "fatura adedi", "satış fatura sayısı",
        "kesilen fatura", "fatura sayisi",
    ],
    # --- Alım / gider tarafı ---
    "alim_tutari": [
        "alım", "alim", "alış", "alis", "alım tutarı", "alış tutarı", "mal alımı",
        "satın alma", "satin alma", "tedarik", "ne aldık", "ne aldim", "alımlar",
        "toplam alım", "alış maliyeti", "hurda alımı", "hammadde alımı",
    ],
    "alim_miktari": [
        "alım miktarı", "alis miktari", "alınan", "alinan", "alınan miktar",
        "toplanan", "giriş miktarı", "tedarik edilen", "satın alınan",
    ],
    # --- Cari / muhasebe ---
    "bakiye": [
        "bakiye", "net bakiye", "kalan", "cari bakiye", "hesap bakiyesi",
        "borç bakiyesi", "kalan borç", "güncel bakiye",
    ],
    "toplam_borc": [
        "borç", "borc", "borç toplamı", "toplam borç", "borçlar", "borclar",
        "borç tutarı", "cari borç",
    ],
    "toplam_alacak": [
        "alacak", "tahsilat", "alacak toplamı", "toplam alacak", "alacaklar",
        "alacak tutarı", "tahsil edilen", "cari alacak",
    ],
    "hareket_sayisi": [
        "hareket sayısı", "işlem sayısı", "kaç hareket", "kaç işlem", "kayıt sayısı",
        "işlem adedi",  # "adet"/"kaç" BARE çıkarıldı (panel: çarpışma makinesi)
    ],
    # --- Cari yaşlandırma (P0 cube) ---
    "net_bakiye": ["net bakiye", "açık bakiye", "bakiye", "kalan bakiye", "cari bakiye"],
    "vadesi_gecen": [
        "vadesi geçen", "vadesi gecen", "gecikmiş", "gecikmis", "gecikme",
        "muaccel", "vadesi geçmiş alacak", "geciken tahsilat", "geciken alacak",
    ],
    # --- Stok / miktar (birim-nötr çekirdek) ---
    "net_miktar": ["net miktar", "stok değişimi", "net stok", "kalan miktar"],
    # --- Kârlılık (türetilmiş — Sınıf B geldiğinde formül kazanır) ---
    # "kar!" TAM-KELİME (codebase konvansiyonu): altdizi eşleme "karşılaştır"ı
    # yakalıyordu (boyahane parti cube'undaki aynı tuzak). Kısa/çarpışan sinonimler !.
    "kar": ["kar!", "kâr!", "kazanç", "net kar", "kârımız", "karimiz", "brüt kar"],
    "kar_marji_yuzde": [
        "kar marjı", "kâr marjı", "kar oranı", "karlılık", "karlilik", "marj!",
        "kar yüzdesi", "karlılık oranı",
    ],
}


# ÇOK-DİL i18n (§7b "ayrı sakla, birleşik ara") — DOSYA-TABANLI, proper i18n konvansiyonu.
# İKİ KAPSAM, ve kapsam YAPISALDIR (hangi katmanda durduğuyla belirlenir):
#   • YEREL dil (tam sözlük): yukarıdaki MEASURE_ARCHETYPES (tr, zengin+gerekçeli) + pack
#     cube YAML. Tüm kelime dağarcığı aranır. TEK yerel dil kodda; "onlarca dil" DEĞİL.
#   • YARDIMCI dil (TEKNİK ALT-KÜME): packs/i18n/<dil>.yml DOSYALARI. Yeni dil = yeni DOSYA
#     (kod değişmez → "sonsuz Python dosyası" sorunu yok). YALNIZ küratörlü teknik/iş terimi;
#     GENEL SÖZLÜK ASLA girmez → YANLIŞ-DOST GARANTİSİ: İng. "son" (=oğul) girmez, Türkçe
#     "son" (=last) tek-anlamlı kalır, %100 kesinlik, gereksiz "bunu mu demek istediniz?" yok.
DEFAULT_LANGS: tuple[str, ...] = ("tr", "en")


@lru_cache(maxsize=1)
def _i18n() -> dict[str, dict[str, dict[str, list[str]]]]:
    """packs/i18n/<dil>.yml → {dil: {"measures": {ad: [syn]}, "dimensions": {...}}}. Dosya
    ekleyerek dil eklenir (kod değişmez). Dizin/dosya yoksa boş (deterministik çekirdek
    dosyaya bağımlı olmasın). Yerel dil (tr) burada DEĞİL — MEASURE_ARCHETYPES'te."""
    import yaml

    from app.config import get_settings
    out: dict[str, dict] = {}
    try:
        d = get_settings().resolved_project_dir().parent / "packs" / "i18n"
        for f in sorted(d.glob("*.yml")):
            data = yaml.safe_load(f.read_text()) or {}
            out[f.stem] = {"measures": data.get("measures") or {},
                           "dimensions": data.get("dimensions") or {}}
    except Exception:
        pass
    return out


def _lang_block(measure_name: str, lang: str) -> list[str]:
    """Bir ölçünün TEK dildeki sinonim bloğu. tr = yerel (MEASURE_ARCHETYPES, tam sözlük);
    gerisi packs/i18n/<lang>.yml (teknik alt-küme). Dil eklemek routing'e değil VERİYE dokunur."""
    if lang == "tr":
        return MEASURE_ARCHETYPES.get(measure_name, [])
    return _i18n().get(lang, {}).get("measures", {}).get(measure_name, [])


def synonyms_for(measure_name: str, langs: tuple[str, ...] = DEFAULT_LANGS) -> list[str]:
    """Ölçü adının arketip sinonimleri — AKTİF dillerin UNION'ı (§7b). Sıra = dil önceliği
    (yerel dil önce). Yoksa boş liste. langs değişince (ör. ("zh","de")) yapı aynı kalır."""
    out: list[str] = []
    for lang in langs:
        out += _lang_block(measure_name, lang)
    return out


def dim_synonyms_for(dim_name: str, langs: tuple[str, ...] = DEFAULT_LANGS) -> list[str]:
    """Bir boyutun EK-DİL sinonimleri (yerel dil pack cube YAML'ında; bu yalnız yardımcı-
    dil i18n katmanı → packs/i18n/<lang>.yml). Aktif dillerin UNION'ı, sıra = öncelik.
    tr atlanır (yerel = YAML). langs esnek (N-dil); yeni dil = yeni dosya."""
    out: list[str] = []
    for lang in langs:
        if lang == "tr":
            continue  # yerel dil boyut sinonimi pack cube YAML'ında
        out += _i18n().get(lang, {}).get("dimensions", {}).get(dim_name, [])
    return out
