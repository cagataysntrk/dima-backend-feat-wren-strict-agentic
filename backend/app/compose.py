"""Paket kompozisyonu (ADR-0005 + ADR-0017): faset katmanları → wren-project.

Katman sırası (son yazan kazanır — en spesifik en son):
    packs/kaynak/<k>/  →  packs/modul/<m>/  →  packs/sektor/<s>/
      →  packs/kaynak/<k>/sektor/<s>/ (kesişim)  →  companies/<şirket>/

Kaynak pack'i (ADR-0017) fiziksel şema katmanıdır (modeller + jenerik cube'lar);
`sektor/` alt-dizini kesişim içeriğidir ve kaynak katmanı kopyalanırken atlanır —
yalnız şirketin seçtiği sektörlerle eşleşenler ayrı kesişim katmanı olarak biner.

Kaynaklar git'te yaşar; `wren-project/` DERLENMİŞ çıktıdır (gitignore). Başlangıçta
otomatik compose + `wren` build çalışır — yeni dikey = yeni YAML, kod değişikliği yok.

Kullanım: uygulama başlangıcı (main.lifespan) ya da elle:
    .venv/bin/python -m app.compose            # settings.company için
    .venv/bin/python -m app.compose <şirket>
"""

from __future__ import annotations

import json
import os
import re
import shutil
import threading
from pathlib import Path

import yaml

# ---------------------------------------------------------------------------
# EŞZAMANLILIK (2 Ağustos 2026 — panel P0 "REGISTRY COMPOSE RACE" kök nedeni)
#
# İki ayrı yarış vardı:
#
#  (1) YAZAR × YAZAR. `compose_and_build()` HİÇ kilit tutmuyordu ve üç yerden çağrılıyor:
#      `main.py` lifespan, `materialize.py`'nin 60 sn'lik scheduler thread'i ve
#      `routers/measures.py`'nin onay isteği. Scheduler thread'i ile bir istek thread'i
#      aynı dizine girdiğinde birinin rmtree'si diğerinin kopyaladığı dosyaları siliyor
#      → sessizce eksik proje (türev view/KPI yok). `CompanyRegistry`'nin per-slug kilidi
#      vardı ama `compose_and_build` ondan geçmiyordu; compose.py:75-76'daki
#      "registry per-slug kilidi eş-zamanlı yazımı zaten engeller" yorumu bu yüzden
#      VARSAYILAN şirket için YANLIŞTI.
#
#  (2) YAZAR × OKUYUCU (daha geniş pencere). `WrenService` `target/mdl.json`'ı HER
#      motor kurulumunda ve HER cube derlemesinde yeniden okur. Eski akışta dosya, tüm
#      compose+build boyunca (~130-160 ms) HİÇ YOKTU (rmtree siliyor, save_target en
#      sonda geri yazıyor). O pencerede gelen bir /ask ya `FileNotFoundError` alıyordu ya
#      da — daha kötüsü — `_inject_always_filter`'ın okuma hatasını yutup **always_filter'ı
#      sessizce düşürmesine** yol açıyordu (iptal kayıtları toplama sızar).
#
# Çözüm iki parçalı ve birbirini tamamlar: aşağıdaki paylaşılan kilit (1) için,
# `compose()`'un `target/`'ı KORUMASI + `build()`'in `os.replace` ile ATOMİK yazması
# (2) için. İkincisi tek başına bile okuyucu yarışını kapatır: okuyucu her an ya ESKİ ya
# YENİ manifesti görür, asla yok/yarım görmez.
# ---------------------------------------------------------------------------

_LOCKS_GUARD = threading.Lock()
_BUILD_LOCKS: dict[str, threading.Lock] = {}


def build_lock_for(out: Path) -> threading.Lock:
    """Bir derleme çıktısı dizini için süreç-genelinde TEK kilit.

    `CompanyRegistry` ve `compose_and_build()` AYNI kilidi kullanmalı — aksi halde
    varsayılan şirket (demo/wren-project) ile registry tenant'ları (demo/wren-projects/
    <slug>) farklı kilitler üzerinden aynı ağaca yazabilir.
    """
    key = str(Path(out).resolve())
    with _LOCKS_GUARD:
        lock = _BUILD_LOCKS.get(key)
        if lock is None:
            lock = _BUILD_LOCKS[key] = threading.Lock()
        return lock


