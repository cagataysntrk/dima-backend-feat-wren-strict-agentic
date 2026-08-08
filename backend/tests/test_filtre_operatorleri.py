"""FAZ 3.3 — DIŞLAMA operatörleri: `neq` / `not_in`.

Motor 12 operatör destekliyor; Python 4 üretiyordu. Eksik olan derleyici değil
**NL→operatör köprüsüydü**: `parse_cube_query` operatörü hiç denetlemiyor, `cube_sql`
iletiyor, Rust uyguluyor. Bu dosyanın ilk testi o zinciri ÇALIŞTIRARAK doğrular — plan
"12 destekleniyor" diyordu, bu test onu varsaymak yerine ölçer.

Kapatılan sessiz-yanlış: *"beyaz hariç rework kg"* bugüne kadar **BEYAZIN** rework'ünü
`source="cube"` rozetiyle döndürüyordu. Kullanıcı tam tersini istemişti.

Kural KELİME LİSTESİ DEĞİL, KONUMSALDIR (MIMARI.md §5 — kök nedeni düzelt, örneği değil):
Türkçede dışlama bir son-çekim edatıyla kurulur ve edat tümlecini İZLER. Bu yüzden edatın
eşleşen DEĞERDEN SONRA gelmesi aranır; aradaki çekim ekleri, bağlaçlar ve AYNI koordinasyona
giren diğer eşleşen değerler yutulur. Ek zinciri için Faz 0.4'ün `_SUFFIX_CHAIN_RE`'si
yeniden kullanılır — aynı dilbilgisi kuralının ikinci bir listeye kopyalanmaması için.
"""

from __future__ import annotations

import pytest

from app import cube_router

# 🔴 `M-6` — **ÜÇÜNCÜ KOPYA BURADAYDI.** Bu liste elle yazılmıştı ve aynı küme
# `app/intent_semasi.py`'de (7 üyeyle, **yanlış** bir adla) bir kez daha duruyordu.
# `MUTFAK-DENETIMI` raporunun teşhisi: *"bir kümenin üç kopyası, üç farklı küme
# demektir"* — ve gerçekten ayrışmışlardı. Artık tek sahip `app/cube_operatorleri.py`.
from app.cube_operatorleri import MOTOR_OPERATORLERI as _MOTOR

MOTOR_OPERATORLERI = list(_MOTOR)


@pytest.fixture(scope="module")
def svc():
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    return WrenService(s.resolved_project_dir(), datasource=s.datasource,
                       connection_info=s.connection_dict())


def _cq(op, value, dim="renk"):
    return {"cube": "kalite", "measures": ["toplam_rework_kg"], "dimensions": ["renk"],
            "filters": [{"dimension": dim, "operator": op, "value": value}]}


@pytest.mark.parametrize("op", MOTOR_OPERATORLERI)
def test_motor_12_operatoru_UYGULUYOR(svc, op):
    """Planın dayanak iddiası. Varsayılmaz — derlenir ve planlanır."""
    deger = (["Beyaz", "Siyah"] if op in ("in", "not_in")
             else None if op in ("is_null", "is_not_null") else "Beyaz")
    assert svc.dry_plan(svc.cube_sql(_cq(op, deger)))


def test_M6_SEMA_ile_MOTOR_ayni_kumeyi_konusur():
    """🔴 `M-6` KAPISI — sipariş fişi mutfaktan **dar ya da yanlış** olamaz.

    Ölçülen kusur: Intent-JSON şeması modele `ne` yazdırıyordu; motor `ne` **tanımıyor**
    ve turu HTTP 400 ile öldürüyordu (*"unknown variant `ne`, expected one of `eq`,
    `neq`, …"*). Ayrıca motorun 12 adından **beşi** (`neq`·`not_in`·`contains`·
    `starts_with`·`is_null`/`is_not_null`) fişte hiç yoktu — garson *"beyaz hariç"*,
    *"adı X ile başlayanlar"*, *"kodu boş olanlar"* niyetlerini **ifade edemiyordu** ve
    Discovery'ye düşüyordu. **Mutfak o yemeği yapabiliyor; menüde yazmıyordu.**

    Bu kapı, kümenin **yeniden ayrışmasını** imkânsız kılar: şema tek kaynaktan üretilir
    ve burada eşitliği ölçülür.
    """
    from app.cube_operatorleri import MOTOR_OPERATORLERI
    from app.intent_semasi import cube_query_json_schema

    sema = cube_query_json_schema({"kalite": {"measures": ["toplam_rework_kg"],
                                              "dimensions": ["renk"]}})
    bulunan: set[str] = set()

    def _gez(d):
        if isinstance(d, dict):
            if isinstance(d.get("enum"), list) and d.get("type") == "string":
                if set(d["enum"]) & set(MOTOR_OPERATORLERI):
                    bulunan.update(d["enum"])
            for v in d.values():
                _gez(v)
        elif isinstance(d, list):
            for v in d:
                _gez(v)

    _gez(sema)
    assert bulunan, "şemada operatör enum'u bulunamadı — kapı kör kalmasın"
    fazla = bulunan - set(MOTOR_OPERATORLERI)
    assert not fazla, (
        f"🔴 şema motorda OLMAYAN operatör yazdırıyor: {sorted(fazla)}. "
        "Motorun kendi hata mesajı geçerli kümeyi sayar; tek kaynak "
        "`app/cube_operatorleri.MOTOR_OPERATORLERI`.")
    eksik = set(MOTOR_OPERATORLERI) - bulunan
    assert not eksik, (
        f"🔴 motor destekliyor ama fiş yazmıyor: {sorted(eksik)}. "
        "Garson ifade edemediği niyeti Discovery'ye taşır — mutfak eksikliği değil, "
        "MENÜ eksikliği doğar.")


