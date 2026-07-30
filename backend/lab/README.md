# lab/ — müşteri DB laboratuvarı (ADR-0017 Faz 0)

Gerçek müşteri yedeklerinin (Logo .bak, Mikro .sql export) restore edilip incelendiği
YEREL SQL Server ortamı. Buradaki hiçbir veri git'e girmez (`data/`, `backups/`,
`reports/` gitignore'lu). Interim üretim deseni de budur: yedek → restore → normal
`DbConnection` (cloud_direct) — dosya-tabanlı ayrı sorgu yolu yoktur.

## Kurulum

```bash
cd lab
docker compose up -d          # SQL Server 2022 (amd64 emülasyon), port 14333
```

Parola: `MSSQL_SA_PASSWORD` env'i, yoksa compose'daki varsayılan. `sqlcmd` container
içinde: `/opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P ...`.

## Scriptler

| Script | İş |
|---|---|
| `restore_bak.sh <dosya.bak> <DB_ADI>` | .bak'ı `backups/`e bekler; FILELISTONLY okuyup WITH MOVE ile restore eder |
| `import_mikro_export.sh <export_dizini> <DB_ADI>` | Tablo-başına .sql dosyalarını (upcyman export biçimi) sıralı import eder; hatalı dosyaları raporlar |
| `inventory.sh <DB_ADI>` | Tablo/kolon/satır envanteri + Logo `LG_` önek → firma/dönem keşfi → `reports/` |
| `schema_diff.sh <DB_A> <DB_B>` | İki DB'nin INFORMATION_SCHEMA farkı (tablo/kolon/tip) → `reports/` |

## Mevcut lab DB'leri (2026-07)

| DB | Kaynak | İçerik |
|---|---|---|
| `GULTEKS_2021` | Logo Start 3 yedeği (13.09.2021) | Veri dolu; firma/dönem `LG_` önekli |
| `GULTEKS_GUNCEL` | Logo Start 3 boş firma yedeği (2026) | Boş; güncel şema referansı |
| `ATIKSAN_MIKRO` | Mikro V16 upcyman export'u | Tablo başına TOP-50000 kesikli veri |