def compose(company: str, base: Path, out: Path) -> dict:
    """Katmanları out'a kopyalar. Döner: {layers: [...], files: N}.

    Sektör alanı iki biçimde gelebilir: ``sektor: x`` (tekil, geriye-uyum) ya da
    ``sektorler: [x, y]`` (çoklu — LİSTEDE ÖNCE gelen kazanır; aynı adlı cube
    çakışmasında ilk sıradaki sektörün içeriği geçerli olur)."""
    base = Path(base)
    out = Path(out)
    company_dir = base / "companies" / company
    cfg = yaml.safe_load((company_dir / "company.yml").read_text()) or {}
    sektorler = cfg.get("sektorler") or ([cfg["sektor"]] if cfg.get("sektor") else [])
    sektor_dirs = [base / "packs" / "sektor" / str(s) for s in sektorler]

    moduller = cfg.get("moduller")
    if moduller is None:
        # Varsayılan modüller: tüm seçili sektör paketlerinin birleşimi (sıra korunur).
        seen: list[str] = []
        for d in sektor_dirs:
            pack_cfg = yaml.safe_load((d / "pack.yml").read_text()) or {}
            for m in pack_cfg.get("moduller") or []:
                if m not in seen:
                    seen.append(m)
        moduller = seen
    moduller = moduller or []

    kaynaklar = [str(k) for k in cfg.get("kaynaklar") or []]
    kaynak_dirs = [base / "packs" / "kaynak" / k for k in kaynaklar]

    # Kopyalama sırası = öncelik sırası (SON yazan kazanır): kaynak → modüller →
    # sektörler → kesişim → şirket. Listelerde önce gelen EN SON kopyalanır ki kazansın.
    # (layer, exclude) çifti: kaynak katmanının sektor/ alt-dizini kesişim içeriğidir,
    # ana kopyada atlanır.
    layers: list[tuple[Path, str | None]] = [(d, "sektor") for d in reversed(kaynak_dirs)]
    layers.extend((base / "packs" / "modul" / m, None) for m in moduller)
    layers.extend((d, None) for d in reversed(sektor_dirs))
    for layer, _ in layers + [(company_dir, None)]:
        if not layer.is_dir():
            raise FileNotFoundError(f"Kompozisyon katmanı yok: {layer}")
    # Kesişim katmanları (ADR-0017): yalnız var olan kaynak×sektör çiftleri biner —
    # matris seyrektir, eksik kesişim hata değildir.
    for k in reversed(kaynak_dirs):
        for s in [d.name for d in reversed(sektor_dirs)]:
            kesisim = k / "sektor" / s
            if kesisim.is_dir():
                layers.append((kesisim, None))
    layers.append((company_dir, None))

    # Çıktıyı sıfırla (derlenmiş artefakt — kaynak değil). rmtree macOS'ta geçici olarak
    # "Directory not empty" verebiliyor (FS gecikmesi/izleyici) — birkaç kez dene, sonra
    # son çare ignore_errors. Eşzamanlı yazımı `build_lock_for(out)` engeller (bkz. modül
    # başı: eskiden bu satırda "registry kilidi zaten engeller" yazıyordu ama varsayılan
    # şirket registry'den GEÇMİYORDU).
    #
    # `target/` KORUNUR (2 Ağustos 2026): içindeki `mdl.json` yeni build bitene kadar
    # okuyucular için GEÇERLİ kalır. Eskiden rmtree onu da siliyordu ve tüm compose+build
    # boyunca manifest YOKTU — o pencerede gelen sorgu ya patlıyor ya da always_filter'ı
    # sessizce kaybediyordu. `target/` bir GİRDİ değildir (`build_json` yalnız models/
    # views/cubes/relationships okur), dolayısıyla korunması bayat içerik sızdırmaz;
    # `build()` sonunda `os.replace` ile atomik olarak değiştirilir.
    if out.exists():
        import time as _t

        for child in sorted(out.iterdir()):
            if child.name == "target":
                continue
            for _ in range(3):
                try:
                    shutil.rmtree(child) if child.is_dir() else child.unlink()
                    break
                except OSError:
                    _t.sleep(0.1)
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)

    skip = {"company.yml", "pack.yml", "schedules.yaml", "gereksinim.yml",
            "cube_synonyms.yml", "turev.yml"}
    count = 0
    for layer, exclude in layers:
        for f in sorted(layer.rglob("*")):
            if not f.is_file() or f.name in skip:
                continue
            rel = f.relative_to(layer)
            if rel.parts[0] == "verified":
                continue  # öğrenilen VQR verisi şirkette KALIR (çalışma verisi, içerik değil)
            if exclude is not None and rel.parts[0] == exclude:
                continue
            dst = out / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dst)
            count += 1
    # SEKTÖR-SİNONİM ENJEKSİYONU (ADR-0017 faset disiplini): sektör/kesişim pack'i
    # generic KAYNAK cube'una terminoloji EKLER (kumaş→mal, hurda→ticaret) — kaynak
    # cube sektörden bağımsız kalır (pack-lint zorlar), sektör kelimesi burada birleşir.
    # additive: base sinonimi silmez. Katman sırasıyla uygulanır (şirket en son).
    _merge_cube_synonyms(layers, out)
    # JENERİK TÜREV METRİKLER: DB-bağımsız kâr/marj/SMM/... tanımlarını (packs/modul/turev/)
    # her ERP'nin turev.yml binding'lerinden view+cube olarak ÜRETİR (logo/mikro/netsis
    # bedavaya; yeni ERP sadece binding verir).
    _compose_derived_metrics(base, out, kaynaklar)
    # İLİŞKİ-TÜREVİ BOYUTLAR (Faz 1.1): `relationships.yml`'deki `expose:` bloklarından
    # handle + calc kolon + cube boyutu üretir. `_compose_derived_metrics`'ten SONRA
    # çalışır ki o pass'in ürettiği cube'lar da kapsansın.
    _compose_relationship_dimensions(out)
    # KPI-KOMPOZİSYON: cross-cube türev KPI'lar (packs/modul/kpi/*.yml). Bileşenleri
    # birden çok türev-view'dan çeker (CCC = cari_finans_src ⊕ karlilik_src). Yalnız
    # gerekli view'ların TAMAMI üretildiyse derlenir (dürüst gate — eksikse KPI yok).
    _compose_kpis(base, out)
    return {"layers": [str(l.relative_to(base)) for l, _ in layers], "files": count}


