"""Thin in-process wrapper around the Wren engine (``wren.engine.WrenEngine``).

The engine is stateless per query: we rebuild it from the compiled MDL manifest
(``target/mdl.json``) and the configured connection info on each call. This keeps
the demo simple and avoids holding DB connections open between requests.
"""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path
from typing import Any

from wren.engine import WrenEngine

# Only read-only statements are allowed through the bridge.
_ALLOWED_PREFIX = re.compile(r"^\s*(with|select)\b", re.IGNORECASE)
_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|merge|call|copy)\b",
    re.IGNORECASE,
)


class UnsafeSqlError(ValueError):
    """Raised when a statement is not a read-only SELECT."""


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

    def _manifest_b64(self) -> str:
        cached = getattr(self, "_mdl_b64_cache", None)
        raw = self._mdl_bytes()
        if cached is not None and cached[0] is raw:
            return cached[1]
        enc = base64.b64encode(raw).decode()
        self._mdl_b64_cache = (raw, enc)
        return enc

    def _engine(self) -> WrenEngine:
        return WrenEngine(self._manifest_b64(), self.datasource, dict(self.connection_info))

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
                    {"name": c.get("name"), "type": c.get("type", "")}
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
            self._enrich_categorical(models)
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
                "synonyms": _syns(c.get("synonyms")),
                "default_measure": c.get("defaultMeasure"),
                # İNSANCA görünüm (chip/not etiketleri): label > ilk ham sinonim
                "display": str(c.get("label") or (c.get("synonyms") or [c.get("name")])[0]).rstrip("!"),
                "measure_synonyms": {
                    m["name"]: _merge_syns(
                        _with_label(m.get("label"), _syns(m.get("synonyms"))),
                        _archetype_syns(m["name"]))
                    for m in c.get("measures", [])
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
                # Cube-düzeyi sabit filtre (LookML sql_always_where): her sorguya
                # otomatik eklenir. CANCELLED=0'ı ölçü ifadelerinden çıkarır — tekrar
                # ve iptal-kaydı sızıntısını yapısal önler. build camelCase'e çevirir.
                "always_filter": c.get("always_filter") or c.get("alwaysFilter"),
                "dimension_labels": {
                    d["name"]: str(d.get("label") or (d.get("synonyms") or [d["name"]])[0]).rstrip("!")
                    for d in c.get("dimensions", [])
                },
                "dimension_synonyms": {
                    d["name"]: _merge_syns(
                        _with_label(d.get("label"), _syns(d.get("synonyms"))),
                        _dim_i18n(d["name"]))  # §7b: yerel (YAML) ⊕ yardımcı-teknik dil
                    for d in c.get("dimensions", [])
                },
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
            "golden_sql": self._load_knowledge("sql"),
            "db_online": db_ok,  # UI çevrimiçi/çevrimdışı rozeti (TCP erişilebilirlik)
        }
        return self._schema_cache

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
        Hata olursa sessizce atlar."""
        col_vals = {
            c["name"]: c["values"]
            for m in models
            for c in m["columns"]
            if c.get("values")
        }
        mdl_cubes = {c.get("name"): c for c in mdl.get("cubes", [])}
        try:
            with self._engine() as eng:
                for cube in cubes:
                    vals: dict[str, list[str]] = {}
                    mc = mdl_cubes.get(cube["name"]) or {}
                    base = mc.get("baseObject")
                    for d in mc.get("dimensions", []):
                        name = d.get("name")
                        if name in col_vals:
                            vals[name] = col_vals[name]
                            continue
                        expr = d.get("expression")
                        if not base or not expr:
                            continue
                        sql = (
                            f"SELECT DISTINCT {expr} AS v FROM {base} "
                            f"WHERE ({expr}) IS NOT NULL LIMIT {self._MAX_ENUM + 1}"
                        )
                        try:
                            got = [self._fix_tr(str(r["v"])) for r in eng.query(sql).to_pylist()]
                        except Exception:
                            continue
                        if 0 < len(got) <= self._MAX_ENUM:
                            # ORDER BY'sız DISTINCT: motor satır sırasını garanti etmez
                            # (_enrich_categorical zaten sorted() kullanıyor — burada
                            # eksikti, schema() çağrıları arasında dimension_values sırası
                            # veri değişmeden de kayabiliyordu).
                            vals[name] = sorted(got)
                    cube["dimension_values"] = vals
        except Exception:
            pass

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

    def _enrich_categorical(self, models: list[dict[str, Any]]) -> None:
        """Düşük kardinaliteli VARCHAR kolonlara `values` ekler (tek engine oturumu).

        NL→SQL'in "marmara boya" / "kırmızı" gibi değerlerle WHERE yazabilmesi için.
        Hata olursa sessizce atlar (şema yine döner)."""
        try:
            with self._engine() as eng:
                for m in models:
                    for c in m["columns"]:
                        if not str(c.get("type", "")).upper().startswith("VARCHAR"):
                            continue
                        sql = (
                            f"SELECT DISTINCT {c['name']} AS v FROM {m['name']} "
                            f"WHERE {c['name']} IS NOT NULL LIMIT {self._MAX_ENUM + 1}"
                        )
                        try:
                            vals = [r["v"] for r in eng.query(sql).to_pylist()]
                        except Exception:
                            continue
                        if 0 < len(vals) <= self._MAX_ENUM:
                            c["values"] = sorted(self._fix_tr(str(v)) for v in vals)
        except Exception:
            pass

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

        base = cube_query_to_sql(json.dumps(cq), self._mdl_bytes().decode())
        base = self._inject_always_filter(base, cq.get("cube"))
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
        cubes = {c.get("name"): c for c in json.loads(self._mdl_bytes()).get("cubes", [])}
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

    def dry_plan(self, sql: str) -> str:
        """Transpile SQL through the semantic layer without touching the DB."""
        guard_sql(sql)
        with self._engine() as eng:
            return eng.dry_plan(sql)

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

    def query(self, sql: str, limit: int | None = None) -> dict[str, Any]:
        guard_sql(sql)
        with self._engine() as eng:
            table = eng.query(sql, limit=limit)
        rows = table.to_pylist()
        if self.datasource in ("mssql", "sqlserver"):
            rows = [{k: self._fix_tr(v) for k, v in r.items()} for r in rows]
        return {
            "columns": list(table.column_names),
            "rows": rows,
            "row_count": len(rows),
        }