def test_gecersiz_operator_GURULTULU_reddedilir(svc):
    """Sessiz yutma yok: tanınmayan operatör Rust'ta patlar, `LIKE` diye bir kapı yoktur."""
    with pytest.raises(Exception) as e:
        svc.cube_sql(_cq("like", "B%"))
    assert "like" in str(e.value).lower()


@pytest.mark.parametrize("soru,beklenen", [
    ("beyaz hariç renk bazında rework kg", ("renk", "neq", "Beyaz")),
    ("beyazın dışında rework kg", ("renk", "neq", "Beyaz")),
    ("beyaz olmayan rework kg", ("renk", "neq", "Beyaz")),
    ("beyaz değil rework kg", ("renk", "neq", "Beyaz")),
    ("boyahane hariç departman bazında brüt maaş", ("departman", "neq", "Boyahane")),
    ("bekar hariç ortalama maaş", ("medeni_hal", "neq", "Bekar")),
])
def test_tek_deger_DISLAMA_neq_uretir(schema, soru, beklenen):
    r = cube_router.route(soru, schema)
    assert r, f"{soru!r} cevaplanamadı"
    dim, op, val = beklenen
    assert {"dimension": dim, "operator": op, "value": val} in r["cube_query"]["filters"], \
        r["cube_query"]["filters"]


def test_bagli_degerler_BIRLIKTE_dislanir(schema):
    """"beyaz VE siyah hariç" → `not_in`. Bağlaç zinciri edatla tümleci arasında durur;
    konumsal kural onu yutmazsa yalnız son değer dışlanır ve sonuç sessizce yanlış olur."""
    r = cube_router.route("beyaz ve siyah hariç renk bazında rework kg", schema)
    assert r
    f = next(f for f in r["cube_query"]["filters"] if f["dimension"] == "renk")
    assert f["operator"] == "not_in" and sorted(f["value"]) == ["Beyaz", "Siyah"]


def test_baglac_zinciri_BOYUT_SINIRINI_asar(schema):
    """Ölçülen hata: `renk_derinlik`te "Siyah" YOK, o yüzden ilk sürümde o boyut zinciri
    yutamıyor ve `eq Beyaz` alıyordu — kullanıcı "beyaz hariç" derken beyaz FİLTRELENİYOR,
    üstelik `renk`teki `not_in` ile ÇELİŞİYORDU. Kardeş değerler artık boyut sınırından
    bağımsız toplanıyor."""
    r = cube_router.route("beyaz ve siyah hariç renk bazında rework kg", schema)
    assert r
    for f in r["cube_query"]["filters"]:
        assert f["operator"] in ("neq", "not_in"), (
            f"{f['dimension']} dışlama sorusunda {f['operator']} aldı: {f}")


def test_KARMA_dislama_durust_RED(schema):
    """"beyaz hariç siyah" — hangi değerin hangi tarafta olduğu metinden güvenle
    çıkarılamaz. Sessizce bir yorum seçmek yerine None (ADR-0008), LLM devralır."""
    assert cube_router.route("beyaz hariç siyah rework kg", schema) is None


@pytest.mark.parametrize("soru,op", [
    ("beyaz renk rework kg", "eq"),
    ("beyaz ve siyah rework kg", "in"),
])
def test_DISLAMASIZ_davranis_degismedi(schema, soru, op):
    """SIFIR REGRESYON KAPISI — dışlama edatı yoksa eski `eq`/`in` yolu aynen çalışmalı."""
    r = cube_router.route(soru, schema)
    assert r
    f = next(f for f in r["cube_query"]["filters"] if f["dimension"] == "renk")
    assert f["operator"] == op