def _compose_kpis(base: Path, out: Path) -> None:
    """Cross-cube KPI tanımlarını (packs/modul/kpi/*.yml) out/kpis/ altına yalnız tüm
    requires_views üretilmişse kopyalar. KPI DB-bağımsızdır (kanonik view kolonları);
    bileşen SQL'i ERP-özel değildir → hiçbir binding gerekmez, view varsa çalışır."""
    kpi_dir = base / "packs" / "modul" / "kpi"
    if not kpi_dir.is_dir():
        return
    for kfile in sorted(kpi_dir.glob("*.yml")):
        spec = yaml.safe_load(kfile.read_text()) or {}
        need = spec.get("requires_views") or []
        if not all((out / "views" / v / "metadata.yml").is_file() for v in need):
            continue  # bu şirkette gerekli türev-view(lar) yok → KPI atlanır (dürüst)
        dst = out / "kpis" / f"{spec['name']}.yml"
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(yaml.safe_dump(spec, allow_unicode=True, sort_keys=False))


def _compose_derived_metrics(base: Path, out: Path, kaynaklar: list[str]) -> None:
    """Jenerik türev-metrikleri (packs/modul/turev/*.yml) her ERP'nin turev.yml
    binding'lerinden view+cube üretir. Metrik DB-bağımsız (kanonik kolonlar); binding
    ERP-özel (fiziksel kolon/kod eşlemesi). İlk sağlayan kaynak kazanır (tekil ERP varsayımı)."""
    metric_dir = base / "packs" / "modul" / "turev"
    if not metric_dir.is_dir():
        return
    bindings_by_kaynak: dict[str, dict] = {}
    for k in kaynaklar:
        bpath = base / "packs" / "kaynak" / k / "turev.yml"
        if bpath.is_file():
            bindings_by_kaynak[k] = yaml.safe_load(bpath.read_text()) or {}
    for mfile in sorted(metric_dir.glob("*.yml")):
        spec = yaml.safe_load(mfile.read_text()) or {}
        name, req = spec.get("name"), (spec.get("requires") or [])
        binding = None
        for k in kaynaklar:  # metriği TAM bağlayan ilk kaynak
            b = (bindings_by_kaynak.get(k) or {}).get(name)
            if b and all(r in b for r in req):
                binding = b
                break
        if binding is None:
            continue  # bu şirketin ERP'si metriği bağlamıyor → metrik atlanır (dürüst)
        # Opsiyonel placeholder default'ları (binding'de yoksa): row_filter = iptal/geçerlilik
        # yüklemi (netsis/mikro: yok → "1=1"; logo: "CANCELLED = 0").
        render = {"row_filter": "1=1", **binding}
        vname = spec["view_name"]
        vdir = out / "views" / vname
        vdir.mkdir(parents=True, exist_ok=True)
        (vdir / "metadata.yml").write_text(yaml.safe_dump(
            {"name": vname, "statement": spec["view_statement"].format(**render),
             "columns": spec["view_columns"]}, allow_unicode=True, sort_keys=False))
        cube = spec["cube"]
        cdir = out / "cubes" / cube["name"]
        cdir.mkdir(parents=True, exist_ok=True)
        (cdir / "metadata.yml").write_text(
            yaml.safe_dump(cube, allow_unicode=True, sort_keys=False))


_COND_RE = re.compile(r"^\s*(\w+)\.\"?(\w+)\"?\s*=\s*(\w+)\.\"?(\w+)\"?\s*$")


class RelationshipExposeError(ValueError):
    """`expose:` bildirimi güvenlik kapılarından geçemedi — build KIRILIR.

    Bilinçli olarak sessiz atlama DEĞİL: yanlış bir join, hatasız ve uyarısız şişmiş bir
    sayı üretir ve `source="cube"` rozetiyle sunulur. Derlemenin patlaması, üretimde
    yanlış sayı görmekten iyidir.
    """


