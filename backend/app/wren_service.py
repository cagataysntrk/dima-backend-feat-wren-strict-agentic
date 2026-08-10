"""Thin in-process wrapper around the Wren engine (``wren.engine.WrenEngine``).

The engine is stateless per query: we rebuild it from the compiled MDL manifest
(``target/mdl.json``) and the configured connection info on each call. This keeps
the demo simple and avoids holding DB connections open between requests.
"""

from __future__ import annotations

import hashlib

import base64
import json
import re
from pathlib import Path
from typing import Any

from wren.engine import WrenEngine

from app import istek_kimligi, rls
from app.logging_setup import get_logger

_log = get_logger("wren")

# Only read-only statements are allowed through the bridge.
_ALLOWED_PREFIX = re.compile(r"^\s*(with|select)\b", re.IGNORECASE)
_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|merge|call|copy)\b",
    re.IGNORECASE,
)


class UnsafeSqlError(ValueError):
    """Raised when a statement is not a read-only SELECT."""



#: FAZ 2.5 — hedef beyanının anahtarı. Tek ad, tek yer (`app/hedef.py::BEYAN_ANAHTARI`).
BEYAN = "target"


def _pack_koku(proje: Path) -> Path | None:
    """Proje dizininden `packs/` köküne çık — pack karar kaydı orada yaşar.

    ⚠ Derleme çıktısı geçici bir dizinde de olabilir (gölge diff, testler); o durumda
    depo içindeki `demo/` aranır. Bulunamazsa `None` → karar kaydı **yok** sayılır ve
    davranış bugünküdür. *Bulunamayan bir kararı uydurmak, kararın kendisinden kötüdür.*
    """
    for aday in (proje.parent.parent, proje.parent, Path(__file__).resolve().parents[1] / "demo"):
        try:
            if (aday / "packs" / "cekirdek").is_dir():
                return aday
        except Exception:                                    # noqa: BLE001
            continue
    return None


def _sayi_mi(v) -> bool:
    """Beyan sayıya çevrilebiliyor mu? Çevrilemiyorsa beyan **yok** sayılır — bozuk bir
    hedefi `0` kabul etmek, *"hedef yok"* ile *"hedef 0"* ayrımını yok ederdi."""
    try:
        float(v)
        return True
    except (TypeError, ValueError):
        return False

def guard_sql(sql: str) -> str:
    """Reject anything that is not a single read-only SELECT/CTE query."""
    stripped = sql.strip().rstrip(";")
    if ";" in stripped:
        raise UnsafeSqlError("Yalnızca tek bir sorgu çalıştırılabilir (';' bulundu).")
    if not _ALLOWED_PREFIX.match(stripped):
        raise UnsafeSqlError("Yalnızca SELECT/WITH sorgularına izin verilir.")
    if _FORBIDDEN.search(stripped):
        raise UnsafeSqlError("Veri değiştiren ifadeler (INSERT/UPDATE/DELETE/DROP...) yasak.")
    return stripped


#: CLAC gölge manifesti — **MDL baytına göre** bellekte. ⚠ Tek girdi: MDL bir istek
#: içinde değişmez ve sınırsız bir sözlük, uzun ömürlü bir süreçte sessiz bir sızıntıdır.
_CLAC_ONBELLEK: dict[str, tuple[bytes, int]] = {}


def _etiket_belirsizligini_ayikla(sinonimler: dict[str, list[str]],
                                  beyan: dict[str, set[str]],
                                  etiketten: dict[str, set[str]],
                                  dusenler: set[str] | None = None) -> dict[str, list[str]]:
    """🔴🔴 `§EB` — **ETİKETTEN TÜREYEN BELİRSİZ TOKEN SİNONİM OLAMAZ.**

    ## Ölçülen kusur (canlı `XII`, 2026-08-10)

    *«**renk grubuna** göre fire bu yıl»* → kırılım **üç** boyut:

        dimensions: ["ham_grup", "renk", "yas_grubu"]

    Kullanıcı **renk** sordu, cevaba **personel yaş grubu** da girdi. Rozet
    `source=cube` — deterministik yol — ve **hiçbir beyan yok**.

    ⊙ Sebep: `_with_label` etiketi kelimelere bölüp **her birini** sinonim yapıyor.
    *«Ham Grubu»* → `ham`, **`grubu`**; *«Yaş Grubu»* → `yas`, **`grubu`**. Yani çıplak
    `grubu` pack'te **yazmıyor**, sistem **kendisi üretiyor** — ve iki ayrı boyuta
    veriyor. `grubu` tek başına hiçbir şeyi adlandırmaz: bir *kategori kategorisidir*.

    🔴 Taranınca sınıf çıktı — **altı** çarpışma (`cari` ×2 · `tipi` · `renk` ·
    `hesap` · `grubu`), hepsi aynı mekanizmadan.

    ## Kural — kelime listesi YOK, yapısal

    Bir token **aynı küpte iki boyutun** sinonim kümesindeyse hiçbirini ayırt etmiyor
    demektir; **etiketten türemişse** düşer. ⚠ Pack'in **açıkça beyan ettiği** sinonim
    asla düşmez: beyan bir karardır, türetme bir tahmindir. *Bir kararı bir tahmin
    yüzünden geri almak, karar verenin yerine geçmektir.*

    *Hiçbir şeyi ayırt etmeyen bir ad, bir ad değildir.*
    """
    from collections import defaultdict

    sahip: dict[str, list[str]] = defaultdict(list)
    for dim, syns in sinonimler.items():
        for s in syns:
            sahip[s].append(dim)
    belirsiz = {t for t, ds in sahip.items() if len(ds) > 1}
    if not belirsiz:
        return sinonimler
    # 🔴🔴 `§EB/T` — **DÜŞEN TOKEN KELİME DAĞARCIĞINDA KALIR.**
    #
    # ⊙ Ölçüldü (kapı, `test_iliski_uzerinden_kirilim_TOPLAMI_DEGISTIRMEZ[yas_grubu]`):
    # `grubu` sinonim kümesinden düşünce **kapsam kapısı** da onu kaybetti ve
    # *«bu yıl yas_grubu bazında işlenen kg»* → *«"grubu" başka bir konu gibi görünüyor»*.
    #
    # ⊙ Kusur ayrımda: `partial_unknowns` *"bu kelime bizim dağarcığımızda mı"* diye
    # sorar; `_match_dimension` *"bu kelime hangi boyutu adlandırıyor"* diye. İkisini
    # aynı listeden okumak, **tanınabilir** ile **ayırt edici**yi bir sayar.
    #
    # *Bir kelimeyi tanımak ile onunla bir şeyi seçmek aynı yetenek değildir; birini
    # kaldırmak ötekini de kaldırıyorsa liste iki iş yapıyordur.*
    if dusenler is not None:
        dusenler |= belirsiz
    out: dict[str, list[str]] = {}
    for dim, syns in sinonimler.items():
        out[dim] = [s for s in syns
                    if s not in belirsiz
                    or s in beyan.get(dim, ())          # beyan korunur
                    or s not in etiketten.get(dim, ())  # etiketten gelmiyorsa dokunma
                    or s == dim]                        # boyutun kendi adı korunur
    return out


