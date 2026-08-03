"""Control-plane database engine + session (SQLModel).

Postgres (prod) veya SQLite (lokal/demo). Migration sahibi admin-api'dir (ADR-0015
Karar 3); ``create_all`` yalnız SQLite/lokal kolaylığı içindir, Postgres'te Alembic
kullanılır.
"""

from __future__ import annotations

from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

from control_plane.config import get_auth_settings

_settings = get_auth_settings()
_db_url = _settings.effective_database_url()
_is_sqlite = _db_url.startswith("sqlite")

engine = create_engine(
    _db_url,
    echo=False,
    connect_args={"check_same_thread": False} if _is_sqlite else {},
    pool_pre_ping=not _is_sqlite,
)


def init_db() -> None:
    """Lokal/SQLite kolaylığı: tabloları oluştur + EKSİK KOLONLARI ekle.

    Postgres'te Alembic devralır (ADR-0015 Karar 3) — orada bu fonksiyon hiçbir şey yapmaz.
    """
    if _is_sqlite:
        # logs/ klasörü zaten var; SQLite dosyası orada yaşar.
        SQLModel.metadata.create_all(engine)
        _sqlite_eksik_kolonlari_ekle()


def _sqlite_eksik_kolonlari_ekle() -> None:
    """SQLite'ta modelde OLAN ama tabloda OLMAYAN kolonları ekler. **Yalnız ekler.**

    ## Neden var — CANLI ORTAMDA ÖLÇÜLDÜ (2026-08-03)

    `create_all` yalnız **eksik TABLOYU** yaratır; var olan bir tabloya **kolon EKLEMEZ**.
    Geliştirme SQLite'ı ilk koşuda modelin o günkü hâlinden doğuyor, model ilerliyor, DB
    kalıyor. Ve her yazma yolu bilinçli olarak **best-effort** (`try/except` + WARNING)
    olduğu için hata **görünmüyor** — özellik sessizce ölüyor.

    Çalışan demo konteynerinde ölçülen hasar (`alembic_version` tablosu bile YOKTU, yani
    migration'lar o DB'de **hiç koşmamıştı**):

    | tablo | eksik kolon | sessiz sonuç |
    |---|---|---|
    | `verified_query` | `verified_at` | **VQR tamamen ölü** — ne okuma ne yazma |
    | `interaction_log` | `reject_reason` | Faz 0'ın **red gerekçesi telemetrisi yazılamıyor** |
    | `contract_log` | `provenance_json` | makbuz DB yerine spool'a düşüyor |
    | `notification_log` | `neden_json` | uyarı **nedeni** kaydedilemiyor |

    78 satır `interaction_log` vardı — yani telemetri **akıyordu**, ama ölçmek için
    eklediğim kolon **yoktu**. Ölçüm zincirinin kendisi sessizce kırıktı.

    ## Sınırlar — bu bir migration motoru DEĞİL

    * **Yalnız `ADD COLUMN`.** Kolon silme/tip değiştirme/yeniden adlandırma YAPILMAZ;
      onlar veri kaybı riskidir ve Alembic'in işidir.
    * **Yalnız SQLite.** Postgres'te şema sahibi admin-api + Alembic'tir (ADR-0015).
    * **NOT NULL + varsayılansız** bir kolon SQLite'a eklenemez — o durumda **sessizce
      geçilmez**, WARNING basılır: sessiz bir şema onarımı, onardığı sorunun aynısı olurdu.
    * Eklenen her kolon **loglanır**. Bir şemanın kendiliğinden değişmesi görünür olmalı.
    """
    from sqlalchemy import inspect as _inspect
    from sqlalchemy import text as _text

    from app.logging_setup import get_logger

    log = get_logger("db")
    try:
        mufettis = _inspect(engine)
        mevcut_tablolar = set(mufettis.get_table_names())
    except Exception:  # noqa: BLE001 — şema okunamıyorsa uygulamayı düşürme
        log.warning("SQLite şema denetimi yapılamadı", exc_info=True)
        return

    eklenen: list[str] = []
    for tablo in SQLModel.metadata.sorted_tables:
        if tablo.name not in mevcut_tablolar:
            continue                       # `create_all` zaten yarattı
        var_olan = {c["name"] for c in mufettis.get_columns(tablo.name)}
        for kolon in tablo.columns:
            if kolon.name in var_olan:
                continue
            tip = kolon.type.compile(engine.dialect)
            if not kolon.nullable and kolon.server_default is None and kolon.default is None:
                log.warning(
                    "ŞEMA GERİDE: %s.%s eklenemiyor (NOT NULL + varsayılansız) — "
                    "Alembic ile taşınmalı. O kolona yazan özellik SESSİZCE çalışmayacak.",
                    tablo.name, kolon.name)
                continue
            try:
                with engine.begin() as baglanti:
                    baglanti.execute(_text(
                        f'ALTER TABLE "{tablo.name}" ADD COLUMN "{kolon.name}" {tip}'))
                eklenen.append(f"{tablo.name}.{kolon.name}")
            except Exception:  # noqa: BLE001
                log.warning("ŞEMA GERİDE: %s.%s eklenemedi", tablo.name, kolon.name,
                            exc_info=True)
    if eklenen:
        log.warning("SQLite şeması modele hizalandı — EKLENEN KOLONLAR: %s. "
                    "(Bu bir migration motoru DEĞİLDİR; Postgres'te Alembic sahiptir.)",
                    ", ".join(eklenen))


def get_session() -> Iterator[Session]:
    """FastAPI dependency: istek başına bir Session."""
    with Session(engine) as session:
        yield session