def _hop_derinligi(hedef_kolon: dict) -> int:
    """Üretilen boyutun kaç JOIN uzağında olduğu (G7).

    1 = hedef modelin FİZİKSEL kolonu (tek join).
    2 = hedef modelin kendi `is_calculated` kolonu → o kolon başka bir modele bakar,
        yani zincir iki join uzunluğundadır (`bordro → personel → personel_ozluk`).

    Üreteç graf GEZMEZ: 2. sıçrama ancak hedef modelde ZATEN elle tanımlanmış bir calc
    kolonu üzerinden kurulabilir. Bu, MetricFlow'un "3 tablo / 2 sıçrama" sınırının yapısal
    karşılığıdır — 3. sıçrama için o ara modelin de calc kolonu olması gerekirdi ve
    `_hop_sinirini_dogrula` onu reddeder.
    """
    return 2 if hedef_kolon.get("is_calculated") or hedef_kolon.get("isCalculated") else 1


def _etiket_carpismasi(e: dict, rname: str, src: str, cube_files: list, _load,
                       kendi_adi: str) -> None:
    """G5b — ÜRETİLEN BOYUTUN ETİKETİ mevcut bir boyutun sözlüğünü ÇALIYOR mu?

    `WrenService.schema()::_with_label` (ADR-0018 "LABEL ⊆ SYNONYM") bir etiketi hem TAM
    haliyle hem de KELİMELERİNE AYIRARAK sinonim listesine ekler. Yani `label: makine bölümü`
    sessizce `makine` sinonimini de doğurur — ve o cube'da zaten bir `makine` boyutu varsa
    "makine bazında su yoğunluğu" sorusu ARTIK İKİ boyut eşleştirir, GROUP BY bölünür ve
    her hücredeki sayı değişir.

    Bu tam olarak yaşandı (2 Ağustos 2026): `partiler_makineler` için `label: makine bölümü`
    verildi, `test_surdurulebilirlik_cube` anında düştü (`['makine'] != ['makine','makine_bolum']`).
    Faz 0.5'in tahkimi bunu KURTARAMAZ: iki eşleşme de tam kelime `makine`'dir, yani öz
    alt-dizi ilişkisi yoktur — GERÇEK bir belirsizliktir.

    Kural: etiketin ürettiği tek-kelime token'lar hedef cube'ların MEVCUT boyut adlarıyla ya
    da sözlükleriyle çakışamaz. Çok kelimeli SİNONİMLER güvenlidir (bölünmezler); yalnız
    ETİKET bölünür. Pratik sonuç: üretilen boyutun etiketi TEK KELİME olmalı ya da
    kelimeleri hedef cube'da serbest olmalı.
    """
    label = str(e.get("label") or "").strip()
    if not label:
        return
    tr = str.maketrans("ışğüöçİâîû", "isguociaiu", "'’`")
    tokens = {t for t in label.lower().replace("̇", "").translate(tr).split() if len(t) >= 3}
    if not tokens:
        return
    for cf in cube_files:
        cm = _load(cf)
        if cm.get("base_object") != src:
            continue
        for d in cm.get("dimensions") or []:
            ad = str(d.get("name", "")).lower()
            if ad == kendi_adi.lower():
                # ÜRETECİN KENDİ ÇIKTISI — bir boyut kendisiyle çakışamaz. Bu, terfi
                # akışı yüzünden gerçekten oluyor: `mdl_writer.resolve_cube_yaml_for_edit`
                # DERLENMİŞ cube'u (üretilmiş boyutlar dahil) şirket katmanına kopyalar,
                # sonraki compose onu kaynak sanır. Üreteç zaten yinelenen boyutu
                # eklemiyor (elle/önceki tanım kazanır); kapı da aynı şekilde atlamalı.
                continue
            sozluk = {ad, *(str(s).lower().replace("̇", "").translate(tr).rstrip("!")
                            for s in (d.get("synonyms") or []))}
            if str(d.get("label") or "").lower().translate(tr):
                sozluk.add(str(d["label"]).lower().replace("̇", "").translate(tr))
            carpisan = tokens & sozluk
            if carpisan:
                raise RelationshipExposeError(
                    f"{rname}: `label: {label!r}` kelimelerine ayrılınca {sorted(carpisan)} "
                    f"üretiyor ve bu, `{cm.get('name')}` cube'undaki `{d.get('name')}` "
                    "boyutunun sözlüğüyle ÇAKIŞIYOR (ADR-0018 LABEL ⊆ SYNONYM). Aynı soru iki "
                    "boyut eşleştirir, GROUP BY bölünür ve sayılar değişir. TEK KELİMELİK ya da "
                    "çakışmayan bir `label` verin; çok kelimeli ifadeleri `synonyms:` altına "
                    "koyun (onlar BÖLÜNMEZ, dolayısıyla güvenlidir).")