class WrenService:
    # Kategorik (düşük kardinalite) kolonlarda tutulacak azami farklı değer sayısı.
    # DETERMİNİSTİK değer-eşleştirme (typo düzeltme + çok-değerli filtre) yalnız bu eşiğin
    # altındaki boyutlarda çalışır. Gerçekçi ölçekte müşteri (~45) / renk (~50) / makine (~28)
    # gibi kategorik boyutlar 25'i aşıyordu → eşleştirme kapanıyordu. 64 bunları kapsar;
    # gerçek yüksek-kardinalite (binlerce cari) hâlâ dışarıda kalır. LLM prompt enum listesi
    # AYRI 25 kapağında (cube_router) → prompt token bütçesi bu değişiklikten etkilenmez.
    _MAX_ENUM = 64

    def __init__(self, project_dir: Path, datasource: str, connection_info: dict[str, Any],
                 company_slug: str | None = None):
        self.project_dir = Path(project_dir)
        self.datasource = datasource
        self.connection_info = connection_info
        # Overlay sinonimlerinin tenant kapsamı (ADR-0018 katman 3); None → yalnız global.
        self.company_slug = company_slug
        self._schema_cache: dict[str, Any] | None = None

    def invalidate_schema_cache(self) -> None:
        """Yeniden compose sonrası şema önbelleğini düşür (yeni cube seti görünsün)."""
        self._schema_cache = None

    # -- MDL -------------------------------------------------------------
    @property
    def mdl_path(self) -> Path:
        return self.project_dir / "target" / "mdl.json"

    def _mdl_bytes(self) -> bytes:
        """Derlenmiş MDL'in ham baytları — (mtime_ns, size) anahtarlı önbellekle.

        NEDEN ÖNBELLEK (2 Ağustos 2026): manifest her `_engine()` kurulumunda okunuyor ve
        `_engine()` `dry_plan()` ile `query()` tarafından AYRI AYRI kuruluyor; ayrıca
        `cube_sql()` ve `_inject_always_filter()` dosyayı kendi başlarına bir kez daha
        okuyor. Yani tek bir /ask, 117 KB'lık manifesti ≥2 kez okuyup base64'lüyordu.
        Faz 1'de manifest ilişki-türevi boyutlarla ~%23 büyüyecek; bu okuma trafiği
        büyümeden önce sabitlensin.

        Anahtar mtime_ns+size: `build()` artık `os.replace` ile ATOMİK yazdığı için yeni
        dosyanın inode/mtime'ı değişir → önbellek kendiliğinden düşer, elle invalidasyon
        gerekmez. Bayat manifest servis etme riski yok.
        """
        try:
            st = self.mdl_path.stat()
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                f"MDL derlenmemiş: {self.mdl_path}. Önce `wren context build` çalıştırın."
            ) from exc
        key = (st.st_mtime_ns, st.st_size)
        cached = getattr(self, "_mdl_cache", None)
        if cached is not None and cached[0] == key:
            return cached[1]
        raw = self.mdl_path.read_bytes()
        self._mdl_cache = (key, raw)
        return raw

    def _rls_kademesi(self) -> str:
        """`motor_rls` ∈ `off|shadow|on` — `_sql_policy` ile **aynı okuma deseni**.

        Config okunamazsa `off`: ölçülemeyen bir yapılandırmada **davranışı değiştirmek**,
        bu maddenin engellemek için var olduğu şeyin ta kendisi olurdu.
        """
        from app.config import get_settings

        try:
            mod = str(getattr(get_settings(), "motor_rls", "shadow") or "shadow").lower()
        except Exception:  # noqa: BLE001 — config yoksa bugünkü davranış aynen sürer
            return "off"
        return mod if mod in rls.KADEMELER else "shadow"

    def _cls_kademesi(self) -> str:
        """`motor_cls` ∈ `off|shadow|on` — varsayılan **`off`** (bkz. `config.py`)."""
        from app.config import get_settings

        try:
            mod = str(getattr(get_settings(), "motor_cls", "off") or "off").lower()
        except Exception:  # noqa: BLE001
            return "off"
        return mod if mod in rls.KADEMELER else "off"

    def _manifest_b64(self) -> str:
        """MDL → base64. **FAZ 1.1'in derleme sınırı burasıdır.**

        `_engine()`'in her kurulumu buradan geçer, yani RLAC'ı buraya yazmak onu **her
        yola** (cube · ham SQL · dry-plan · query) tek noktadan uygular. Sıcak yola bayrak
        koymak iki kod yolu ve her sorguda bir yapılandırma okuması demekti; `metrik_kaydi.
        semaya_yaz` ile **aynı desen** bilinçle tekrarlanıyor.

        🔴 **Önbellek anahtarı kademeyi İÇERİR.** İçermeseydi bayrak çevrildiği an
        **bayat** bir manifest servis edilirdi — ve bu, bir güvenlik katmanının
        *"açtım ama çalışmıyor"* hâli olurdu, üstelik sessiz.
        """
        kademe = (self._rls_kademesi(), self._cls_kademesi())
        cached = getattr(self, "_mdl_b64_cache", None)
        raw = self._mdl_bytes()
        if cached is not None and cached[0] is raw and cached[2] == kademe:
            return cached[1]
        islenmis, _n = rls.manifeste_yaz(raw, kademe=kademe[0])
        islenmis, _m = rls.cls_manifeste_yaz(islenmis, kademe=kademe[1])
        enc = base64.b64encode(islenmis).decode()
        self._mdl_b64_cache = (raw, enc, kademe)
        return enc

    def _sql_policy(self):
        """Motor SQL politikası (Faz A3) — `(config, mod)`.

        `off`    → politika yok (yalnız `denied_sql_functions` verildiyse o çalışır).
        `shadow` → motor GEVŞEK kurulur; politika AYRI bir katı motorla PARALEL denenir,
                   reddetmez, `_shadow_policy_check` loglar.
        `on`     → motor KATI kurulur; ihlal `WrenError` ile reddedilir.
        """
        from wren.config import WrenConfig

        from app.config import get_settings

        try:
            s = get_settings()
            mod = str(getattr(s, "strict_sql_policy", "shadow") or "shadow").lower()
            denied = {f.strip().lower()
                      for f in str(getattr(s, "denied_sql_functions", "") or "").split(",")
                      if f.strip()}
        except Exception:  # noqa: BLE001 — config okunamazsa politika devre dışı, akış sürer
            return WrenConfig(), "off"
        if mod not in ("off", "shadow", "on"):
            mod = "shadow"
        return WrenConfig(strict_mode=(mod == "on"),
                          denied_functions=frozenset(denied)), mod

    def _zaman_asimli_baglanti(self) -> dict[str, Any]:
        """Bağlantı bilgisine SORGU ve BAĞLANTI zaman aşımı ekler (Faz B).

        ## Ölçülen boşluk (2 Ağustos 2026)

        Motorun `DataSource.get_connection_info()`'su `statement_timeout`'u **yalnız dört
        datasource için** enjekte ediyor: `postgres` · `clickhouse` · `trino` · `bigquery`
        (varsayılan **180 sn**). **`mssql` dalı YOK** — ve üretimdeki tenant'larımız
        (gitas, atiksan) tam olarak mssql. Konnektör `kwargs["statement_timeout"]`'u
        **onurlandırıyor** (`connection.timeout = ...`) ama onu **kimse geçmiyordu**.

        Sonuç: mssql'de ağır ya da kilitlenmiş bir sorgu **süresiz** asılabilir ve isteği
        de kendisiyle birlikte askıya alır. postgres'te ise 180 sn — bir toplu iş için
        makul, **etkileşimli bir BI cevabı için değil**.

        ## `_db_reachable`'ın YERİNE GEÇMEZ — tamamlar

        Plan bu maddeyi *"`_db_reachable`'ın elle TCP ping'i yerine gerçek sorgu zaman
        aşımı"* diye yazmıştı. Ölçünce ikisinin **farklı şeyleri** yakaladığı görüldü:

        | | TCP ping | connect timeout | statement timeout |
        |---|---|---|---|
        | Tünel düşmüş (canlı olay 2026-07-25) | ✅ 3 sn'de | ✅ ama daha yavaş | ❌ hiç bağlanamaz |
        | DB ayakta, sorgu kilitli | ❌ **anında "erişilebilir" der** | ❌ | ✅ |

        Bu yüzden TCP ping **KALIR** (en hızlı ön eleme) ve zaman aşımları onun
        göremediği durumu kapatır. Birini ötekinin "yerine" saymak, kapanmamış bir
        boşluğu kapanmış göstermek olurdu.

        ## Neden burada, `company_registry`'de değil

        Her `WrenService` — kayıt defterinden gelen, ayarlardan gelen, testin kurduğu —
        aynı garantiyi almalı. Bağlantıyı ÜRETEN yere koymak, ikinci bir üretici
        eklendiği gün sessizce kaçırırdı (bu depoda ölçülmüş desen).
        """
        from app.config import get_settings

        info = dict(self.connection_info)
        sure = int(getattr(get_settings(), "db_statement_timeout", 0) or 0)
        if sure <= 0 or self.datasource in ("duckdb", "", None):
            # duckdb gömülüdür: ağ yok, kilitlenecek uzak bir sunucu yok. 0 = kapalı
            # (acil durumda ayarla geri alınabilir olmalı).
            return info
        # BOŞ/HEDEFSİZ bağlantıya DOKUNULMAZ. `dry_plan` DB'ye hiç bağlanmaz ve o yolda
        # `connection_info={}` geçmek meşrudur (transpile + model CTE'leri yeter). Böyle bir
        # sözlüğe `kwargs` eklemek onu "eksik bir GERÇEK bağlantı"ya çevirir ve motorun
        # pydantic doğrulaması patlar — ölçüldü: `test_gitas_calculated_ad_kolonlari`.
        # Zaten var olmayan bir bağlantıya zaman aşımı koymak anlamsızdır.
        if not any(info.get(k) for k in ("host", "url", "connectionUrl", "connection_url")):
            return info
        kwargs = dict(info.get("kwargs") or {})
        if self.datasource == "mssql":
            # Konnektör bunu `connection.timeout`'a yazar (pyodbc sorgu zaman aşımı).
            kwargs.setdefault("statement_timeout", sure)
            # ODBC anahtar sözcüğü: bilinmeyen kwargs bağlantı dizesine AYNEN eklenir
            # (`{key}={value}`), yani bu da konnektöre dokunmadan geçer.
            kwargs.setdefault("Connect Timeout", str(min(sure, 15)))
        elif self.datasource == "postgres":
            # Motor `if "statement_timeout" not in options` diye bakıyor → BİZİMKİ kazanır.
            opts = str(kwargs.get("options") or "")
            if "statement_timeout" not in opts:
                kwargs["options"] = (opts + " " if opts else "") + f"-c statement_timeout={sure}s"
            # Motorun varsayılanı 120 sn: bir tünel düştüğünde istek o kadar asılırdı.
            kwargs.setdefault("connect_timeout", min(sure, 15))
        else:
            # Diğerleri motorun kendi varsayılanını alır (clickhouse/trino/bigquery: 180 sn;
            # gerisi: yok). SESSİZ DEĞİL — bilinmeyen bir datasource'a zaman aşımı
            # UYDURMAK, konnektörün beklemediği bir anahtarla bağlantıyı kırabilirdi.
            _log.debug("statement_timeout enjekte edilmedi: datasource=%s (motorun "
                       "varsayılanı geçerli)", self.datasource)
            return info
        info["kwargs"] = kwargs
        return info

    def _engine(self, *, strict: bool = False) -> WrenEngine:
        """Motor örneği. `strict=True` yalnız GÖLGE denetimi için kullanılır (bkz.
        `_shadow_policy_check`) — normal akış yapılandırılmış politikayla kurulur."""
        cfg, _mod = self._sql_policy()
        if strict:
            from wren.config import WrenConfig

            cfg = WrenConfig(strict_mode=True, denied_functions=cfg.denied_functions)
        return WrenEngine(self._manifest_b64(), self.datasource,
                          self._zaman_asimli_baglanti(), config=cfg)

    def _connector(self):
        """Ham DB konnektörü — **semantik katmanı ATLAYARAK** fiziksel sorgu çalıştırmak için.

        Yalnız MDL'in bir katkısı olmayan işler için kullanılır: değer indeksi
        (`SELECT DISTINCT col FROM tablo`). Kullanıcı SQL'i buradan GEÇMEZ — o `dry_plan`/
        `query`'den, dolayısıyla `guard_sql` + SQL politikasından geçer.
        """
        from wren.engine import get_connector
        from wren.model.data_source import DataSource

        ds = DataSource(self.datasource)
        # Zaman aşımı BURADA DA geçerli — hatta en çok burada. Canlı olayda (2026-07-25)
        # `/schema`'yı asan sorgular tam olarak bu yoldan geçen değer indeksi
        # sorgularıydı; motor yolunu korurken ham konnektörü korumasız bırakmak, kapıyı
        # kilitleyip pencereyi açık unutmak olurdu.
        return get_connector(ds, ds.get_connection_info(self._zaman_asimli_baglanti()))

    @staticmethod
    def _physical_name(model: dict) -> str:
        """Modelin FİZİKSEL, nitelikli tablo adı (`"katalog"."şema"."tablo"`)."""
        tr = model.get("tableReference") or model.get("table_reference") or {}
        parts = [tr.get("catalog"), tr.get("schema"), tr.get("table") or model.get("name")]
        return ".".join(f'"{x}"' for x in parts if x)

    def _shadow_policy_check(self, sql: str) -> None:
        """GÖLGE MOD: "strict açık olsaydı bu sorgu reddedilir miydi?" — sorar, LOGLAR,
        akışı DEĞİŞTİRMEZ.

        Amaç, strict'i ölçmeden açmamak. Demo'da ölçüldü ki hiçbir meşru yol kırılmıyor,
        ama gerçek müşteri şemalarında (binlerce tablo, MDL'de yalnız bir kısmı) Discovery'nin
        ham SQL'i MDL-dışı bir tabloya dokunabilir. O redde geçmeden önce **kaç sorgunun**
        etkileneceği bilinmelidir. Log satırı `strict_sql_policy=on` kararının kanıtıdır.
        """
        try:
            with self._engine(strict=True) as eng:
                # 🔴 Gölge ölçüm de oturum özelliği taşımalı: taşımazsa `motor_cls=on`
                # iken **her meşru sorgu** için *"strict açık olsaydı REDDEDİLİRDİ"*
                # uyarısı basar. *Yanlış alarm üreten bir ölçüm, ölçüm değildir* — ve
                # bu gölgenin tüm amacı, strict'e geçmenin maliyetini SAYMAK.
                eng.dry_plan(sql, self._katalog_ozellikleri())
        except BaseException as exc:  # noqa: BLE001 — Rust PANIC `Exception` DEĞİLDİR
            _log.warning("SQL POLİTİKASI (gölge): strict açık olsaydı REDDEDİLİRDİ — %s | %s",
                         str(exc)[:180], " ".join(sql.split())[:220])

    def _cls_golge_denetimi(self, sql: str, properties) -> None:
        """GÖLGE MOD: *"`motor_cls=on` olsaydı bu sorgu **kolon kaybeder miydi**?"*
        — sorar, LOGLAR, akışı **DEĞİŞTİRMEZ**.

        ## 🔴 Bu ölçüm YOKTU — ve `shadow` bir HİÇLİKTİ

        Ölçüldü (§C ölçüt 4, 3. teşhis): `rls.cls_manifeste_yaz` `shadow` kademesinde
        manifesti **dokunmadan** döndürüyor, yani **`shadow ≡ off`**. Kademe vardı,
        ölçümü yoktu. Ölçütün hedefi ise *"`on`; **gölge modda 7 gün · sapma 0**"* —
        yani `off → shadow` yapmak, ölçmeden bir kutu işaretlemek olurdu.

        > 🔴 *Ölçmeyen bir gölge modu, ilerleme gibi görünen bir hiçliktir.*

        ## Neden kolon SAYISI kıyaslanıyor

        CLS `pii.py`'den **kategorik olarak farklıdır**: maskeleme kolonu **gösterir**
        (`123****89`), CLS onu **plandan düşürür** — ve düşme **sessizdir**. Yani gölgenin
        ölçmesi gereken şey *"plan patlar mı"* değil, **"kaç kolon kaybolur"**dur.

        ## ⚠ Maliyet — ve belgemi DÜZELTTİM

        İlk yazımda *"ucuz ön eleme (kardeş desen)"* yazdım ve **uygulamadım**: RLS
        gölgesi `alwaysFilter` baytını tarayabiliyor çünkü manifest o işareti taşıyor;
        CLS'in sınıflandırması ise **ad tabanlıdır** (`sensitivity.classify`) ve
        manifestte byte düzeyinde taranabilecek bir işaret **yok**.

        🔴 *Belgede olup kodda olmayan bir iyileştirme, kodda olmayan bir iyileştirmeden
        kötüdür — çünkü var sanılır.*

        Gerçek çözüm **bellekleme**: CLAC manifesti MDL baytlarına göre bir kez üretilir
        (`_CLAC_ONBELLEK`). Gölge her sorguda koşar ama `json.loads` **manifest başına bir
        kez** olur; kalan maliyet iki `dry_plan`dır ve o, gölgenin **kendisidir**.

        ⚠ **Kayıt yeri kardeşiyle aynı** (`_log.warning`), ikinci bir JSONL **açılmadı**:
        gölge bulgularının bu depoda zaten bir sahibi var ve ikincisi *"aynı kuralın iki
        sahibi"* olurdu. 7 günlük ölçüt aynı greple ölçülür: **`CLS (gölge)`** etiketi.
        """
        try:
            ham = self._mdl_bytes()
            # ⚠ Hassas kolon yoksa CLS `on`'da da bir şey düşürmez → ölçülecek fark yok.
            anahtar = hashlib.sha256(ham).hexdigest()
            if anahtar not in _CLAC_ONBELLEK:
                _CLAC_ONBELLEK.clear()          # tek girdi yeter: MDL istek içinde değişmez
                _CLAC_ONBELLEK[anahtar] = rls.clac_manifesti(ham)
            golge, kural_sayisi = _CLAC_ONBELLEK[anahtar]
            if not kural_sayisi:
                return
            cfg, _mod = self._sql_policy()
            with WrenEngine(base64.b64encode(golge).decode(), self.datasource,
                            self._zaman_asimli_baglanti(), config=cfg) as eng:
                # ⚠ **AYNI özellikler**: farklı özelliklerle planlanan iki SQL'i
                # kıyaslamak, CLS farkı yerine ÖZELLİK farkını ölçerdi.
                cls_li = eng.dry_plan(sql, properties)
            with self._engine() as eng:
                bugunku = eng.dry_plan(sql, properties)
        except BaseException as exc:  # noqa: BLE001 — Rust PANIC `Exception` DEĞİLDİR
            # 🔴 **Planlama HATASI da bir bulgudur**: `on`'da bu sorgu **çalışmazdı**.
            # Sessizce geçmek, `on`'a geçişin maliyetini sıfır göstermek olurdu.
            _log.warning("CLS (gölge): `motor_cls=on` olsaydı bu sorgu PLANLANAMAZDI — "
                         "%s | %s", str(exc)[:180], " ".join(sql.split())[:200])
            return

        if cls_li != bugunku:
            # ⚠ Fark **beklenen** de olabilir (hassas kolon gerçekten düşer) ama ölçütün
            # istediği *"sapma 0"*dır: her fark bir **karar** gerektirir ve kararın
            # verilebilmesi için önce **görünmesi** gerekir.
            _log.warning("CLS (gölge): plan FARKLI — `motor_cls=on` %d kuralla kolon "
                         "düşürürdü | %s", kural_sayisi, " ".join(sql.split())[:200])

    def _rls_golge_denetimi(self, sql: str) -> None:
        """GÖLGE MOD: *"`motor_rls=on` olsaydı bu sorgu farklı mı planlanırdı?"* — sorar,
        LOGLAR, akışı **DEĞİŞTİRMEZ**.

        Amaç `on`'a ölçmeden geçmemek. Fark **beklenen** bir yerde olabilir (ham SQL yolu:
        kapatılmak istenen baypas tam orası) ya da **beklenmedik** bir yerde (cube yolu:
        orada `_inject_always_filter` zaten filtreliyor, fark çıkarsa iki mekanizma
        **ayrışmış** demektir). Log satırı `motor_rls=on` kararının kanıtıdır.

        🔴 **KARDEŞ DESENLE AYNI, ve JSONL'dan SAPMA BİLİNÇLİ.** Yol haritası
        `logs/rls_shadow.jsonl` diyordu; bu depoda gölge bulgularının **zaten bir sahibi
        var** (`_shadow_policy_check` → `_log.warning`) ve ikinci bir kayıt mekanizması
        açmak *"aynı kuralın iki sahibi"* olurdu. Kapının 7 günlük ölçütü (*"0 satır"*)
        aynı greple ölçülebilir: `RLS (gölge)` etiketi.
        """
        try:
            ham = self._mdl_bytes()
            # ⚠️ UCUZ ÖN ELEME — FAZ 0.17'nin gecikme bütçesi gereği. Gölge denetimi HER
            # sorguda koşar; `json.loads` 117 KB'lık bir manifesti her turda ayrıştırırdı
            # ve **beş tenant'ın dördünde** hiç `alwaysFilter` YOK (ölçüldü: yalnız
            # gulteks taşıyor, 3 cube). Bayt taraması o dördünü ayrıştırmadan eler.
            if b"alwaysFilter" not in ham and b"always_filter" not in ham:
                return
            golge, kural_sayisi = rls.rlac_manifesti(ham)
            if not kural_sayisi:
                return                      # çevrilecek kural yok → ölçülecek fark da yok
            cfg, _mod = self._sql_policy()
            with WrenEngine(base64.b64encode(golge).decode(), self.datasource,
                            self._zaman_asimli_baglanti(), config=cfg) as eng:
                rls_li = eng.dry_plan(sql, self._katalog_ozellikleri())
            with self._engine() as eng:
                # ⚠ İKİ tarafa da AYNI özellikler: farklı özelliklerle planlanan iki
                # SQL'i kıyaslamak, RLS farkı yerine ÖZELLİK farkını ölçerdi.
                bugunku = eng.dry_plan(sql, self._katalog_ozellikleri())
        except BaseException as exc:  # noqa: BLE001 — Rust PANIC `Exception` DEĞİLDİR
            _log.warning("RLS (gölge): kıyas KOŞULAMADI — %s | %s",
                         str(exc)[:180], " ".join(sql.split())[:180])
            return
        if rls_li != bugunku:
            _log.warning(
                "RLS (gölge): motor_rls=on olsaydı plan DEĞİŞİRDİ (%d kural) | %s",
                kural_sayisi, " ".join(sql.split())[:220])

    def _db_reachable(self, timeout: float = 3.0) -> bool:
        """Uzak DB'ye hızlı TCP erişilebilirlik kontrolü. Amaç: enrichment (best-effort
        değer zenginleştirme) ULAŞILAMAZ müşteri DB'sinde /schema'yı ASMASIN — canlı
        (2026-07-25): gitas DB tüneli düşünce /schema uzun bağlantı-timeout'unda asılıp
        proxy 500'ü veriyordu. duckdb/yerel → her zaman True (gerçek sorgu yolu etkilenmez)."""
        if self.datasource in ("duckdb", "", None):
            return True
        host = str(self.connection_info.get("host") or "").strip()
        if not host:
            return True  # host yok → engine kendi hatasını versin (enrichment try/except sarar)
        try:
            port = int(self.connection_info.get("port") or 1433)
        except (TypeError, ValueError):
            port = 1433
        import socket

        s = socket.socket()
        s.settimeout(timeout)
        try:
            s.connect((host, port))
            return True
        except Exception:
            return False
        finally:
            s.close()

    def _active_langs(self) -> tuple[str, ...]:
        """Tenant AKTİF DİL SETİ (§7b) — company.yml `diller:` (materialize eder). Yoksa
        varsayılan (DEFAULT_LANGS = tr+en). Sıra = öncelik. Best-effort okuma: hata/dosya
        yoksa varsayılana düşer (deterministik çekirdek config'e bağımlı olmasın)."""
        from app.archetypes import DEFAULT_LANGS
        try:
            import yaml

            cfg = self.project_dir.parent / "companies" / (self.company_slug or "") / "company.yml"
            diller = (yaml.safe_load(cfg.read_text()) or {}).get("diller")
            if diller:
                return tuple(str(x) for x in diller)
        except Exception:
            pass
        return DEFAULT_LANGS

    # -- Public API ------------------------------------------------------
    def schema(self) -> dict[str, Any]:
        if self._schema_cache is not None:
            # db_online CANLI durumdur, cache'lenmez: cache DB KAPALIYKEN kurulduysa (değerler
            # eksik, db_online=False) DB geri gelince YENİDEN KUR (enrichment tazelensin);
            # değilse yalnız güncel erişilebilirliği yaz ve cache'i döndür. (Badge canlı kalır.)
            live_ok = self._db_reachable()
            if live_ok and not self._schema_cache.get("db_online", True):
                self._schema_cache = None
            else:
                self._schema_cache["db_online"] = live_ok
                return self._schema_cache
        mdl = json.loads(self._mdl_bytes())
        models = [
            {
                "name": m.get("name"),
                "columns": [
                    # `sensitivity` MANİFESTTEN TAŞINIR (Faz A1). Bu sözlük eskiden yalnız
                    # name+type kuruyordu; YAML'daki `sensitivity: person` beyanı burada
                    # DÜŞÜYOR ve aşağıdaki sınıflandırma ad-tabanlı emniyet ağına geri
                    # düşüyordu — yani beyan hiç işe yaramıyordu (ölçüldü: `operator`
                    # beyan edilmesine rağmen prompt'a gitmeye devam etti).
                    # `is_calculated` / `relationship` de TAŞINIR (Faz A2): bunlar FİZİKSEL
                    # olmayan kolonlardır (calc ifadesi ya da ilişki handle'ı) ve ham satır
                    # sorgusuna giremezler — `SELECT personel FROM partiler` binder hatası
                    # verir. Bayraklar düşürüldüğü için tüketiciler bunu ayırt edemiyordu.
                    {"name": c.get("name"), "type": c.get("type", ""),
                     **({"sensitivity": c["sensitivity"]} if c.get("sensitivity") else {}),
                     **({"is_calculated": True}
                        if (c.get("isCalculated") or c.get("is_calculated")) else {}),
                     **({"relationship": c["relationship"]} if c.get("relationship") else {})}
                    for c in m.get("columns", [])
                ],
            }
            for m in mdl.get("models", [])
        ]
        # DB erişilebilirliğini BİR KEZ ölç: ulaşılamazsa enrichment'ı ATLA (fail-open,
        # hızlı) — /schema yapısal olarak yine döner, değerler sonra tazelenir. Ulaşılamaz
        # müşteri DB'sinde uzun bağlantı-timeout'unda asılmayı önler (canlı 2026-07-25).
        db_ok = self._db_reachable()
        if db_ok:
            # Fiziksel ad haritası: değer indeksi semantik katmanı ATLAR (Faz B1), bu
            # yüzden modelin gerçek `tableReference`'ına ihtiyacı var.
            self._enrich_categorical(
                models,
                {m.get("name"): self._physical_name(m) for m in mdl.get("models", [])},
            )
        relationships = [
            {
                "name": r.get("name"),
                "models": list(r.get("models", [])),
                "join_type": r.get("joinType", ""),
                "condition": r.get("condition", ""),
            }
            for r in mdl.get("relationships", [])
        ]
        # Cube kataloğu + NL yönlendirme içeriği (synonyms) — içerik cube metadata'sında
        # yaşar (ADR-0005: içerik Wren'de, kod generic); generic router bunları okur.
        from app.llm import _norm

        def _syns(lst) -> list[str]:
            return [_norm(str(s)) for s in (lst or [])]

        # ETİKET ⊆ SİNONİM (ADR-0018 evrensel kuralı, prototip): kullanıcıya GÖSTERDİĞİMİZ
        # etiket ("cari adı") ve anlamlı token'ları ("adı") otomatik sinonim setine katılır.
        # Böylece "cari adı bazında" duvara çarpmaz — sıfır pack işi, tüm kaynaklarda geçerli.
        # Token eşiği: ≥3 harf + dolgu/durak değil (yanlış-pozitif dar tutulur).
        _LABEL_STOP = {"gore", "bazinda", "adet", "sayi", "sayisi", "toplam", "orani",
                       "kodu", "kod", "tutari", "tutar", "miktari", "miktar"}

        def _label_tokens(label: str | None) -> list[str]:
            """Etiketten **türetilen** token'lar — `_with_label`'ın eklediklerinin aynısı.

            ⚠ Ayrı bir fonksiyon çünkü sonradan *"bu token beyan mı, türetme mi"*
            sorusuna cevap gerekiyor (`§EB`). Kural `_with_label` ile **birebir** aynı
            tutulur; ikisi ayrışırsa ayıklama yanlış token'ı düşürür.
            """
            if not label:
                return []
            nl = _norm(str(label).rstrip("!"))
            return [c for c in [nl, *nl.split()]
                    if c and (c == nl or (len(c) >= 3 and c not in _LABEL_STOP))]

        def _with_label(label: str | None, syns: list[str]) -> list[str]:
            out = list(syns)
            if not label:
                return out
            nl = _norm(str(label).rstrip("!"))
            for cand in [nl, *nl.split()]:
                if cand and cand not in out and (
                        cand == nl or (len(cand) >= 3 and cand not in _LABEL_STOP)):
                    out.append(cand)
            return out

        def _merge_syns(*lists) -> list[str]:
            out: list[str] = []
            for lst in lists:
                for s in lst:
                    if s not in out:
                        out.append(s)
            return out

        _langs = self._active_langs()  # tenant aktif dil seti (company.yml diller:) §7b
        #: `§EB/T` — küp başına **düşen** belirsiz token'lar. Ayırt etmezler ama
        #: dağarcıkta kalırlar (`partial_unknowns` onları tanır).
        _dusen: dict[str, set[str]] = {}

        def _archetype_syns(measure_name: str) -> list[str]:
            # Ölçü arketip sözlüğü (ADR-0018 kaldıraç b): ölçü adı = arketip anahtarı.
            from app.archetypes import synonyms_for

            return [_norm(s) for s in synonyms_for(measure_name, _langs)]

        def _dim_i18n(dim_name: str) -> list[str]:
            # Boyut çok-dil katmanı (§7b): yerel dil YAML'da, ek diller (en teknik) burada.
            from app.archetypes import dim_synonyms_for

            return [_norm(s) for s in dim_synonyms_for(dim_name, _langs)]

        cubes = [
            {
                "name": c.get("name"),
                # Faz 4.10 (1 Ağustos 2026): cube'un fiziksel taban tablosu/view'ı — dallı
                # kök-neden analizinin YAPRAK seviyesi (app/drill.py::build_raw_row_sql)
                # ham satırları BURADAN çeker. Önceden schema()'da HİÇ yoktu (yalnız
                # app/mdl_writer.py YAML dosyasını doğrudan okuyarak biliyordu) — canlı
                # bulgu: /ask/drill'in "raw" action'ı bu alan olmadan cube ADINI (fiziksel
                # olarak var OLMAYAN bir tablo) sorgulamaya çalışıp WrenError üretiyordu.
                "base_object": c.get("baseObject") or c.get("base_object"),
                "measures": [m.get("name") for m in c.get("measures", [])],
                "dimensions": [d.get("name") for d in c.get("dimensions", [])],
                "time_dimensions": [t.get("name") for t in c.get("timeDimensions", [])],
                # 🔴🔴 `§DK-4` — **ZAMAN EKSENİ DE BİR İFADE OLABİLİR, ve üç küpte ÖYLE.**
                #
                # Ölçüldü (2026-08-10): `enerji_makine` · `enerji_sapma` · `cusum`
                # zaman eksenini bir **türev ifadeyle** tanımlıyor:
                #
                #     timeDimensions: [{name: "donem_tarih",
                #                       expression: "make_date(yil, ay, 1)"}]
                #
                # `veri_araligi.aralik()` ise `SELECT MIN("donem_tarih") FROM …` diye
                # **adı** kullanıyordu → `Binder Error: Referenced column "donem_tarih"
                # not found` → aralık **ölçülemiyor** → `varsayilan_donem` fail-close
                # ediyor ve o küplerde **her dönem sorusu** netleştirmeye düşüyor.
                #
                # ⊙ Bu, bugünün **dördüncü** aynı-sınıf bulgusu: `§DK` (enum) · `§DK-3`
                # (route değerleri) · ve bu. Üçünde de bir tüketici, **ifadenin**
                # gerektiği yerde **adı** okuyordu.
                #
                # ⚠ `A11` envanteri *«zaman ekseni olmayan küp: 0»* diyordu ve **doğruydu**
                # — ama yanıltıcıydı: küpler bir eksen **beyan ediyor**, o eksen
                # **çözülmüyor**. Yüklem beyanı ölçüyordu, çözülebilirliği değil.
                #
                # *Bir adın ardında bir ifade varsa, o adı kullanan her tüketici o
                # ifadeyi de bilmek zorundadır — yoksa aynı katalog iki farklı şey anlatır.*
                "time_dimension_expressions": {
                    t.get("name"): t.get("expression")
                    for t in c.get("timeDimensions", [])
                    if t.get("expression") and t.get("expression") != t.get("name")
                },
                "synonyms": _syns(c.get("synonyms")),
                "default_measure": c.get("defaultMeasure"),
                # İNSANCA görünüm (chip/not etiketleri): label > ilk ham sinonim
                "display": str(c.get("label") or (c.get("synonyms") or [c.get("name")])[0]).rstrip("!"),
                # 🔴 `nl: false` → ölçü NL YÜZEYİNDEN ÇIKAR (2026-08-06).
                #
                # Ölçülen kusur: `maliyet.toplam_uretim_kg` bir üretim ölçüsü DEĞİL,
                # kg-başına maliyetin **PAYDASIDIR** (`urun_maliyetleri` aylık
                # maliyetlendirme tablosu). Ama `toplam üretim` sinonimini taşıdığı için
                # `route()` on eval vakasını oraya yönlendiriyordu — ve o cube'un yalnız
                # `makine` boyutu olduğu için soruların çoğunu **cevaplayamıyordu** bile.
                #
                # ⚠ Ölçü SİLİNMİYOR: SQL'de gerekli (oran hesabının paydası) ve `/cube`
                # ile açıkça istenebilir. Yalnız **doğal dil eşleştirmesine** girmiyor.
                # *Bir paydayı, ölçünün kendisi sanmak — payda büyüdükçe cevap kayar.*
                "measure_synonyms": {
                    m["name"]: _merge_syns(
                        _with_label(m.get("label"), _syns(m.get("synonyms"))),
                        _archetype_syns(m["name"]))
                    for m in c.get("measures", []) if m.get("nl") is not False
                },
                "measure_synonyms_display": {
                    m["name"]: str(m.get("label") or (m.get("synonyms") or [m["name"]])[0]).rstrip("!")
                    for m in c.get("measures", [])
                },
                # Yön semantiği (metadata kaynaklı): yüksek=KÖTÜ ölçüler — frontend
                # ısı-haritası rengini buradan okur (UI regex'ine gömülmez).
                # Not: wren build snake_case'i camelCase'e çevirir (lowerIsBetter).
                "lower_is_better": [
                    m["name"] for m in c.get("measures", [])
                    if m.get("lowerIsBetter") or m.get("lower_is_better")
                ],
                # Birim semantiği (metadata kaynaklı, lower_is_better deseni): ölçünün
                # birimi cube YAML'ında BİR KEZ tanımlanır; frontend buradan okur —
                # kolon-adı regex'i yalnız yedektir (şirket başına yeniden tanım YOK).
                "units": {
                    m["name"]: str(m["unit"]) for m in c.get("measures", [])
                    if m.get("unit")
                },
                # ÇEKİRDEK METRİK BAĞI (FAZ 2.1/2.2b) — `units`/`lower_is_better` ile AYNI
                # desen: ölçü YAML'ında bir kez bildirilir, buradan okunur. Ad göçünden
                # sonra (`satis_tutari` → `_kalem`/`_hareket`) çapraz-cube geçişinin
                # "bu ikisi AYNI kavramın farklı grain'i mi" sorusunu cevaplayan tek yer.
                # ⚠ İkinci bir sözlük DEĞİL: kaynak hâlâ cube YAML'ı.
                "cekirdek_metrik": {
                    m["name"]: str(m["cekirdekMetrik"] or m.get("cekirdek_metrik"))
                    for m in c.get("measures", [])
                    if m.get("cekirdekMetrik") or m.get("cekirdek_metrik")
                },
                # 🔴 KIYASLANAMAZ ölçüler: grain'i ERP'ye göre DEĞİŞEN türev metrikler
                # (`satis_tutari_turev`). Çapraz-cube geçişi bunlara ASLA geçmez —
                # iki şirketin bu sayısını yan yana koymak iki farklı şeyi karşılaştırmaktır.
                # FAZ 2.5 — HEDEF BEYANI (`units` deseni). 🔴 Beyan YOKSA anahtar da yok:
                # "hedef yok" ile "hedef 0" asla karıştırılmaz — sıfır hedef ULAŞILMIŞ bir
                # hedeftir, hedefsizlik ise ÖLÇÜLEMEZLİKTİR.
                "hedefler": {
                    m["name"]: float(m[BEYAN]) for m in c.get("measures", [])
                    if m.get(BEYAN) is not None and _sayi_mi(m.get(BEYAN))
                },
                "kiyaslanamaz": [
                    m["name"] for m in c.get("measures", [])
                    if m.get("kiyaslanamaz")
                ],
                # Additivite (cube-katalog 2026-07 §3, lower_is_better deseni): zaman
                # kovasında toplanamayan ölçüler. semi = zaman DIŞINDA toplanır ama
                # zamanda dönem-SONU değeridir (bakiye/stok — düz SUM sessiz-yanlış);
                # non = hiçbir boyutta toplanamaz (avg/count_distinct). cube_sql zaman
                # kovalı semi ölçüde uyarır/dönem-sonuna çevirir.
                "semi_additive": [
                    m["name"] for m in c.get("measures", [])
                    if str(m.get("additive") or "").lower() == "semi"
                ],
                "non_additive": [
                    m["name"] for m in c.get("measures", [])
                    if str(m.get("additive") or "").lower() == "non"
                ],
                # Ölçü İFADELERİ (Faz 5.2). Yalnız katkı ayrıştırmasının TOPLANABİLİRLİK
                # kapısı için yayımlanır (`app/contribution.py`): `AVG(...)`/oran/
                # `COUNT(DISTINCT ...)` bir ölçüde segment katkısı MATEMATİKSEL OLARAK
                # tanımsızdır ve o kapı ada bakarak değil KANITA bakarak karar vermeli.
                # `additive:` beyanı öncelikli kalır — bu, beyan YOKSA devreye giren yedek.
                # LLM'e gitmez (değişmez #1: LLM ham değer görmez; bu şema metadata'sıdır
                # ama `build_catalog` yalnız ad listesi üretir, ifadeleri taşımaz).
                "measure_expressions": {
                    m["name"]: m.get("expression")
                    for m in c.get("measures", []) if m.get("expression")
                },
                # PVM (fiyat-miktar-karma) eşleştirmeleri (Faz 5.1) — cube'un AÇIK beyanı.
                # Tahmin edilmez: `toplam_ciro / toplam_agirlik_kg` gerçek bir TL/kg
                # fiyatıdır, `toplam_tutar / fatura_sayisi` ise ortalama fatura büyüklüğü.
                # Ayrım bir İÇERİK bilgisidir; ad kalıbından çıkarmak yanlış eşleştirmede
                # GÜVENLE YANLIŞ ekonomi üretirdi ("birim fiyat %12 arttı" sorgulanmaz).
                "pvm": c.get("pvm") or [],
                # Cube-düzeyi sabit filtre (LookML sql_always_where): her sorguya
                # otomatik eklenir. CANCELLED=0'ı ölçü ifadelerinden çıkarır — tekrar
                # ve iptal-kaydı sızıntısını yapısal önler. build camelCase'e çevirir.
                "always_filter": c.get("always_filter") or c.get("alwaysFilter"),
                "dimension_labels": {
                    d["name"]: str(d.get("label") or (d.get("synonyms") or [d["name"]])[0]).rstrip("!")
                    for d in c.get("dimensions", [])
                },
                # 🔴🔴 `§EB` — **ETİKETTEN TÜREYEN BELİRSİZ TOKEN SİNONİM OLAMAZ.**
                # Gerekçe ve ölçüm `_etiket_belirsizligini_ayikla`'da.
                "dimension_synonyms": _etiket_belirsizligini_ayikla(
                    # ⟳🔴 **`§EB/A` DENENDİ, ÖLÇÜLDÜ, GERİ ALINDI.**
                    #
                    # Hipotez: *«bir boyut her zaman kendi adıyla anılabilmeli»* —
                    # çünkü `«… yas_grubu bazında …»` yalnız **kazara** çalışıyordu
                    # (eşleşen token `grubu` idi) ve `_norm` alt çizgiyi koruduğu için
                    # `yas grubu` (boşluklu) `yas_grubu`'yu karşılamıyor.
                    #
                    # ⊙ Ama ad **her boyut için** eklenince katalog **açgözlü** oldu:
                    # gerçek-dünya korpusu `sessiz_yanlis` **12 → 18**. `§99.1`'in
                    # birebir tekrarı — *geniş sinonim küpü açgözlü yapar*, ve teknik
                    # adlar kullanıcının **konuşmadığı** kelimelerdir: kazandırdıkları
                    # nadir, çarptırdıkları sık.
                    #
                    # ⚠ Ders: bir kapının **kazara** geçmesi, geçtiği yolu meşru yapmaz —
                    # ama o yolu kapatırken **yerine ne konduğu** ölçülmelidir.
                    # *Bir kesinlik kazanmak için bir belirsizlik satın alıyorsan,
                    # takasın yönünü sayıyla bilmen gerekir.*
                    {d["name"]: _merge_syns(
                        _with_label(d.get("label"), _syns(d.get("synonyms"))),
                        _dim_i18n(d["name"]))  # §7b: yerel (YAML) ⊕ yardımcı-teknik dil
                     for d in c.get("dimensions", [])},
                    {d["name"]: set(_syns(d.get("synonyms")))
                     for d in c.get("dimensions", [])},
                    {d["name"]: set(_label_tokens(d.get("label")))
                     for d in c.get("dimensions", [])},
                    _dusen.setdefault(c.get("name"), set())),
                # ⚠ `dimension_synonyms`'ten **SONRA** gelmeli: sözlük değişmezi kaynak
                # sırasıyla değerlendirilir ve bu anlık görüntü, kümeyi dolduran çağrı
                # koştuktan sonra alınmalı. İlk yazımda üstteydi ve **boş** kalıyordu —
                # kapı bunu yakaladı. *Bir anlık görüntünün doğruluğu, ne zaman
                # alındığına bağlıdır.*
                "belirsiz_boyut_tokenlari": sorted(
                    _dusen.setdefault(c.get("name"), set())),
                # PROVENANCE (Faz 1.3): boyut cube'un KENDİ base_object'inden mi geliyor,
                # yoksa bir İLİŞKİ üzerinden mi? `_compose_relationship_dimensions`
                # üretilen boyuta `properties.origin` yazar; burası onu router/UI'a açar.
                # Yalnız ilişki-türevi boyutlar yer alır — yerel boyutlar sözlükte YOKTUR.
                #
                # Bugüne kadar `schema()` boyutun `expression`'ını bile atıyordu, yani
                # `parti.cinsiyet` ile `parti.makine` router açısından AYIRT EDİLEMEZDİ.
                # Açtığı dört tüketici:
                #   (i)   Query Contract: "bu kolon hangi join'den geldi" (ADR-0010).
                #   (ii)  `_match_cube` tie-break: boyutu YERELİNDE taşıyan cube, 2 sıçrama
                #         ötesinden ulaşana YEĞ TUTULMALI (Faz 3.2) — bugün böyle bir
                #         sinyal YOK ve enrichment yayıldıkça belirsizlik artacak.
                #   (iii) fan-out risk anotasyonu (hangi ilişki, kaç sıçrama).
                #   (iv)  drill'in `base_object` ötesine inebilmesi.
                # `base_object` alanı da tam bu gerekçeyle sonradan eklenmişti (bkz. :215).
                "dimension_origin": {
                    d["name"]: origin
                    for d in c.get("dimensions", [])
                    if (origin := (d.get("properties") or {}).get("origin"))
                },
            }
            for c in mdl.get("cubes", [])
        ]
        self._apply_synonym_overlays(cubes)  # ADR-0018 katman 3 (canlı, deploy'suz)
        self._apply_measure_overrides(cubes)  # Faz 2d: deprecate edilen ölçüleri NL'den gizle
        self._damgala_fanout(cubes)           # Faz D2: ilişki sertifikası → boyut kökeni
        if db_ok:
            self._enrich_cube_dim_values(cubes, mdl, models)
        # CROSS-CUBE KPI kataloğu (kpis/*.yml): yönlendirme için ad/etiket/sinonim; tam
        # bileşen SQL'i tanımda kalır, resolver çalıştırır. Yalnız hafif metadata schema'da.
        from app.kpi import load_kpis

        kpis = [
            {"name": k["name"], "label": k.get("label", k["name"]),
             "unit": k.get("unit"), "lower_is_better": bool(k.get("lower_is_better")),
             "synonyms": _syns(k.get("synonyms"))}
            for k in load_kpis(self.project_dir).values()
        ]
        self._schema_cache = {
            "catalog": mdl.get("catalog"),
            "schema_name": mdl.get("schema"),
            "models": models,
            "relationships": relationships,
            "cubes": cubes,
            "kpis": kpis,
            "business_rules": self._load_knowledge("rules"),
            # 🔴 FAZ 5.13b — **YAPISAL** kurallar (`knowledge/kurallar.yml`). `business_rules`
            # düz metindir ve LLM prompt'una gider; bu ise `app/rules.py`'nin okuduğu
            # `{id, metin, kapsam}` listesidir ve çıktısı **anlatıya** girer, SQL'e değil.
            # ⚠ İkisi ayrı tüketiciler: biri modeli yönlendirir, öteki kullanıcıya
            # **kaynağı gösterilebilir** bir not verir.
            "kurallar": self._yapisal_kurallar(),
            "golden_sql": self._load_knowledge("sql"),
            "db_online": db_ok,  # UI çevrimiçi/çevrimdışı rozeti (TCP erişilebilirlik)
        }
        # ⚠️ FAZ 0.18 — METRİK KAYDI şemaya BURADA yazılır (bayrak açıksa).
        # Neden burada: `cube_router` hiçbir bayrak okumaz ve okumamalı — deterministik
        # olması bilinçli bir karardır. Bayrak, ayarların erişilebilir olduğu **derleme
        # sınırında** durur; sıcak yolda değil. Kapalıysa anahtar HİÇ yazılmaz →
        # `_match_cube` kaydı görmez → davranış **birebir bugünkü** (GERİ AL).
        try:
            from app.config import get_settings
            from app.features import resolve_for
            from app.metrik_kaydi import semaya_yaz

            # FAZ 3.1 — `base`: pack karar kaydının kökü. `demo/` dizini, projenin
            # iki üstü (`<demo>/wren-projects/<slug>` ya da geçici derleme dizini).
            _base = get_settings().demo_dir if hasattr(get_settings(), "demo_dir") else None
            semaya_yaz(self._schema_cache,
                       acik="metrik_kaydi" in resolve_for(get_settings(), None),
                       base=_base or _pack_koku(self.project_dir))
        except Exception:                                      # noqa: BLE001
            # Kayıt bir **iyileştirmedir**, bir ön koşul değil: üretilemezse şema
            # eksiksiz döner ve sistem bugünkü yolunu izler. Sessiz yutma YOK:
            _log.warning("metrik kaydı şemaya yazılamadı (best-effort)", exc_info=True)
        return self._schema_cache

    def _damgala_fanout(self, cubes: list) -> None:
        """İlişki sertifikasını (Faz D2) boyut kökenine damgalar: `origin["certified"]`.

        Sertifika bir **build artefaktıdır** (`target/fanout_certificate.json`,
        `python -m app.fanout`). `schema()` onu yalnız OKUR — ölçmez. Bilerek: ölçüm 62
        `COUNT` sorgusudur ve `schema()` Faz B1'de 2277 ms'den aşağı çekildi; her istemci
        çağrısına build-time bir maliyeti geri koymak o kazancı geri verirdi.

        Artefakt yoksa damga `"olculmedi"` olur — **sessiz "sağlıklı" DEĞİL**. Sertifikanın
        tüm değeri *"ölçülmedi"* ile *"ölçüldü, temiz"* ayrımındadır; ölçülmemişi temiz
        göstermek, olmayan bir garantiyi rozetlemek olurdu.
        """
        from app import fanout

        sert = fanout.oku(self.project_dir)
        for c in cubes:
            for origin in (c.get("dimension_origin") or {}).values():
                if isinstance(origin, dict):
                    origin["certified"] = fanout.rozet(sert, origin.get("relationship"))

    def _apply_synonym_overlays(self, cubes: list) -> None:
        """Control-plane DB'deki ONAYLI sinonim overlay'lerini schema'ya BİRLEŞTİRİR
        (ADR-0018 katman 3, additive): pack YAML + arketip üstüne biner, base'i silmez.
        Kapsam: global (tüm tenantlar) + tenant (self.company_slug). Yalnız approved=True
        satırlar uygulanır (aday kuyruğu canlıya inmez). DB erişilemezse sessizce atlar
        (deterministik çekirdek DB'ye bağımlı olmasın)."""
        try:
            import json as _json

            from sqlmodel import Session, select

            from app.llm import _norm
            from control_plane.db import engine
            from control_plane.models import SynonymOverride

            with Session(engine) as s:
                rows = s.exec(select(SynonymOverride).where(
                    SynonymOverride.approved == True)).all()  # noqa: E712
        except Exception:
            return
        if not rows:
            return
        by_name = {c.get("name"): c for c in cubes}
        for r in rows:
            if r.scope_type == "tenant" and r.scope_id != self.company_slug:
                continue
            cube = by_name.get(r.cube)
            if cube is None:
                continue
            try:
                extra = [_norm(str(x)) for x in _json.loads(r.synonyms_json)]
            except ValueError:
                continue
            if r.field_kind == "cube":
                pool = cube.setdefault("synonyms", [])
                for x in extra:
                    if x not in pool:
                        pool.append(x)
            elif r.field_kind == "measure" and r.field_name:
                pool = cube.setdefault("measure_synonyms", {}).setdefault(r.field_name, [])
                for x in extra:
                    if x not in pool:
                        pool.append(x)
            elif r.field_kind == "dimension" and r.field_name:
                pool = cube.setdefault("dimension_synonyms", {}).setdefault(r.field_name, [])
                for x in extra:
                    if x not in pool:
                        pool.append(x)

    def _apply_measure_overrides(self, cubes: list) -> None:
        """Control-plane DB'deki `MeasureOverride` (Faz 2d, ölçü GİZLEME) satırlarını
        uygular: eşleşen ölçünün `measure_synonyms` girdisini BOŞALTIR. `cube_router.
        _match_measure` YALNIZ `measure_synonyms`'a bakar (bare ölçü adına değil) — bu
        yüzden boşaltmak `route()`/`cube_only_match()`'in onu bir daha ÖNERMEMESİ için
        yeterli VE tektir; ölçü `measures` listesinden/YAML'dan SİLİNMEZ (eski VQR/
        dashboard/Contract kayıtları ölçüyü ADIYLA taşır, sinonim aramaz — kırılmazlar).
        DB erişilemezse sessizce atlar (deterministik çekirdek DB'ye bağımlı olmasın)."""
        try:
            from sqlmodel import Session, select

            from control_plane.db import engine
            from control_plane.models import MeasureOverride

            with Session(engine) as s:
                rows = s.exec(select(MeasureOverride)).all()
        except Exception:
            return
        if not rows:
            return
        by_name = {c.get("name"): c for c in cubes}
        for r in rows:
            if r.scope_type == "tenant" and r.scope_id != self.company_slug:
                continue
            cube = by_name.get(r.cube)
            if cube is None:
                continue
            msyn = cube.get("measure_synonyms")
            if msyn is not None and r.measure_name in msyn:
                msyn[r.measure_name] = []

    def _enrich_cube_dim_values(self, cubes: list, mdl: dict, models: list) -> None:
        """Cube boyutlarının olası değerlerini `dimension_values` olarak ekler.

        Model kolonundan gelenler hazır (enrich_categorical); TÜREV boyutlar
        (ör. hafta_gunu = CASE isodow(...)) motor üzerinden DISTINCT ile toplanır →
        yorum chip'lerinin alternatif listeleri ("sadece Pzt" vb.) buradan beslenir.
        Hata olursa sessizce atlar.

        🔴🔴 **`§DK` — KATALOG GARSONA YALAN SÖYLÜYORDU; kısayol ADA bakıyordu.**

        ## Ölçülen kusur (canlı, 2026-08-10)

        Kısayol `col_vals`'ı **80 modelin kolonlarını tek sözlükte** düzleştirerek
        kuruyordu ve eşleşmeyi **boyut ADI** üzerinden yapıyordu. Bir küp boyutunun
        adı başka bir modelin ham kolonuyla çakışırsa, o kolonun değerleri küpün
        **kendi ifadesini gölgeliyordu** — ve `expression` satırına hiç gelinmiyordu.

        | küp·boyut | küpün İFADESİ (verinin gerçeği) | enum (garsona söylenen) |
        |---|---|---|
        | `parti.musteri` | `musteri_ad` → *TOROS ÖRME TİC. LTD. ŞTİ.* | `M1001…` 🔴 |
        | `kalite.musteri` | `musteri_ad` | `M1001…` 🔴 |
        | `kalite.tedarikci` | `tedarikci_ad` | `T-101…` 🔴 |
        | `kalite.vardiya` | `CASE … '1. Vardiya (08-16)'` | `1 · 2 · 3` 🔴 |
        | `makine_duruslari.vardiya` | aynı `CASE` | `1 · 2 · 3` 🔴 |

        ⊙ **43 boyutun ifadesi adından farklı** — kısayolun yalan söyleyebileceği küme
        buydu; beşi kanıtlandı. `hafta_gunu`·`yas_grubu` gibi adı hiçbir ham kolonla
        çakışmayanlar **doğru** çalışıyordu, çünkü onlar zaten DISTINCT yoluna düşüyordu.

        ## Bedeli bir kolaylık değil, bir SESSİZ YANLIŞ

            «bu yıl 1. vardiyada fire oranı» → 3 vardiya birden döndü,
                                               ilk satır «3. Vardiya (00-08)»,
                                               süzgeç sessizce düştü, BEYAN YOK.

        Kullanıcı 1. vardiyayı sordu, 3. vardiyanın sayısını okudu. Değer eşleşmesi
        tutmadı çünkü katalog `'1'` diyordu, veri `'1. Vardiya (08-16)'` tutuyordu.

        ## Düzeltme — *doğruyu yalnız İFADE söyler*

        Kısayol **kaldırılmadı, kanıta bağlandı**: yalnız değerlerin **o küpün kendi
        `baseObject` modelinin** kolonundan geldiği ve ifadenin **o kolonun çıplak adı**
        olduğu durumda kullanılır (`(base, expr)` anahtarı). Aksi hâlde değerler,
        sorgunun kullanacağı **ifadenin kendisiyle** motordan DISTINCT ile toplanır.

        ⚠ Düzleştirilmiş ad sözlüğü yalnız **ifadesi olmayan** boyutlar için kaldı:
        orada karşılaştırılacak bir ifade yok, ve elde olan en iyi kaynak odur.

        *Bir katalog, sorgunun kullanacağı ifadeden başka bir yerden okunuyorsa, er ya
        da geç ondan ayrışır — ve ayrıştığı gün kimse fark etmez, çünkü ikisi de
        geçerli birer cevap üretir.*
        """
        #: `(model, kolon) → değerler` — **çakışmaz** anahtar. Eski düz sözlük
        #: (`kolon → değerler`) 80 modeli tek düzleme indiriyordu ve son yazan
        #: kazanıyordu; hangi modelin kazandığı sözlük ekleme sırasına bağlıydı.
        col_vals_tam = {
            (m["name"], c["name"]): c["values"]
            for m in models
            for c in m["columns"]
            if c.get("values")
        }
        #: Yalnız **ifadesiz** boyutlar için yedek (karşılaştırılacak ifade yok).
        col_vals = {
            c["name"]: c["values"]
            for m in models
            for c in m["columns"]
            if c.get("values")
        }
        mdl_cubes = {c.get("name"): c for c in mdl.get("cubes", [])}

        # TÜREV boyutları TEK sorguda topla (Faz B1) — aynı gerekçe: maliyet DB'de değil
        # PLANLAMADA. Boyut başına bir plan yerine hepsi için bir plan.
        istekler: list[tuple[str, str, str, str]] = []  # (cube, boyut, base, ifade)
        vals_map: dict[str, dict[str, list[str]]] = {}
        for cube in cubes:
            vals_map[cube["name"]] = {}
            mc = mdl_cubes.get(cube["name"]) or {}
            base = mc.get("baseObject")
            for d in mc.get("dimensions", []):
                name = d.get("name")
                expr = d.get("expression")
                # 🔴 KISAYOL ARTIK KANITA BAĞLI (`§DK`): değerler **bu küpün kendi
                # baseObject modelinin** kolonundan geldiyse ve ifade o kolonun
                # **çıplak adıysa**, DISTINCT ile birebir aynı sonucu verir → ucuz yol.
                if base and expr and (base, expr) in col_vals_tam:
                    vals_map[cube["name"]][name] = col_vals_tam[(base, expr)]
                    continue
                # İfade var ama çıplak bir kolon değil (CASE · COALESCE · ilişki
                # üzerinden düzleştirilmiş ad) → **doğruyu yalnız ifade söyler**.
                if base and expr:
                    istekler.append((cube["name"], name, base, expr))
                    continue
                # İfadesiz boyut: karşılaştırılacak bir ifade yok, elde olan en iyi
                # kaynak düzleştirilmiş ad sözlüğüdür.
                if name in col_vals:
                    vals_map[cube["name"]][name] = col_vals[name]

        if istekler:
            def _parca(i: int, base: str, expr: str) -> str:
                return (f"SELECT {i} AS _i, CAST(v AS VARCHAR) AS v FROM "
                        f"(SELECT DISTINCT {expr} AS v FROM {base} "
                        f"WHERE ({expr}) IS NOT NULL LIMIT {self._MAX_ENUM + 1})")
            kova: dict[int, list[str]] = {}
            try:
                with self._engine() as eng:
                    tablo = eng.query(" UNION ALL ".join(
                        _parca(i, b, e) for i, (_, _, b, e) in enumerate(istekler)),
                        properties=self._katalog_ozellikleri())
                for r in tablo.to_pylist():
                    kova.setdefault(r["_i"], []).append(self._fix_tr(str(r["v"])))
            except Exception:
                # Tek bozuk ifade hepsini düşürmesin → boyut-başına yedek.
                _log.warning("cube türev boyut toplu sorgusu başarısız — boyut-başına",
                             exc_info=True)
                try:
                    with self._engine() as eng:
                        for i, (_, _, b, e) in enumerate(istekler):
                            try:
                                kova[i] = [self._fix_tr(str(r["v"])) for r in eng.query(
                                    f"SELECT DISTINCT {e} AS v FROM {b} "
                                    f"WHERE ({e}) IS NOT NULL LIMIT {self._MAX_ENUM + 1}",
                                    properties=self._katalog_ozellikleri(),
                                ).to_pylist()]
                            except Exception:
                                continue
                except Exception:
                    _log.warning("cube türev boyut yedek yolu da başarısız", exc_info=True)
            for i, (cn, dn, _, _) in enumerate(istekler):
                got = kova.get(i) or []
                if 0 < len(got) <= self._MAX_ENUM:
                    # ORDER BY'sız DISTINCT sıra garantisi vermez → deterministik sırala.
                    vals_map[cn][dn] = sorted(got)

        for cube in cubes:
            cube["dimension_values"] = vals_map.get(cube["name"], {})

    def _yapisal_kurallar(self) -> list[dict]:
        """`knowledge/kurallar.yml` → kural listesi. Yoksa **boş** — ve bu doğrudur:
        kuralı olmayan bir sektör paketi bir kusur değil.

        ⚠ Bozuk bir dosya **sessizce yutulmaz**: loglanır ve boş dönülür. *Bir bilgi
        merkezinin okunamayan dosyası, olmayan dosyadan tehlikelidir — çünkü var
        sanılır.*
        """
        import yaml as _yaml

        # ⚠ Yol **`_load_knowledge` ile aynı köke** bağlı (`project_dir/knowledge`):
        # ikinci bir kök icat etmek, iki bilgi kaynağı yaratırdı ve biri bir gün
        # ötekinden ayrışırdı. (İlk yazımda olmayan bir `_knowledge_dirs()` varsaydım;
        # *bir yardımcıyı var sanmak, onu yazmakla aynı şey değildir.*)
        yol = self.project_dir / "knowledge" / "kurallar.yml"
        if not yol.exists():
            return []
        try:
            d = _yaml.safe_load(yol.read_text(encoding="utf-8")) or {}
            return list(d.get("kurallar") or [])
        except Exception:                                # noqa: BLE001
            _log.warning("yapısal kural dosyası okunamadı: %s", yol, exc_info=True)
            return []

    def _load_knowledge(self, sub: str) -> str:
        """knowledge/<sub>/*.md içeriğini prompt'a taşınmak üzere birleştirir (ADR-0005).

        rules → boyahane sektör paketinin 'kurallar' katmanı (metrik semantiği: oran→AVG,
        miktar→SUM). sql → doğrulanmış golden SQL örnekleri (analitik desenler).
        Hata olursa boş döner."""
        try:
            kdir = self.project_dir / "knowledge" / sub
            parts = [
                txt
                for f in sorted(kdir.glob("*.md"))
                if (txt := f.read_text().strip())
            ]
            return "\n\n".join(parts)
        except Exception:
            return ""

    def _enrich_categorical(self, models: list[dict[str, Any]],
                            phys: dict[str, str] | None = None) -> None:
        """Düşük kardinaliteli VARCHAR kolonlara `values` ekler (tek engine oturumu).

        NL→SQL'in "marmara boya" / "kırmızı" gibi değerlerle WHERE yazabilmesi için.
        Hata olursa sessizce atlar (şema yine döner).

        HASSASİYET BURADA DAMGALANIR, BURADA ELENMEZ (Faz A1). Değerler örneklenmeye devam
        eder çünkü **iki farklı tüketici** var ve ikisinin hakkı aynı değil:
          * `cube_router.route()` — SÜREÇ İÇİNDE çalışır, veri kurumdan ÇIKMAZ; "Aylin
            Bulut'un firesi" gibi bir soruyu deterministik çözebilmesi için değerleri
            görmesi GEREKİR. Burada eleseydik bu yetenek sessizce ölürdü.
          * LLM prompt'u — veri **üçüncü tarafa gider**; hassas değer oraya giremez.
        Sınır bu yüzden kaynakta değil **prompt sınırındadır** (bkz. `app/sensitivity.py`
        `prompt_safe_values`). Kolona `sensitivity` damgası basılır ki her tüketici
        hakkını bilsin ve CI tarafı denetlenebilsin.
        """
        from app.sensitivity import classify

        # 1) Hassasiyet damgası + hedef kolonlar (fiziksel, VARCHAR).
        hedef: list[tuple[str, str, dict]] = []       # fiziksel → konnektör (toplu, hızlı)
        turev: list[tuple[str, str, dict]] = []       # calc → motor (semantik katman şart)
        for m in models:
            fiziksel = (phys or {}).get(m.get("name"))
            for c in m["columns"]:
                if (sv := classify(c)) != "normal":
                    c["sensitivity"] = sv
                if not str(c.get("type", "")).upper().startswith("VARCHAR"):
                    continue
                if c.get("is_calculated") or c.get("relationship"):
                    # Calc kolon tabloda YOK — ifadesi bir ilişki üzerinden çözülür, yani
                    # semantik katman ŞART. Konnektöre gönderilirse "kolon bulunamadı" der
                    # ve o kolon değerlerini SESSİZCE kaybederdi; `route()` ise model
                    # kolonlarının `values`'ını kategorik filtre için OKUYOR (ör.
                    # `operator_cinsiyet = 'Kadın'`). Ölçüldü: bu ayrım olmadan 19 kolon
                    # değerini kaybediyordu. Sayıları az olduğu için motor yolu ucuz.
                    turev.append((m.get("name"), c["name"], c))
                    continue
                if fiziksel:
                    hedef.append((fiziksel, c["name"], c))
        if turev:
            self._enrich_categorical_yavas(turev)
        if not hedef:
            return

        # 2) TEK sorgu, KONNEKTÖR üzerinden (Faz B1).
        #
        # ÖLÇÜLDÜ (2 Ağustos 2026): eski hâli kolon başına bir `eng.query()` atıyordu —
        # 183 sorgu, **2188 ms**. Maliyetin **%97'si planlamaydı**, %3'ü DB (aynı sorgu
        # doğrudan DuckDB'de 0,70 ms, motor üzerinden 22,65 ms). Sebep: her çağrı 118 KB'lık
        # manifesti yeniden çözüp sqlglot'la ayrıştırıyor ve yeni bir `ManifestExtractor`
        # kuruyor. Motoru uzun ömürlü tutmak İŞE YARAMADI (ölçüldü: 5,54 → 5,50 ms) çünkü
        # maliyet motor kurulumunda değil, **her plan çağrısında**.
        #
        # Asıl içgörü: bu sorgular `SELECT DISTINCT kolon FROM tablo` — **fiziksel** bir iş.
        # Semantik katmanın katkısı YOK. Konnektör üzerinden tek `UNION ALL` ile: **98 ms**
        # (22× hızlı, birebir aynı 2735 satır).
        #
        # GÜVENLİK NOTU: bu yol kullanıcı SQL'i taşımaz — sorgu tamamen MDL metadata'sından
        # (fiziksel tablo + kolon adı) üretilir. Kullanıcı SQL'i `dry_plan`/`query`'den,
        # dolayısıyla `guard_sql` + SQL politikasından geçmeye devam eder.
        def _parca(fiz: str, kol: str) -> str:
            return (f"SELECT '{fiz}' AS _t, '{kol}' AS _c, CAST(v AS VARCHAR) AS v "
                    f'FROM (SELECT DISTINCT "{kol}" AS v FROM {fiz} '
                    f'WHERE "{kol}" IS NOT NULL LIMIT {self._MAX_ENUM + 1})')

        try:
            tablo = self._connector().query(" UNION ALL ".join(_parca(f, k) for f, k, _ in hedef))
            kova: dict[tuple[str, str], list] = {}
            for r in tablo.to_pylist():
                kova.setdefault((r["_t"], r["_c"]), []).append(r["v"])
        except Exception:
            # YEDEK YOL: konnektör/nitelikli-ad bu datasource'ta beklendiği gibi çalışmazsa
            # eski (yavaş ama kanıtlanmış) kolon-başına yol. Hız bir iyileştirmedir;
            # değer indeksinin KAYBOLMASI bir gerilemedir — o yüzden fail-open.
            _log.warning("değer indeksi toplu sorgusu başarısız — kolon-başına yola dönülüyor",
                         exc_info=True)
            self._enrich_categorical_yavas(hedef)
            return

        for fiz, kol, c in hedef:
            vals = kova.get((fiz, kol)) or []
            if 0 < len(vals) <= self._MAX_ENUM:
                c["values"] = sorted(self._fix_tr(str(v)) for v in vals)

    def _enrich_categorical_yavas(self, hedef: list) -> None:
        """Motor üzerinden değer örnekleme — calc kolonlar (semantik katman şart) ve
        konnektör yolu başarısız olduğunda yedek.

        Burada da TEK sorgu (UNION ALL) kullanılır: maliyet DB'de değil **planlamada**
        (ölçüldü: aynı sorgu doğrudan 0,70 ms, motor üzerinden 22,65 ms). N kolon için
        N plan yerine 1 plan. Tek sorgu patlarsa kolon-başına yola düşülür — bir kolonun
        ifadesi bozuksa hepsini kaybetmemek için.
        """
        if not hedef:
            return
        def _parca(kaynak: str, kol: str) -> str:
            return (f"SELECT '{kaynak}' AS _t, '{kol}' AS _c, CAST(v AS VARCHAR) AS v "
                    f"FROM (SELECT DISTINCT {kol} AS v FROM {kaynak} "
                    f"WHERE {kol} IS NOT NULL LIMIT {self._MAX_ENUM + 1})")
        try:
            with self._engine() as eng:
                tablo = eng.query(" UNION ALL ".join(_parca(k, c) for k, c, _ in hedef),
                                  properties=self._katalog_ozellikleri())
            kova: dict[tuple[str, str], list] = {}
            for r in tablo.to_pylist():
                kova.setdefault((r["_t"], r["_c"]), []).append(r["v"])
            for kaynak, kol, c in hedef:
                vals = kova.get((kaynak, kol)) or []
                if 0 < len(vals) <= self._MAX_ENUM:
                    c["values"] = sorted(self._fix_tr(str(v)) for v in vals)
            return
        except Exception:
            _log.warning("değer indeksi toplu motor sorgusu başarısız — kolon-başına",
                         exc_info=True)
        try:
            with self._engine() as eng:
                for kaynak, kol, c in hedef:
                    try:
                        vals = [r["v"] for r in eng.query(
                            f"SELECT DISTINCT {kol} AS v FROM {kaynak} "
                            f"WHERE {kol} IS NOT NULL LIMIT {self._MAX_ENUM + 1}",
                            properties=self._katalog_ozellikleri(),
                        ).to_pylist()]
                    except Exception:
                        continue
                    if 0 < len(vals) <= self._MAX_ENUM:
                        c["values"] = sorted(self._fix_tr(str(v)) for v in vals)
        except Exception:
            _log.warning("değer indeksi yedek yolu da başarısız", exc_info=True)

    @property
    def mdl_version(self) -> str:
        """Derlenmiş MDL'in sürüm damgası (ADR-0010): sözleşmede saklanır — replay'de
        "şema değişti mi?" sorusunun deterministik cevabı."""
        import hashlib

        # ÖNBELLEK ARTIK DOSYAYA BAĞLI (2 Ağustos 2026). Eskiden `_mdl_ver` bir kez
        # hesaplanıp NESNE ÖMRÜ boyunca saklanıyordu; `invalidate_schema_cache()` onu
        # düşürmüyordu. Sonucu: yeniden compose sonrası Query Contract'lar ESKİ MDL
        # sürümüyle damgalanıyordu — yani "şema değişti mi?" sorusunun cevabı yanlıştı,
        # ki sözleşmenin tek varlık sebebi budur (ADR-0010). `_mdl_bytes()` (mtime_ns+size
        # anahtarlı) yeni dosyada kendiliğinden tazelenir.
        try:
            return hashlib.sha256(self._mdl_bytes()).hexdigest()[:12]
        except Exception:
            return "unknown"

    def cube_sql(self, cube_query: dict[str, Any], order=None, limit: int | None = None) -> str:
        """Yapısal CubeQuery → deterministik SQL (Wren `cube_query_to_sql`, LLM'siz).

        İsteğe bağlı dış sıralama/limit sarmalar (cube query'nin kendisi ölçüye göre
        sıralamayı desteklemez)."""
        import json

        from wren_core import cube_query_to_sql

        cq = dict(cube_query)
        # CubeQuery'ye gömülü sıralama/limit (konuşmasal düzenleme: "en düşük", "ilk 5")
        # — Wren cube_query_to_sql bunları tanımaz, ayıklayıp dışarıdan sararız.
        emb_order = cq.pop("order", None)  # {"measure": <m>, "direction": "asc|desc"}
        emb_limit = cq.pop("limit", None)
        # ÖLÇÜ EŞİĞİ (HAVING, "10 milyon üzeri"): cube derleyici HAVING üretmez — agregat
        # ölçü ALIAS'ına dış WHERE ile uygulanır (duckdb lehçesinde sarılır, sonra transpile).
        emb_having = cq.pop("measure_having", None)
        if order is None and isinstance(emb_order, dict) and emb_order.get("measure"):
            d = str(emb_order.get("direction") or "desc").lower()
            order = (emb_order["measure"], "ASC" if d.startswith("a") else "DESC")
        if limit is None and emb_limit:
            limit = int(emb_limit)

        # AYRIK AYLAR ("ocak ve mart") — motor bunu YEREL OLARAK İFADE EDEMİYOR (ölçüldü,
        # `cube_router.ayrik_ay_kovalari` docstring'i): `in` operatörü kabul ediliyor ama
        # HAM tarih kolonuna uygulanıyor, ay kovasına değil; çoklu `dateRange` ve
        # `tarih__month` filtresi de reddediliyor. Çözüm: ay granülerliğinde GRUPLA, sonra
        # kesilmiş kolona DIŞARIDAN filtre uygula — toplama gruplamadan ÖNCE bittiği için
        # sonuç kesindir (`measure_having` ile AYNI sarma kalıbı).
        emb_ayrik = cq.pop("ayrik_aylar", None)
        # 🔴 `M-9`/`M-3` — PENCERE ve TÜREV: `ayrik_aylar` ile **aynı sarma kalıbı**.
        # Gerekçe ve neden kataloğa DEĞİL buraya kondukları `_pencere_sar`'da.
        emb_pencere = cq.pop("pencere", None)
        emb_turev = cq.pop("turev", None)
        base = cube_query_to_sql(json.dumps(cq), self._mdl_bytes().decode())
        base = self._inject_always_filter(base, cq.get("cube"))
        if emb_ayrik:
            base = self._ayrik_ay_sar(base, cq, emb_ayrik)
        if emb_turev:
            base = self._turev_sar(base, cq, emb_turev)
        if emb_pencere:
            base = self._pencere_sar(base, cq, emb_pencere)
        if isinstance(emb_having, dict) and emb_having.get("measure") and emb_having.get("op"):
            _op = {">": ">", "<": "<", ">=": ">=", "<=": "<="}.get(emb_having["op"], ">")
            base = (f"SELECT * FROM ({base}) AS _hv "
                    f"WHERE {emb_having['measure']} {_op} {float(emb_having['value'])}")
        if self.datasource in ("duckdb", "", None):
            if order or limit:
                base = f"SELECT * FROM ({base}) AS _c"
                if order:
                    base += f" ORDER BY {order[0]} {order[1]}"
                if limit:
                    base += f" LIMIT {int(limit)}"
            return base
        return self._dialect_sql(base, order=order, limit=limit)

    @staticmethod
    def _ayrik_ay_sar(base: str, cq: dict[str, Any], isaret: dict[str, Any]) -> str:
        """Ay-kovalı sonucu, kullanıcının SAYDIĞI aylara daraltır — FAIL-CLOSED.

        İşaret (`ayrik_aylar`) ve kapsayan aralık filtresi **birlikte** anlamlıdır: aralık
        tek başına araya giren ayları da içerir. İşaret varken ay granülerliği yoksa sarma
        yapılamaz ve **sessizce kapsayan aralığa düşmek** cube rozetli bir yanlış cevap
        üretirdi — bu deponun en tehlikeli sınıfı. O yüzden burada `ValueError` atılır:
        derlenmeyen bir sorgu, sessizce yanlış bir sorgudan iyidir.
        """
        aylar = [str(a) for a in (isaret.get("aylar") or [])]
        dim = str(isaret.get("dimension") or "")
        tds = cq.get("timeDimensions") or []
        if not aylar or not dim:
            raise ValueError(f"ayrik_aylar işareti eksik/bozuk: {isaret!r}")
        if not any(t.get("dimension") == dim and t.get("granularity") == "month"
                   for t in tds):
            raise ValueError(
                f"ayrik_aylar işareti var ama '{dim}' üzerinde ay granülerliği YOK "
                f"(timeDimensions={tds!r}). Sarma uygulanamaz; kapsayan aralığa sessizce "
                f"düşmek araya giren ayları da katardı.")
        kume = ", ".join(f"DATE '{a}'" for a in aylar)
        return f"SELECT * FROM ({base}) AS _ay WHERE {dim}__month IN ({kume})"

    #: 🔴 `M-9` — PENCERE KİPLERİ. **Kapalı küme**: her biri bir `OVER (…)` ifadesidir ve
    #: motorun kendi cebri değil, onun **üstüne** yazılan bir sarmadır.
    from app.cube_operatorleri import PENCERE_KIPLERI as _PENCERE_KIPLERI

    @classmethod
    def _pencere_sar(cls, base: str, cq: dict[str, Any], istek: dict[str, Any]) -> str:
        """🔴🔴 **`M-9` — PENCERE KATMANI.** [FAIL-CLOSED]

        ## Ölçülen kusur

        `CubeQuery` yalnız **GROUP BY** cebri konuşuyor. `OVER (PARTITION BY … ORDER BY …)`
        ailesi — kümülatif · hareketli ortalama · grup-içi sıra · önceki dönem — **hiçbir
        katmanda yoktu** (`app/` içinde `PARTITION BY` **sıfır** kez geçiyordu). Sonuç,
        canlı turlarda **sessiz kapsam daralması**:

            p15  `bu yıl aylık **kümülatif** fire toplamını göster`  → düz aylık seri
            r18  `son 12 ayın **hareketli** 3 aylık ortalaması`      → düz aylık seri
            r12  `her biri için **en sık** rework sebebi`            → 66 satır (grup-içi ilk-1 yok)

        Üçünde de `niyet.bilinmeyenler` düşen kelimeyi **yazıyordu** ve cevap sessizce
        dar geliyordu — *"anlamadım"* değil, **sorulanın bir parçasına** verilmiş doğru
        bir cevap. `KÖK-3`'ün kapsamadığı bölge.

        ## 🔴 Raporun formu DÜZELTİLDİ — ve düzeltmenin sebebi ÖLÇÜLDÜ

        `MUTFAK-DENETIMI` bu alanı **menü dosyasına** (ölçü düzeyi `pencere:`) koyuyordu.
        `M-2`'de ölçüldü ki **MDL'de bir ölçünün alanları sabittir**
        (`name·expression·type·unit·synonyms`); yeni bir anahtar ya derlemede düşer ya
        motorun `serde`'si tüm projeyi reddeder (*"unknown variant"*).

        ⊙ Oysa bu deponun **kendi kalıbı** zaten doğru yeri gösteriyor: `measure_having` ·
        `ayrik_aylar` · `entity_limit` · `blend` — dördü de **CubeQuery alanıdır**,
        kataloğa hiç girmezler. `pencere` de öyle olmalı. Ve bunun bir **yan kazancı** var:
        pencere artık *önceden tanımlanmış* olmak zorunda değil — kullanıcının o anki
        sorusundan doğabilir.

        *Bir yeteneği kataloğa yazmak, onu birinin önceden yazmış olmasına bağlamaktır.*

        ## Sınır — fail-closed

        ⚠ Sıralama ekseni **uydurulmaz**: açıkça verilmemişse `timeDimensions`'tan
        türetilir (`<boyut>__<granülerlik>` — tabanın gerçek kolon adı). İkisi de yoksa
        `ValueError`. *Sırasız bir pencere, rastgele bir birikimdir.*

        ⚠ Pencereli sonuç **toplanamaz** (`M-5`): kümülatif bir seriyi ikinci kez toplamak
        küp rozetli bir sessiz-yanlış üretir. Bu yüzden sarma **en dışta** durur ve türev
        kolon adı `_p_` önekiyle ayrılır — bir sonraki katmanın onu ham ölçü sanmaması için.
        """
        kip = str(istek.get("kip") or "")
        taban = str(istek.get("taban") or "")
        if kip not in cls._PENCERE_KIPLERI:
            raise ValueError(f"pencere kipi tanınmıyor: {kip!r} — {cls._PENCERE_KIPLERI}")
        if not taban:
            raise ValueError(f"pencere işareti eksik: taban yok ({istek!r})")
        sira = str(istek.get("siralama") or "") or cls._zaman_kolonu(cq)
        # ⚠ `sira` kipi **ölçüye göre** sıralar (grup-içi rütbe); zaman eksenine ihtiyacı
        # yoktur. İlk yazımım onu da zorunlu tutuyordu ve canlı sondaj bunu **gürültüyle**
        # gösterdi (HTTP 400 + `ValueError`) — yani fail-closed tam çalıştı, kusur
        # yüklemin kendisindeydi. *Bir ön koşulu tüm kiplere dayatmak, kipleri
        # ayırmamaktır.*
        if not sira and kip not in ("sira", "pay"):
            raise ValueError(
                "pencere işareti var ama sıralama ekseni YOK: ne `siralama` verildi ne de "
                "`timeDimensions` var. Sırasız bir pencere rastgele bir birikimdir.")
        bolum = [str(b) for b in (istek.get("bolum") or []) if b]
        part = f"PARTITION BY {', '.join(bolum)} " if bolum else ""
        ad = f"_p_{kip}_{taban}"
        if kip == "kumulatif":
            ifade = (f"SUM({taban}) OVER ({part}ORDER BY {sira} "
                     f"ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)")
        elif kip == "hareketli_ort":
            n = int(istek.get("pencere_boyu") or 3)
            if n < 2:
                raise ValueError(f"hareketli ortalama için pencere_boyu >= 2 olmalı ({n})")
            ifade = (f"AVG({taban}) OVER ({part}ORDER BY {sira} "
                     f"ROWS BETWEEN {n - 1} PRECEDING AND CURRENT ROW)")
        elif kip == "sira":
            yon = "ASC" if str(istek.get("yon") or "desc").lower().startswith("a") else "DESC"
            ifade = f"ROW_NUMBER() OVER ({part}ORDER BY {taban} {yon})"
        elif kip == "pay":
            # *"toplam içindeki payı"* — bölen, satırın kendisi değil **bütün**tür.
            # `bolum` verilmezse payda TÜM sonucun toplamıdır (`OVER ()`).
            ifade = (f"ROUND(100.0 * {taban} / "
                     f"NULLIF(SUM({taban}) OVER ({part.rstrip()}), 0), 2)")
        elif kip == "onceki":
            ifade = f"LAG({taban}) OVER ({part}ORDER BY {sira})"
        else:  # degisim_yuzde — önceki döneme göre yüzde değişim
            onc = f"LAG({taban}) OVER ({part}ORDER BY {sira})"
            ifade = f"ROUND(100.0 * ({taban} - {onc}) / NULLIF({onc}, 0), 2)"
        return f"SELECT *, {ifade} AS {ad} FROM ({base}) AS _pn"

    #: 🔴 `M-3` — TÜREV KİPLERİ. `yuzde`/`oran` bir **bölme**, `fark` bir çıkarma.
    from app.cube_operatorleri import TUREV_KIPLERI as _TUREV_KIPLERI

    @classmethod
    def _turev_sar(cls, base: str, cq: dict[str, Any], istek: dict[str, Any]) -> str:
        """🔴 **`M-3` — TÜREV ÖLÇÜ: oran · pay · fark.** [FAIL-CLOSED]

        Ölçülen kusur: `CubeQuery`'nin ölçü alanı bir **ad listesidir**; ölçü **aritmetiği**
        için yer yok. *"Toplam üretimin yüzde kaçı fire"* sorusuna sistem ancak biri
        `fire_orani_yuzde`'yi **önceden yazdıysa** cevap verebiliyordu. Yani türev ölçü
        kapasitesi = *birinin önceden yazmış olması*.

        ⊙ Ve bu, `p16` (`her hattın toplam fire içindeki **payı**`) ile `o7`'de canlıda
        ölçüldü: `payı` `bilinmeyen`'e yazıldı, cevap **mutlak kg** döndü, **beyan yok**.

        ⚠ **Neden ham `expression:` yazmak yanlış çözüm** (raporun kendi gerekçesi):
        ham SQL **toplanabilirlik bilgisini taşımaz** — `SUM(a)/SUM(b)` ile `AVG(a/b)`
        arasındaki fark SQL'de görünmez, **ölçü cebrinde** görünür. Burada bölme
        **gruplamadan sonra** yapılır, yani `SUM(pay)/SUM(payda)` semantiği korunur:
        taban zaten gruplanmış gelir.

        ⚠ Fail-closed: pay ve payda **tabanın kolonlarında** olmalı; olmadığı hâlde
        sarmak, motorun tanımadığı bir ada bölme yazmak olurdu.
        """
        kip = str(istek.get("kip") or "yuzde")
        pay, payda = str(istek.get("pay") or ""), str(istek.get("payda") or "")
        if kip not in cls._TUREV_KIPLERI:
            raise ValueError(f"türev kipi tanınmıyor: {kip!r} — {cls._TUREV_KIPLERI}")
        olculer = [str(m) for m in (cq.get("measures") or [])]
        if kip != "fark" and pay and pay == payda:
            # 🔴 Ölçüldü (`p16`, canlı): garson *"toplam içindeki payı"* için
            # `pay=payda=toplam_fire_kg` üretti → her satır **%100**. Bir ölçünün kendine
            # oranı hiçbir zaman kastedilen şey değildir; ve asıl istenen **pencere**
            # kipidir (`pay`). Sessizce %100 döndürmek küp rozetli bir sessiz-yanlıştır.
            raise ValueError(
                f"türev pay ve payda AYNI ölçü ({pay!r}) — sonuç her satırda %100 olurdu. "
                f"«toplam içindeki payı» için `pencere:{{kip:'pay'}}` kullanılır.")
        if pay not in olculer or (kip != "fark" and payda not in olculer):
            raise ValueError(
                f"türev işareti tabanda olmayan ölçüye bakıyor (pay={pay!r} payda={payda!r}, "
                f"measures={olculer!r}). Sessizce düşmek yerine reddedilir.")
        if kip == "fark":
            ifade, ad = f"({pay} - {payda})", f"_t_fark_{pay}"
        elif kip == "oran":
            ifade, ad = f"(1.0 * {pay} / NULLIF({payda}, 0))", f"_t_oran_{pay}"
        else:
            ifade, ad = (f"ROUND(100.0 * {pay} / NULLIF({payda}, 0), 2)",
                         f"_t_yuzde_{pay}")
        return f"SELECT *, {ifade} AS {ad} FROM ({base}) AS _tv"

    @staticmethod
    def _zaman_kolonu(cq: dict[str, Any]) -> str:
        """Tabanın zaman kolonunun **gerçek adı** (`tarih__month`) — tek sahip.

        ⚠ İkinci bir ad üretici yazılmadı: bu biçim `cube_query_to_sql`'in çıktısında
        kullanılıyor ve `_ayrik_ay_sar` de aynı biçimi varsayıyor (`{dim}__month`)."""
        for t in (cq.get("timeDimensions") or []):
            d, g = t.get("dimension"), t.get("granularity")
            if d and g:
                return f"{d}__{g}"
        return ""

    def blend_sql(self, cube_query: dict[str, Any]) -> str:
        """CROSS-CUBE BLEND: birden çok cube'un ölçüsünü PAYLAŞILAN gruplama anahtarlarında
        (zaman kovası + ortak boyutlar) FULL OUTER JOIN ile TEK tabloda birleştirir. Her cube
        kendi taban tablosundan toplanır (farklı grain — faturalar vs karlilik_src); sonuçlar
        anahtar üstünde eşlenir. "her sorguda tüm eksenler" vizyonunun yürütme primitifi.

        cube_query: normal alanlar + `blend: [{cube, measures}, ...]` (ek cube'lar). Paylaşılan
        dimensions/timeDimensions/filters TÜM cube'lara uygulanır (çağıran, hepsinde var
        olduğunu garantiler). Her CTE base (DuckDB) SQL'dir; blend'in tamamı sonda tek
        _dialect_sql'le hedef lehçeye çevrilir (CTE içi GROUP BY/DATE_TRUNC dahil)."""
        import json
        import re

        from wren_core import cube_query_to_sql

        # FAIL-CLOSED: blend her CTE'yi AÇIK alanlardan yeniden kurar ve `ayrik_aylar`
        # işaretini KOPYALAMAZ. Sessizce düşerse geriye kapsayan aralık kalır ve cevap
        # araya giren ayları da içerir — cube rozetli sessiz-yanlış. Reddetmek doğrudur.
        if cube_query.get("ayrik_aylar"):
            raise ValueError(
                "ayrik_aylar + blend birlikte desteklenmiyor: blend CTE'leri işareti "
                "taşımaz ve sonuç sessizce kapsayan aralığa düşerdi.")

        mdl = self._mdl_bytes().decode()
        parts = [{"cube": cube_query["cube"], "measures": list(cube_query.get("measures") or [])}]
        parts += [{"cube": p["cube"], "measures": list(p.get("measures") or [])}
                  for p in (cube_query.get("blend") or [])]
        shared_dims = list(cube_query.get("dimensions") or [])
        shared_time = list(cube_query.get("timeDimensions") or [])
        shared_filters = list(cube_query.get("filters") or [])
        key_cols = [f'{td["dimension"]}__{td["granularity"]}' for td in shared_time] + shared_dims

        ctes: list[tuple[str, str, list[str]]] = []
        seen_measures: set[str] = set()
        for i, p in enumerate(parts):
            measures = [m for m in p["measures"] if m not in seen_measures]  # ad çakışması korumas
            seen_measures.update(measures)
            sub: dict[str, Any] = {"cube": p["cube"], "measures": measures}
            if shared_dims:
                sub["dimensions"] = shared_dims
            if shared_time:
                sub["timeDimensions"] = shared_time
            if shared_filters:
                sub["filters"] = shared_filters
            base = cube_query_to_sql(json.dumps(sub), mdl)
            base = self._inject_always_filter(base, p["cube"])
            base = re.sub(r"\s+ORDER\s+BY\s+[\d,\s]+\s*$", "", base, flags=re.I)  # CTE'de ORDER BY yasak
            ctes.append((f"c{i}", base, measures))

        # COALESCE ≥2 argüman ister (SQL Server tek-arg'ı ")'de syntax hatası" sayar) —
        # tek CTE varken düz kolon, çok CTE'de COALESCE.
        def _coalesce(exprs: list[str]) -> str:
            return exprs[0] if len(exprs) == 1 else f'COALESCE({", ".join(exprs)})'

        sel = [f'{_coalesce([f"{c}.{k}" for c, _, _ in ctes])} AS {k}' for k in key_cols]
        sel += [f"{c}.{m} AS {m}" for c, _, ms in ctes for m in ms]
        frm = ctes[0][0]
        prior = [ctes[0][0]]
        for c, _, _ in ctes[1:]:
            if key_cols:
                on = " AND ".join(
                    f'{_coalesce([f"{pc}.{k}" for pc in prior])} = {c}.{k}'
                    for k in key_cols)
                frm += f" FULL OUTER JOIN {c} ON {on}"
            else:
                frm += f" CROSS JOIN {c}"  # kırılımsız (toplam) → tek satır × tek satır
            prior.append(c)
        with_clause = ", ".join(f"{c} AS ({sql})" for c, sql, _ in ctes)
        # ORDER BY 1 (ordinal, ilk anahtar) — cube'un kendi deseniyle aynı: sqlglot ordinal'e
        # dokunmaz, mssql connector'ın flatten'ı basit ORDER BY 1'i doğru işler (alias/CASE
        # ORDER BY'ı upstream bug yüzünden bozuyordu). Anahtarsız (toplam) blend → sırasız.
        order = " ORDER BY 1" if key_cols else ""
        blend = f"WITH {with_clause} SELECT {', '.join(sel)} FROM {frm}{order}"
        if self.datasource in ("duckdb", "", None):
            return blend
        return self._dialect_sql(blend)

    def _inject_always_filter(self, sql: str, cube_name: str | None) -> str:
        """Cube-düzeyi `always_filter`'ı (LookML sql_always_where) üretilen SQL'in
        WHERE'ine ekler — CANCELLED=0 tekrarını ölçü ifadelerinden kaldırır. Filtre
        ham SQL yüklem'idir (base kolonlarına), dialect-nötr; DuckDB/mssql ortak yol.
        cube_query_to_sql'den ÖNCE (base lehçesinde) uygulanır."""
        import json as _json

        # Manifest okunamıyorsa SESSİZCE geçme (2 Ağustos 2026). Eskiden buradaki
        # `except Exception: return sql` bir okuma hatasında filtresiz SQL döndürüyordu —
        # 20 satır aşağıdaki fail-closed bloğun ÖNLEMEK için yazıldığı şeyin ta kendisi.
        # Somut senaryo: compose penceresinde manifest yokken gelen sorgu `always_filter`
        # olmadan çalışıp iptal kayıtlarını toplama sızdırıyordu. (Pencere artık atomik
        # build ile kapatıldı — bkz. app/compose.py — ama koruma yine de fail-closed olmalı.)
        ham = self._mdl_bytes()

        # ⚠️ FAZ 1.1 — `on` kademesinde SAHİP MOTORDUR, uygulama katmanı elini çeker.
        # İki sahip olursa yüklem iki kez yazılır; `CANCELLED = 0` için zararsızdır ama
        # kural genel olmalı: bu depoda *"aynı kuralın iki sahibi"* birinci kusur sınıfı.
        #
        # 🔴 `shadow`'da sahip BURADA KALIR. Gölgenin işi ÖLÇMEK, davranmak değil: servis
        # edilen cevap `off` ile birebir aynı olmalı ki ölçüm bir kıyas olabilsin. Bu,
        # `strict_sql_policy`'nin gölge deseniyle aynı karar.
        if cube_name in rls.motorun_devraldigi_cubelar(ham, kademe=self._rls_kademesi()):
            return sql

        cubes = {c.get("name"): c for c in json.loads(ham).get("cubes", [])}
        cube = cubes.get(cube_name) or {}
        pred = cube.get("always_filter") or cube.get("alwaysFilter")
        if not pred:
            return sql
        import sqlglot
        from sqlglot import exp

        # FAIL-CLOSED (panel P0, Fable geniş): bilinen bir always_filter VARKEN enjeksiyon
        # başarısız olursa sessizce filtresiz SQL DÖNME — CANCELLED=0 düşerse iptal
        # faturaları toplama sızar (cube rozetli sessiz-yanlış, doğruluk-kritik yolda). Ret.
        try:
            tree = sqlglot.parse_one(sql, read="duckdb")
            cond = sqlglot.parse_one(str(pred), read="duckdb")
            sel = tree if isinstance(tree, exp.Select) else tree.find(exp.Select)
            if sel is None:
                raise ValueError("SELECT bulunamadı")
            sel.where(cond, copy=False)  # mevcut WHERE'e AND, yoksa oluşturur
            return tree.sql(dialect="duckdb")
        except Exception as e:
            raise RuntimeError(
                f"always_filter enjeksiyonu başarısız (cube={cube_name!r}, pred={pred!r}): {e} "
                "— sessiz iptal-kaydı sızıntısını önlemek için sorgu reddedildi"
            ) from e

    def _dialect_sql(self, sql: str, order=None, limit: int | None = None) -> str:
        """Cube derleyicisinin SQL'ini hedef lehçeye çevirir (ADR-0017 lab bulgusu).

        `cube_query_to_sql` çıktısı DuckDB/ANSI biçimindedir (DATE_TRUNC('month',..),
        GROUP BY 1); engine.dry_plan ise girdiyi HEDEF lehçe varsayar. sqlglot transpile
        + GROUP BY ordinal genişletme (T-SQL ordinal kabul etmez) yapılır.

        Sıralama/limit alt-sorgu SARMADAN doğrudan SELECT'e işlenir: mssql
        connector'ının `_flatten_pagination_limit`'i `SELECT TOP n * FROM (alt) ORDER
        BY` biçimini düzleştirirken dış WITH/ORDER BY'ı düşürüyor (upstream bug —
        fork'a dokunmama kararı gereği burada şekilden kaçınılır; wrapper yalnız
        DuckDB yolunda kalır)."""
        import sqlglot
        from sqlglot import exp

        write = {"mssql": "tsql", "sqlserver": "tsql"}.get(self.datasource, self.datasource)
        tree = sqlglot.parse_one(sql, read="duckdb")
        if order and isinstance(tree, exp.Select):
            # İstenen sıralama, cube'un varsayılan ORDER BY 1'inin (zaman kovası)
            # yerine geçer — wrapper davranışıyla birebir.
            tree.set("order", exp.Order(expressions=[
                exp.Ordered(this=exp.column(order[0]), desc=str(order[1]).upper() == "DESC")
            ]))
        if limit and isinstance(tree, exp.Select):
            tree.set("limit", exp.Limit(expression=exp.Literal.number(int(limit))))
        for select in tree.find_all(exp.Select):
            group = select.args.get("group")
            if not group:
                continue
            exprs = select.expressions
            expanded = []
            for g in group.expressions:
                if isinstance(g, exp.Literal) and g.is_int and 1 <= int(g.name) <= len(exprs):
                    e = exprs[int(g.name) - 1]
                    expanded.append((e.this if isinstance(e, exp.Alias) else e).copy())
                else:
                    expanded.append(g)
            group.set("expressions", expanded)
        if write == "tsql":
            # DATETRUNC yalnız SQL Server 2022+; müşteri sunucuları eski olabilir
            # (Gitaş: 2017). Her sürümde çalışan klasik desen kullanılır:
            # DATE_TRUNC('ay', x) → DATEADD(MONTH, DATEDIFF(MONTH, 0, x), 0).
            for node in list(tree.find_all(exp.DateTrunc, exp.TimestampTrunc)):
                unit = (node.args.get("unit").name
                        if node.args.get("unit") is not None else "day")
                col = node.this.sql(dialect="tsql")
                node.replace(sqlglot.parse_one(
                    f"DATEADD({unit}, DATEDIFF({unit}, 0, {col}), 0)", read="tsql"))
            # DEĞER EŞLEŞME (canlı 2026-07: 'soya fasülyesi' ≠ DB 'SOYA FASULYESİ' → 0 satır):
            # metin eşitlik/IN karşılaştırmalarına COLLATE Turkish_CI_AI — büyük/küçük + aksan
            # (ü=u, i=İ) duyarsız. İç kodlara (GCKOD='C') zararsız (yine eşleşir). Kullanıcı
            # yazımı DB kanonik değerine uyar; deterministik + LLM cube SQL'i ikisi de düzelir.
            def _is_str_lit(e):
                # Yalnız GERÇEK metin değerleri (≥3 karakter) — iç kodlar ('1','C','8')
                # COLLATE gürültüsü almasın (zaten exact eşleşir, sargability korunur).
                return (isinstance(e, exp.Literal) and e.args.get("is_string")
                        and len(str(e.name)) >= 3)

            def _collate(colexpr):
                # Latin1_General_CI_AI (Turkish_CI_AI DEĞİL): Türkçe yazım toleransı için
                # DAHA bağışlayıcı — ü=u, ö=o, ç=c, ş=s, ğ=g, İ/ı/i gevşek eşleşir. Kullanıcı
                # 'soya fasülyesi' yazar, DB 'SOYA FASULYESİ' → eşleşir. Turkish collation
                # ü/u'yu AYRI harf sayıp eşleştirmiyordu (canlı gitas 2026-07 doğrulaması).
                return exp.Collate(this=colexpr.copy(),
                                   expression=exp.column("Latin1_General_CI_AI"))

            for eqn in list(tree.find_all(exp.EQ)):
                lft, rgt = eqn.this, eqn.expression
                if _is_str_lit(rgt) and not _is_str_lit(lft) and not isinstance(lft, exp.Collate):
                    eqn.set("this", _collate(lft))
                elif _is_str_lit(lft) and not _is_str_lit(rgt) and not isinstance(rgt, exp.Collate):
                    eqn.set("expression", _collate(rgt))
            for inn in list(tree.find_all(exp.In)):
                vals = inn.args.get("expressions") or []
                if vals and all(_is_str_lit(v) for v in vals) and not isinstance(inn.this, exp.Collate):
                    inn.set("this", _collate(inn.this))
        return tree.sql(dialect=write)

    def _katalog_ozellikleri(self):
        """🔴 **Katalog/şema sorguları da motora gider — ve `motor_cls=on` iken oturum
        özelliği ZORUNLUDUR.**

        Ölçüldü (`DIMA_MOTOR_CLS=on`, 39 kırmızı): kusur test yollarında değil, tam
        burada — `_enrich_cube_dim_values` ve değer indeksi `eng.query()`'yi **özelliksiz**
        çağırıyordu ve motor planlama aşamasında `session property session_gizlilik is
        required … but not found in headers` diyerek **fail-closed** patlıyordu.

        ⚠ *Bir teşhisi ilk açıklamada bırakmak, ölçmemekle aynı sonucu verir:* bu turda
        önce *"kalan iş test/lab fixture'ları"* denmişti; traceback okunduğunda kusurun
        **ürün kodunda** olduğu görüldü. Sebep, hatanın `try/except` içinde **loglanıp
        yutulması** ve yüzeyde *"güvenilir bir sorgu üretemedim"* olarak görünmesiydi —
        yani kusur **sebebinden uzakta** konuşuyordu.

        ## 🔴 Kimlik yoksa BOŞ değil, EN KISITLI

        Traceback okunduğunda ikinci bir şey daha görüldü: katalog zenginleştirme bir
        isteğin **içinde** koşmuyor — **şema derlenirken**, yani hiç kimse sormadan önce
        koşuyor. Orada bir kullanıcı kimliği aramak bir **kategori hatasıdır**: katalog
        tenant düzeyindedir, kullanıcı düzeyinde değil.

        Kimliksizken patlamak, ürünü *"şema derlenemiyor"* diye **tamamen** durdururdu —
        motor-CLS'in koruduğundan çok daha fazlasını kaybederek. Bu yüzden
        `rls.en_kisitli_ozellikler()`: ölçeğin **kapalı ucu**, bir varsayılan değil.

        ⚠ Sonuç: katalog, **en az yetkili kullanıcının görebileceğinden fazlasını asla
        numaralandıramaz** — hassas bir kolonun değerleri bir chip önerisinde sızamaz.
        ⚠ Bir istek **içinde** çağrıldıysa (chip/drill yolu) bağlamdaki gerçek kimlik
        kullanılır; en-kısıtlı yalnız **yedektir**.
        """
        return self._oturum_ozellikleri(None) or rls.en_kisitli_ozellikler()

    def _oturum_ozellikleri(self, principal):
        """FAZ 1.2 — motor session property'leri. **`WrenEngine` SÖZLÜK ister.**

        🔴 **İKİ KATMAN, İKİ BİÇİM — ve ilk yazımımda karıştırdım.**

        * `wren_core.SessionContext(..., properties=…)` → **`frozenset`** ister; düz sözlük
          `TypeError: 'dict' object is not an instance of 'frozenset'` verir.
        * `wren.engine.WrenEngine.dry_plan/query(..., properties=…)` → **`dict`** ister ve
          dönüşümü **kendi** yapar (`_plan`: `frozenset(properties.items())`).

        Ön ölçüm probe'u `SessionContext`'i doğrudan kullandığı için `frozenset` gördüm ve
        onu **bir katman yukarıya** taşıdım → `'frozenset' object has no attribute 'items'`
        ile üç PII testi kırmızı verdi. Yani belgelediğim tuzağa **yanlış katmanda**
        düştüm; süit yakaladı. `test_motor_cls.py::test_HANGI_KATMAN_HANGI_BICIM` artık
        ikisini birden kilitliyor.

        `principal` yoksa `None` döner (boş sözlük değil): motorun *"property yok"* dalı
        ile *"boş property kümesi"* dalı aynı şey değildir.

        ## 🔴 BORÇ 1 KAPANDI — kimlik artık BAĞLAMDAN da okunuyor

        `OPERASYON-DURUM.md`: *"36 çağrı sitesi kimlik geçmiyor → `motor_cls=on`
        KİLİTLİ."* Otuz altı imzayı değiştirmek yerine kimliğin **tek sahibi** kuruldu
        (`app/istek_kimligi.py` — bu depoda üç kez kanıtlanmış ContextVar deseni).

        🔴 **İmza değiştirmek FAIL-OPEN bir düzeltme olurdu:** bugünkü 36'yı kapatır,
        yarın yazılan 37.'si `principal` geçmeyi unutur ve **hiçbir şey kırılmaz**.

        🔴 **Öncelik: AÇIK argüman bağlamı EZER.** Tersi olsaydı bir arka plan işi
        (zamanlanmış rapor) kendi kimliğini geçse bile isteği tetikleyen kullanıcının
        kimliğiyle koşardı — **çapraz-kullanıcı sızıntı**.

        ⚠ İkisi de yoksa `None` kalır ve bu **fail-safe** yöndür: motor *"property yok"*
        dalına girer, `motor_cls=on` iken **en kısıtlı** gizlilik seviyesi uygulanır.
        *Kimliği bilinmeyen bir çağrı, en az yetkili çağrıdır.*
        """
        if principal is None:
            principal = istek_kimligi.simdiki()
        return rls.oturum_ozellikleri(principal) or None

    def dry_plan(self, sql: str, *, principal=None) -> str:
        """Transpile SQL through the semantic layer without touching the DB.

        Motora giden İKİ kapıdan biri (öteki `query`); SQL politikası bu yüzden burada
        uygulanır — `guard_sql` ile aynı boğaz noktası."""
        guard_sql(sql)
        _cfg, _mod = self._sql_policy()
        if _mod == "shadow":
            self._shadow_policy_check(sql)
        # FAZ 1.1 — RLS gölgesi SQL politikasından AYRI bir kademedir (`motor_rls`);
        # ikisini tek bayrağa bağlamak, birinin ölçümünü ötekinin kararına bağlardı.
        if self._rls_kademesi() == "shadow":
            self._rls_golge_denetimi(sql)
        # 🔴 §C ölçüt 4'ün ÖN KOŞULU: `shadow` artık **ölçüyor**. Önce `cls_manifeste_yaz`
        # `shadow`'da manifesti dokunmadan döndürüyordu — yani `shadow ≡ off` idi ve
        # *"gölge modda 7 gün · sapma 0"* şartı **ölçülemezdi**.
        if self._cls_kademesi() == "shadow":
            self._cls_golge_denetimi(sql, self._oturum_ozellikleri(principal))
        with self._engine() as eng:
            return eng.dry_plan(sql, self._oturum_ozellikleri(principal))

    # Türkçe kod sayfası onarımı (Gitaş bulgusu 2026-07-24): yerli ERP DB'lerinde
    # kolon collation'ı CP1252 iken uygulama CP1254 baytları yazar; ODBC sürücüsü
    # mojibake üretir (Ð=Ğ, Ý=İ, Þ=Ş). Onarım GÜVENLİDİR: yalnız bozuk karakter
    # içeren string'lerde denenir; düzgün Türkçe metin cp1252'ye encode EDİLEMEZ
    # (Ş/Ğ/İ cp1252'de yok) → dokunulmadan kalır.
    _TR_BROKEN = frozenset("ÐÝÞðýþ")

    @classmethod
    def _fix_tr(cls, v):
        if isinstance(v, str) and any(ch in cls._TR_BROKEN for ch in v):
            try:
                return v.encode("cp1252").decode("cp1254")
            except (UnicodeEncodeError, UnicodeDecodeError):
                return v
        return v

    def query(self, sql: str, limit: int | None = None, *, principal=None) -> dict[str, Any]:
        guard_sql(sql)
        _cfg, _mod = self._sql_policy()
        if _mod == "shadow":
            self._shadow_policy_check(sql)
        # FAZ 1.1 — RLS gölgesi SQL politikasından AYRI bir kademedir (`motor_rls`);
        # ikisini tek bayrağa bağlamak, birinin ölçümünü ötekinin kararına bağlardı.
        if self._rls_kademesi() == "shadow":
            self._rls_golge_denetimi(sql)
        # 🔴 §C ölçüt 4'ün ÖN KOŞULU: `shadow` artık **ölçüyor**. Önce `cls_manifeste_yaz`
        # `shadow`'da manifesti dokunmadan döndürüyordu — yani `shadow ≡ off` idi ve
        # *"gölge modda 7 gün · sapma 0"* şartı **ölçülemezdi**.
        if self._cls_kademesi() == "shadow":
            self._cls_golge_denetimi(sql, self._oturum_ozellikleri(principal))
        with self._engine() as eng:
            table = eng.query(sql, limit=limit,
                              properties=self._oturum_ozellikleri(principal))
        rows = table.to_pylist()
        if self.datasource in ("mssql", "sqlserver"):
            rows = [{k: self._fix_tr(v) for k, v in r.items()} for r in rows]
        return {
            "columns": list(table.column_names),
            "rows": rows,
            "row_count": len(rows),
            # FAZ 1 (K1): Arrow ŞEMASI eskiden burada ATILIYORDU — yalnız kolon ADLARI
            # dönüyordu. Tipsiz bir sonuçtan ölçü/boyut/zaman ayrımı yapılamaz, yani
            # Discovery cevabından ad-hoc cube türetmenin önündeki TEK eksik buydu
            # (plan §4.1-K1). Geriye uyumlu EK alan: `QueryResult` bunu okumaz
            # (pydantic fazlalığı yok sayar), yalnız `adhoc_cube.turet()` tüketir.
            "column_types": [str(f.type) for f in table.schema],
        }