def test_dislamada_KIRILIM_korunur(schema):
    """`eq`te boyut düşürülür (tek değere göre gruplamak dejenere). Dışlamada geriye
    BİRDEN ÇOK değer kalır → kırılım anlamlıdır ve düşürülürse bilgi yok olur."""
    r = cube_router.route("beyaz hariç renk bazında rework kg", schema)
    assert r and "renk" in (r["cube_query"].get("dimensions") or [])


def test_edat_KAPSAM_KAPISINA_takilmaz(schema):
    """"hariç"/"dışında" ANLAŞILDI (bir operatöre çevrildi), dolgu değil. `known`a
    eklenmezse ADR-0008 kapısı doğru üretilmiş filtreyi çöpe atardı."""
    q = cube_router._norm("beyaz hariç renk bazında rework kg")
    assert cube_router.route(q, schema) is not None
    assert "haric" in q


def test_dislama_SONUCU_gercek_veride_dogru(svc, schema):
    """Uçtan uca: üretilen SQL çalıştırılır ve dışlanan değerin sonuçta OLMADIĞI ölçülür."""
    import duckdb

    from app.config import get_settings

    con = duckdb.connect(str((get_settings().connection_dict() or {}).get("path")
                             or "demo/data/boyahane.duckdb"), read_only=True)
    try:
        r = cube_router.route("beyaz hariç renk bazında rework kg", schema)
        plan = svc.dry_plan(svc.cube_sql(r["cube_query"]))
        renkler = {row[0] for row in
                   con.execute(plan.replace('boyahane."main".', "main.")).fetchall()}
        assert renkler, "boş sonuç"
        assert "Beyaz" not in renkler, f"dışlanan değer sonuçta: {renkler}"
        assert len(renkler) > 1, f"dışlama her şeyi eledi: {renkler}"
    finally:
        con.close()


def test_starts_with_BUYUK_KUCUK_HARF_duyarli(svc, schema):
    """Neden `starts_with` NL'den DOĞRUDAN üretilmiyor — ölçülmüş gerekçe.

    Motorun operatörü harf duyarlıdır; Dima'nın NL katmanı `_norm` ile küçültür. İkisini
    doğrudan bağlamak, kullanıcı "beyaz" yazdığında GÜVENLE BOŞ sonuç döndürmek demekti —
    `None`dan kötü, çünkü boş sonuç "veri yok" gibi okunur.
    """
    import duckdb

    from app.config import get_settings

    con = duckdb.connect(str((get_settings().connection_dict() or {}).get("path")
                             or "demo/data/boyahane.duckdb"), read_only=True)
    try:
        sonuc = {}
        for val in ("B", "b"):
            plan = svc.dry_plan(svc.cube_sql(_cq("starts_with", val)))
            sonuc[val] = con.execute(plan.replace('boyahane."main".', "main.")).fetchall()
    finally:
        con.close()
    assert sonuc["B"] and not sonuc["b"], (
        "starts_with artık harf duyarlı değil — önek çözümü doğrudan operatöre "
        "bağlanabilir, `_PREFIX_RE`'nin gerekçesi yeniden değerlendirilmeli")


def test_onek_DEGER_INDEKSINDE_cozulur(schema):
    """"m10 ile başlayan" → gerçek değerler (özgün yazımlarıyla) bulunur ve `in` kurulur.
    Boyut, KELİMESİNDEN değil değerlerin nerede bulunduğundan gelir — "hangi boyutu
    kastetti" tahmini hiç yapılmaz."""
    r = cube_router.route("m10 ile başlayan müşteri bazında rework kg", schema)
    assert r
    f = next(f for f in r["cube_query"]["filters"] if f["dimension"] == "musteri")
    assert f["operator"] == "in"
    assert all(v.startswith("M10") for v in f["value"]), f["value"]
    assert len(f["value"]) > 1


def test_onek_hicbir_degere_uymazsa_DURUST_RED(schema):
    """Boş `in` üretmek "veri yok" gibi okunan güvenli-boş bir sonuç doğururdu."""
    assert cube_router.route("zzz ile başlayan müşteri bazında rework kg", schema) is None


def test_onek_BIRDEN_COK_boyuta_uyarsa_DURUST_RED(schema):
    """"ram" hem `makine` (RAM-1) hem `hat` (RAM 1) değerlerinde geçiyor — makine mi hat mı
    olduğu gerçekten belirsiz. Sessizce biri seçilseydi kullanıcı yanlış grain'de bir
    rapor alırdı."""
    assert cube_router.route("ram içeren makine bazında oee", schema) is None


def test_disi_edati_BILEREK_yok():
    """`_norm` "dışı" ile "dişi"yi AYNI dizeye indirger. "disi" bir dışlama edatı sayılsaydı
    cinsiyet/hayvan bağlamındaki her "dişi" kelimesi sessizce bir `neq` üretirdi."""
    assert "disi" not in cube_router._EXCLUDE_MARKERS
    assert cube_router._norm("dışı") == cube_router._norm("dişi")