def _compose_relationship_dimensions(out: Path) -> None:
    """İLİŞKİ-TÜREVİ BOYUT ÜRETECİ (Faz 1.1) — `relationships.yml`'deki `expose:` blokları.

    Bir cube yalnız TEK bir `base_object`'e bağlanır ve cube derleyicisi JOIN üretmez.
    Ama MODEL KATMANI (`WrenEngine.dry_plan`) ilişki handle'ı + `is_calculated` kolon
    üzerinden JOIN'i otomatik ve çok-sıçramalı enjekte eder (bkz. backend/MIMARI.md §3.2,
    Faz 1.0 pilotuyla 26 noktada birebir doğrulandı). Bu üreteç o mekanizmayı ELLE YAZILMIŞ
    view'lardan alıp bildirime dayalı hale getirir.

    Tek bir `expose:` girdisinden ÜÇ artefakt üretilir:
        1. kaynak modele  → ilişki handle kolonu   {name: <hedef>, type: <hedef>, relationship}
        2. kaynak modele  → is_calculated kolon    {expression: "<hedef>.<kolon>"}
        3. base_object'i o model olan HER cube'a → boyut (+ provenance)

    Kaldıraç (3) maddesindedir: bir bildirim, o modele oturan tüm cube'lara yayılır.

    NEDEN AÇIK BİLDİRİM, otomatik tarama DEĞİL — ölçülmüş gerekçe: üretilen boyutlar
    Türkçe `label`/`synonyms` olmadan `cube_router`'a GÖRÜNMEZ. Mekanik kolon adlarıyla
    router bir ERP şemasında 6 sorudan 1'ini, elle yazılmış etiketlerle 5'ini eşleştirdi.
    Sözlük kürasyonu işin indirgenemez insan kısmıdır; `expose:` onu görünür ve
    gözden geçirilebilir kılar.

    Biçim (`relationships.yml`):
        - name: oee_vardiya_makineler
          join_type: MANY_TO_ONE
          models: [oee_vardiya, makineler]
          condition: "oee_vardiya.makine = makineler.makine"
          expose:
            - column: bolum          # HEDEF modeldeki kolon (fiziksel ya da calc → 2. sıçrama)
              as: bolum              # cube boyut adı (varsayılan: <hedef>_<kolon>)
              label: bölüm
              synonyms: [bölüm, birim, kısım]
    """
    rel_file = out / "relationships.yml"
    if not rel_file.is_file():
        return
    rels = (yaml.safe_load(rel_file.read_text(encoding="utf-8")) or {}).get("relationships") or []
    if not any(r.get("expose") for r in rels):
        return

    models_dir, cubes_dir = out / "models", out / "cubes"

    def _load(p: Path) -> dict:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}

    def _save(p: Path, data: dict) -> None:
        p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                     encoding="utf-8")

    model_files = {d.name: d / "metadata.yml" for d in models_dir.iterdir()
                   if (d / "metadata.yml").is_file()} if models_dir.is_dir() else {}
    cube_files = [d / "metadata.yml" for d in cubes_dir.iterdir()
                  if (d / "metadata.yml").is_file()] if cubes_dir.is_dir() else []

    for rel in rels:
        expose = rel.get("expose")
        if not expose:
            continue
        rname = rel.get("name") or "(adsız)"

        # --- G6: condition ayrıştırılabilmeli (bileşik/karmaşık join DESTEKLENMEZ) -----
        # `db_introspect.py` bileşik FK'yi İLK KOLONA KIRPIYOR; öyle bir join semantik
        # olarak yanlıştır ve tekil olmayan bir anahtar üretir. Sessizce üretmektense reddet.
        m = _COND_RE.match(str(rel.get("condition") or ""))
        if not m:
            raise RelationshipExposeError(
                f"{rname}: `condition` tek-kolonlu eşitlik değil ({rel.get('condition')!r}). "
                "Bileşik anahtarlı ilişkiler `expose:` ile üretilemez — elle bir view yazın.")
        la, lc, ra, rc = m.groups()

        # --- G4: kendine-referanslı ilişki → Rust çekirdeği PANIC atıyor ---------------
        # `core/src/mdl/lineage.rs:146` `unwrap()` on None. `PanicException` `Exception`
        # DEĞİLDİR (MRO: PanicException → BaseException), yani `except Exception` onu
        # YAKALAMAZ ve worker düşer. Hesap planı parent / BOM / org şeması ERP'lerde standart.
        if la == ra:
            raise RelationshipExposeError(
                f"{rname}: kendine-referanslı ilişki ({la}) — motor çekirdeği PANIC atıyor "
                "(lineage.rs), `except Exception` yakalamaz. `expose:` desteklenmiyor.")

        # --- G1+G2: YÖN, `join_type`'tan DEĞİL, ŞEMADAN türetilir ---------------------
        # Motor `join_type`'ı OKUMUYOR (ölçüldü: MANY_TO_ONE / ONE_TO_MANY / MANY_TO_MANY
        # AYNI SQL'i üretir), dolayısıyla o alan bir YORUMDUR. Tek yapısal sinyal: "bir"
        # tarafının join kolonu o modelin PRIMARY KEY'i olmalı. Bu, Snowflake'in
        # `REFERENCES <PK/UNIQUE>` kuralının ve Apache Ossie'nin ilişki modelinin aynısıdır.
        # Yalnız MANY→ONE üretilir; ters yön handle'ı YASAKTIR (join pruning yüzünden bir
        # ölçünün değeri SELECT'teki DİĞER ölçülere göre değişir — ölçüldü: 3 → 7.038).
        def _pk(model_name: str) -> str | None:
            f = model_files.get(model_name)
            return _load(f).get("primary_key") if f else None

        if _pk(ra) == rc:
            src, src_col, dst, dst_col = la, lc, ra, rc
        elif _pk(la) == lc:
            src, src_col, dst, dst_col = ra, rc, la, lc
        else:
            raise RelationshipExposeError(
                f"{rname}: hiçbir tarafın join kolonu o modelin `primary_key`'i değil "
                f"({la}.{lc} / {ra}.{rc}). Benzersizlik YAPISAL olarak kanıtlanamıyor → "
                "üretim reddedildi. Ya modelin primary_key'ini doğru bildirin ya da "
                "`models_enrich.yml` ile ELLE, bilinçli bir istisna olarak tanımlayın "
                "(veri düzeyi doğrulama: tests/test_relationship_health.py).")

        src_file = model_files.get(src)
        if src_file is None:
            raise RelationshipExposeError(f"{rname}: kaynak model {src!r} bulunamadı")
        dst_file = model_files.get(dst)
        if dst_file is None:
            raise RelationshipExposeError(f"{rname}: hedef model {dst!r} bulunamadı")

        # --- G10: FİLTRELİ bir modele join'lemek `always_filter`'ı BAYPAS EDER ----------
        # `always_filter` (LookML `sql_always_where`) bir CUBE özelliğidir ve
        # `WrenService._inject_always_filter` onu YALNIZ o cube'un kendi SQL'ine ekler.
        # Bir başka cube o modele JOIN'lediğinde filtre UYGULANMAZ — join model katmanının
        # ALTINDA gerçekleşir. Ölçüldü (2 Ağustos 2026): `ticaret.always_filter =
        # "tur='satis'"` iken `fatura_satirlari` üzerinden `faturalar`'a join edilince
        # 34 milyon TL'lik `alis` verisi filtreyi GEÇTİ.
        #
        # Bu, Discovery'de bilinen bir baypastı; otomatik join onu "handle üretilen HER
        # cube"a yayar. Sessizce yaymaktansa üretimi reddet: doğru çözüm ya filtreyi model
        # katmanına taşımak ya da o ilişkiyi elle, bilinçli olarak tanımlamaktır.
        filtreli = [
            cm.get("name") for cf in cube_files
            if (cm := _load(cf)).get("base_object") == dst
            and (cm.get("always_filter") or cm.get("alwaysFilter"))
        ]
        if filtreli:
            raise RelationshipExposeError(
                f"{rname}: hedef model {dst!r} `always_filter` taşıyan cube'ların "
                f"({', '.join(map(str, filtreli))}) tabanı. Join model katmanının ALTINDA "
                "gerçekleştiği için o filtre UYGULANMAZ ve satırlar sessizce sızar "
                "(ölçüldü: 34M TL'lik alış verisi `tur='satis'` filtresini geçti). "
                "Üretim reddedildi — filtreyi model katmanına taşıyın ya da ilişkiyi elle "
                "tanımlayıp sızıntıyı bilinçli olarak kabul edin.")

        src_meta, dst_meta = _load(src_file), _load(dst_file)
        src_cols = src_meta.setdefault("columns", [])
        dst_cols = {c["name"]: c for c in (dst_meta.get("columns") or [])}

        # --- G5: ad çakışması BÜYÜK/KÜÇÜK HARF DUYARSIZ -------------------------------
        # `MAKINE` ile `makine` yan yana durursa motor TÜM modeli geçersiz kılar
        # (`[INVALID_MDL] columns that differ only in case`) ve bu SORGU ANINDA patlar,
        # build'de değil. Logo (`LOGICALREF`) / Netsis (`CARI_KOD`) gibi BÜYÜK harfli ERP
        # şemalarında kaçınılmaz. Ölçü adlarıyla çakışma da ayrıca ölümcül
        # (`circular dependency detected in measure expressions`).
        used = {str(c.get("name", "")).lower() for c in src_cols}
        for cf in cube_files:
            cm = _load(cf)
            if cm.get("base_object") == src:
                used |= {str(x.get("name", "")).lower() for x in (cm.get("measures") or [])}

        # handle kolonu: adı HEDEF MODEL ADINA EŞİT olmak ZORUNDA (motor kısıtı). Bu yüzden
        # (kaynak, hedef) çifti başına EN FAZLA BİR ilişki ifade edilebilir — rol-oynayan
        # boyutlar (fatura-adresi/sevk-adresi) yapısal olarak imkânsızdır, bkz. MIMARI §9.2.
        if dst.lower() not in used:
            src_cols.append({"name": dst, "type": dst, "relationship": rname})
            used.add(dst.lower())
        elif not any(c.get("name") == dst and c.get("relationship") for c in src_cols):
            raise RelationshipExposeError(
                f"{rname}: handle adı {dst!r} {src} üzerinde FİZİKSEL bir kolonla çakışıyor. "
                "Motor handle adının hedef model adına eşit olmasını şart koşar → bu ilişki "
                "`expose:` ile üretilemez.")

        yeni_boyutlar = []
        for e in expose:
            col = e.get("column")
            if not col:
                raise RelationshipExposeError(f"{rname}: `expose` girdisinde `column` yok")
            if col not in dst_cols:
                raise RelationshipExposeError(
                    f"{rname}: {dst}.{col} yok. (2. sıçrama için hedef modelde ZATEN tanımlı "
                    "bir calc kolonu gösterin — üreteç graf gezmez, hop sınırı 2'dir.)")
            # --- G7: SIÇRAMA SINIRI = 2 (MetricFlow emsali: "3 tablo / 2 sıçrama") -------
            # Hedefteki kolon bir calc ise zincir 2 sıçramadır (`bordro → personel →
            # personel_ozluk`). O calc'ın BAKTIĞI kolon da calc ise 3 olurdu. Cube'un kendi
            # dokümanı "çoklu yol öngörülebilirliği düşürür" diyor; burada sınır SESSİZCE
            # aşılmasın diye build kırılır. Ölçülmüş bir vaka değil — yapısal bir kilit:
            # üçüncü sıçrama eklendiğinde bunu fark etmeden yapmak mümkün olmasın.
            if _hop_derinligi(dst_cols[col]) == 2:
                ifade = str(dst_cols[col].get("expression") or "")
                ara_model, _, ara_kolon = ifade.partition(".")
                ara_file = model_files.get(ara_model)
                ara_kolonlar = ({c["name"]: c for c in (_load(ara_file).get("columns") or [])}
                                if ara_file else {})
                if _hop_derinligi(ara_kolonlar.get(ara_kolon) or {}) == 2:
                    raise RelationshipExposeError(
                        f"{rname}: {dst}.{col} → {ifade} zinciri 3 SIÇRAMA uzunluğunda. "
                        "Sınır 2'dir (MetricFlow emsali: 3 tablo / 2 sıçrama). Ara modelde "
                        "doğrudan bir kolon tanımlayıp onu gösterin.")
            calc_ad = e.get("calc_name") or f"{dst}_{col}"
            if calc_ad.lower() in used:
                raise RelationshipExposeError(
                    f"{rname}: üretilen kolon adı {calc_ad!r} {src} üzerinde zaten var "
                    "(büyük/küçük harf duyarsız) — `calc_name:` ile farklı bir ad verin.")
            src_cols.append({"name": calc_ad, "type": e.get("type") or dst_cols[col].get("type")
                             or "VARCHAR", "is_calculated": True,
                             "expression": f"{dst}.{col}"})
            used.add(calc_ad.lower())
            # `dimension: false` → YALNIZ calc kolonu üret, cube boyutu ÜRETME.
            # Gerekçe: bazen kolon bir İFADENİN İÇİNDE kullanılır, kendi başına bir
            # kırılım ekseni olarak değil. İki gerçek vaka (Faz 2.1):
            #   * mizan `tarih`: bir ZAMAN boyutudur; üreteç `time_dimensions`'a ekleme
            #     yapmaz, bağ elle kurulur. Ayrıca normal boyut olarak yayımlanırsa aynı
            #     kolon iki kez görünür ve router yüzeyi gereksiz büyür.
            #   * mizan `hesap_adi`: cube onu COALESCE ile sarmalar (boş ad → hesap kodu).
            if e.get("dimension") is False:
                continue
            _etiket_carpismasi(e, rname, src, cube_files, _load,
                               e.get("as") or calc_ad)
            yeni_boyutlar.append({
                "name": e.get("as") or calc_ad,
                "expression": calc_ad,
                "type": e.get("type") or dst_cols[col].get("type") or "VARCHAR",
                **({"label": e["label"]} if e.get("label") else {}),
                **({"synonyms": list(e["synonyms"])} if e.get("synonyms") else {}),
                # PROVENANCE: hangi join'den, kaç sıçrama sonra geldi. `properties` MDL'de
                # birinci sınıf; wren-core bilinmeyen anahtarları yok sayar → motor değişmez.
                #
                # `hops` ÖLÇÜLÜR, varsayılmaz (2 Ağustos 2026 düzeltmesi — eskiden sabit 1
                # yazılıyordu): hedefteki kolonun KENDİSİ bir calc kolonuysa zincir bir
                # sıçrama daha uzundur (`bordro → personel → personel_ozluk`). Sabit 1,
                # yayımlanmış bir 2-sıçramalı boyutu YAKINMIŞ gibi gösterirdi ve
                # sıçrama-derinliğini okuyan her tüketici (chip sıralaması, Query Contract,
                # ileride router tercihi) yanlış bilgiyle çalışırdı.
                "properties": {"origin": {"model": dst, "column": col,
                                          "relationship": rname,
                                          "hops": _hop_derinligi(dst_cols[col])}},
            })

        _save(src_file, src_meta)

        # base_object'i bu model olan HER cube'a boyutları ekle (asıl kaldıraç).
        for cf in cube_files:
            cm = _load(cf)
            if cm.get("base_object") != src:
                continue
            dims = cm.setdefault("dimensions", [])
            mevcut = {str(d.get("name", "")).lower() for d in dims}
            eklendi = False
            for d in yeni_boyutlar:
                if d["name"].lower() in mevcut:
                    continue  # cube kendi boyutunu ZATEN tanımlamış → elle tanım kazanır
                dims.append(dict(d))
                eklendi = True
            if eklendi:
                _save(cf, cm)


