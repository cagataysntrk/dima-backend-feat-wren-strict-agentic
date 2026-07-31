"""RuleBasedSqlGenerator'ın OEE dalı — Faz 2b regresyon kilidi (31 Temmuz 2026).

47-tablo rebind'inden (eski `vardiya_kayitlari` → `oee_vardiya`) sonra bu dal hiç
güncellenmemişti: `use_oee` kapısı artık HİÇBİR ZAMAN doğru olmadığından fiilen ÖLÜ KOD'du
ve oee-ipucu taşıyan sorular sessizce `_partiler_sql`'e (ilgisiz cube) düşüyordu. Bu testler
hem "artık gerçek `oee_vardiya` şemasına karşı ÇALIŞIYOR" (dry_plan geçiyor) hem de "eski
tablo adına asla bir daha sessizce geri dönmüyor" garantisini kilitler."""

from app.llm import RuleBasedSqlGenerator


def test_oee_sql_kullanir_gercek_tablo_adini(schema):
    gen = RuleBasedSqlGenerator()
    sql = gen.generate_sql("makine bazında ortalama oee", schema)
    assert "oee_vardiya" in sql
    assert "vardiya_kayitlari" not in sql


def test_oee_sql_dry_plan_gecer(schema):
    """Üretilen SQL gerçek demo MDL'sine karşı GERÇEKTEN planlanabilir olmalı — eski
    kod bu noktada "tablo/kolon yok" hatasıyla patlardı (hiç fark edilmemişti çünkü
    `use_oee` zaten hep False'du, buraya hiç ulaşılmıyordu)."""
    from app.config import get_settings
    from app.wren_service import WrenService

    s = get_settings()
    svc = WrenService(project_dir=s.resolved_project_dir(), datasource=s.datasource,
                      connection_info=s.connection_dict())
    gen = RuleBasedSqlGenerator()
    for q in ["makine bazında ortalama oee", "vardiya bazında kullanılabilirlik",
             "gündüz vardiyasında toplam duruş"]:
        sql = gen.generate_sql(q, schema)
        svc.dry_plan(sql)  # hata fırlatmazsa geçer


def test_oee_sql_gercek_kolon_adlarini_kullanir(schema):
    gen = RuleBasedSqlGenerator()
    sql = gen.generate_sql("vardiya bazında kullanılabilirlik", schema)
    assert "kullanilabilirlik_EV" in sql
    sql2 = gen.generate_sql("makine bazında performans", schema)
    assert "performans_PV" in sql2
    sql3 = gen.generate_sql("makine bazında duruş", schema)
    assert "planli_durus_dk" in sql3 and "plansiz_durus_dk" in sql3


def test_vardiya_gunduz_aksam_gece_artik_tam_sayi_filtreler(schema):
    """vardiya kolonu artık TAM SAYI (1/2/3) — eski kod 'Gündüz'/'Akşam'/'Gece' metin
    değeriyle filtrelerdi (o tabloda hiç var olmamış bir eşleme)."""
    gen = RuleBasedSqlGenerator()
    sql = gen.generate_sql("gündüz vardiyasında toplam duruş", schema)
    assert "vardiya = 1" in sql
    assert "Gündüz" not in sql
