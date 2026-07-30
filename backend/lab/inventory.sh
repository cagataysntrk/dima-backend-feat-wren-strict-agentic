#!/usr/bin/env bash
# Şema envanteri + ERP fingerprint verisi (ADR-0017 Faz 0).
# Kullanım: ./inventory.sh GULTEKS_2021
# Çıktı: reports/inventory_<DB>.txt — tablo/satır envanteri, Logo LG_ firma/dönem
# keşfi, Mikro imza kontrolü.
set -euo pipefail
cd "$(dirname "$0")"

DB_NAME="$1"
PASS="${MSSQL_SA_PASSWORD:-DimaLab!2026}"
OUT="reports/inventory_${DB_NAME}.txt"
mkdir -p reports

sql() {
  docker exec dima-lab-mssql /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P "$PASS" \
    -d "$DB_NAME" -W -s'|' -Q "SET NOCOUNT ON; $1"
}

{
  echo "# Envanter: $DB_NAME ($(date +%F))"
  echo
  echo "## Boyut ve tablo sayısı"
  sql "SELECT COUNT(*) AS tablo_sayisi FROM sys.tables"
  sql "SELECT CAST(SUM(size)*8/1024 AS int) AS mb FROM sys.database_files"

  echo
  echo "## En büyük 40 tablo (satır sayısıyla)"
  sql "SELECT TOP 40 t.name, SUM(p.rows) AS satir
       FROM sys.tables t JOIN sys.partitions p
         ON t.object_id=p.object_id AND p.index_id IN (0,1)
       GROUP BY t.name ORDER BY satir DESC"

  echo
  echo "## Logo imzası: LG_ önekli tablolar → firma/dönem dağılımı"
  sql "SELECT LEFT(name, 7) AS firma_donem, COUNT(*) AS tablo
       FROM sys.tables WHERE name LIKE 'LG[_]%'
       GROUP BY LEFT(name, 7) ORDER BY 1"

  echo
  echo "## Logo firma tanımları (L_CAPIFIRM: no, ad, sürüm)"
  sql "IF OBJECT_ID('L_CAPIFIRM','U') IS NOT NULL
         SELECT NR, NAME, VERSION FROM L_CAPIFIRM ORDER BY NR
       ELSE SELECT 'L_CAPIFIRM yok' AS bilgi"

  echo
  echo "## Logo dönem tanımları (L_CAPIDIV/PERDOC benzeri ilk eşleşen)"
  sql "SELECT name FROM sys.tables WHERE name LIKE 'L[_]%' ORDER BY name"

  echo
  echo "## Mikro imzası: CARI_HESAPLAR + cari_ önekli kolonlar"
  sql "IF OBJECT_ID('CARI_HESAPLAR','U') IS NOT NULL
         SELECT COUNT(*) AS cari_kolon FROM sys.columns
         WHERE object_id=OBJECT_ID('CARI_HESAPLAR') AND name LIKE 'cari[_]%'
       ELSE SELECT 'CARI_HESAPLAR yok' AS bilgi"

  echo
  echo "## Şema parmak izi (tablo+kolon+tip hash'i — drift takibi, ADR-0017 K6)"
  sql "SELECT CONVERT(varchar(64), HASHBYTES('SHA2_256', (
         SELECT t.name, c.name, ty.name, c.max_length
         FROM sys.tables t
         JOIN sys.columns c ON c.object_id = t.object_id
         JOIN sys.types ty ON ty.user_type_id = c.user_type_id
         ORDER BY t.name, c.column_id FOR XML PATH(''))), 2) AS sema_hash"
} >"$OUT"

echo "Yazıldı: $OUT ($(wc -l <"$OUT" | tr -d ' ') satır)"