def _merge_cube_synonyms(layers: list[tuple[Path, str | None]], out: Path) -> None:
    """Her katmandaki cube_synonyms.yml'i derlenmiş cube metadata'sına additive işler.

    Biçim (cube adı → ekler):
        mal:
          synonyms: [kumaş, metre, top]       # cube-düzeyi
          measures: {satis_miktari: [kaç metre]}
          dimensions: {stok_kodu: [hangi kumaş]}
    """
    def _add(dst_list_owner: dict, key: str, extra: list) -> None:
        cur = dst_list_owner.get(key) or []
        for s in extra:
            if s not in cur:
                cur.append(s)
        dst_list_owner[key] = cur

    for layer, _ in layers:
        spec_path = layer / "cube_synonyms.yml"
        if not spec_path.is_file():
            continue
        spec = yaml.safe_load(spec_path.read_text()) or {}
        for cube_name, adds in spec.items():
            meta_path = out / "cubes" / cube_name / "metadata.yml"
            if not meta_path.is_file():
                continue  # bu şirkette o cube yok → atla (seyrek matris)
            meta = yaml.safe_load(meta_path.read_text()) or {}
            if adds.get("synonyms"):
                _add(meta, "synonyms", adds["synonyms"])
            for mname, syns in (adds.get("measures") or {}).items():
                for m in meta.get("measures", []):
                    if m.get("name") == mname:
                        _add(m, "synonyms", syns)
            for dname, syns in (adds.get("dimensions") or {}).items():
                for d in meta.get("dimensions", []):
                    if d.get("name") == dname:
                        _add(d, "synonyms", syns)
            meta_path.write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False))


def build(project_dir: Path) -> Path:
    """Derlenmiş projeden target/mdl.json üretir (wren build, in-process) — ATOMİK.

    Upstream `wren.context.save_target()` düz `out.write_text(...)` yapar; bu, yazım
    sürerken okuyan bir thread'e YARIM JSON gösterebilir. `WrenService` manifesti her
    motor kurulumunda ve her cube derlemesinde yeniden okuduğu için bu pencere gerçekti.
    Burada aynı işi geçici dosya + `os.replace` ile yapıyoruz: POSIX'te rename atomiktir,
    dolayısıyla okuyucu ya ESKİ ya YENİ manifesti görür — asla yarım.

    (Upstream forklanmıyor: `build_json` aynen kullanılır, yalnız YAZMA adımı bizim.)
    """
    from wren.context import build_json

    project_dir = Path(project_dir)
    manifest = build_json(project_dir)
    target_dir = project_dir / "target"
    target_dir.mkdir(parents=True, exist_ok=True)
    out = target_dir / "mdl.json"
    # PID'li geçici ad: aynı dizine yazan iki süreç birbirinin tmp'ini ezmesin.
    tmp = target_dir / f".mdl.json.tmp.{os.getpid()}"
    try:
        tmp.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, out)  # atomik (aynı dosya sistemi)
    finally:
        if tmp.exists():
            tmp.unlink(missing_ok=True)
    return out


def compose_and_build(settings) -> dict:
    base = Path(settings.demo_root) if getattr(settings, "demo_root", "") else None
    if base is None or not str(base):
        base = settings.resolved_project_dir().parent  # .../demo
    out = settings.resolved_project_dir()
    # Paylaşılan per-dizin kilidi (bkz. modül başı): scheduler thread'i ile istek thread'i
    # aynı ağaca AYNI ANDA giremesin. Registry de AYNI kilidi kullanır.
    with build_lock_for(out):
        info = compose(settings.company, base, out)
        build(out)
    return info


if __name__ == "__main__":
    import sys

    from app.config import get_settings

    s = get_settings()
    if len(sys.argv) > 1:
        object.__setattr__(s, "company", sys.argv[1])
    info = compose_and_build(s)
    print(f"compose: {' ⊕ '.join(info['layers'])} → {s.resolved_project_dir()} ({info['files']} dosya) + mdl.json")
