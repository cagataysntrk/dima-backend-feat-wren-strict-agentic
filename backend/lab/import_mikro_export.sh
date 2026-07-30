#!/usr/bin/env bash
# upcyman Mikro export'unu (tablo-başına .sql) lab SQL Server'ına import eder.
# Kullanım: ./import_mikro_export.sh backups/atiksan ATIKSAN_MIKRO
#
# Export biçiminin bilinen kusurları burada onarılır (kaynak: upcyman
# integrations.service.ts generateTableSQL):
#   - Tipler uzunluksuz yazılmış: `nvarchar` T-SQL'de nvarchar(1) demektir → (max)'a
#     genişletilir; decimal/numeric hassasiyetsiz → (38,10).
#   - Tarih literalleri ISO-Z biçiminde ('...T...000Z') → datetime kabul etmez,
#     milisaniye korunup Z atılır.
set -euo pipefail
cd "$(dirname "$0")"

SRC_DIR="$1" # host yolu, backups/ altında olmalı (container'a mount)
DB_NAME="$2"
PASS="${MSSQL_SA_PASSWORD:-DimaLab!2026}"
FIXED_DIR="${SRC_DIR%/}-fixed"
LOG="reports/import_${DB_NAME}.log"

mkdir -p "$FIXED_DIR" reports

echo "== Ön-işleme: $SRC_DIR → $FIXED_DIR"
for f in "$SRC_DIR"/*.sql; do
  base=$(basename "$f")
  [ -f "$FIXED_DIR/$base" ] && continue
  sed -E \
    -e 's/\] (nvarchar|varchar) (NOT NULL|NULL)/] \1(max) \2/g' \
    -e 's/\] (nchar|char) (NOT NULL|NULL)/] \1(255) \2/g' \
    -e 's/\] (varbinary|binary|image) (NOT NULL|NULL)/] varbinary(max) \2/g' \
    -e 's/\] (decimal|numeric) (NOT NULL|NULL)/] \1(38,10) \2/g' \
    -e "s/(\.[0-9]{3})Z'/\1'/g" \
    "$f" >"$FIXED_DIR/$base"
done
echo "   $(ls "$FIXED_DIR" | wc -l | tr -d ' ') dosya hazır"

echo "== DB oluştur: $DB_NAME"
docker exec dima-lab-mssql /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P "$PASS" \
  -Q "IF DB_ID(N'$DB_NAME') IS NULL CREATE DATABASE [$DB_NAME]"

echo "== Import (log: $LOG)"
: >"$LOG"
# Tek docker exec içinde döngü: dosya başına exec maliyeti ödenmez.
docker exec dima-lab-mssql bash -c '
  ok=0; fail=0
  for f in /backups/'"$(basename "$FIXED_DIR")"'/*.sql; do
    if /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P "'"$PASS"'" \
        -d "'"$DB_NAME"'" -b -m 1 -i "$f" >/tmp/imp.out 2>&1; then
      ok=$((ok+1))
    else
      fail=$((fail+1))
      echo "=== HATA: $(basename "$f")"; tail -3 /tmp/imp.out
    fi
  done
  echo "=== SONUC ok=$ok fail=$fail"
' | tee -a "$LOG" | grep -E '^=== ' || true

echo "== Satır sayıları (ilk 10 tablo)"
docker exec dima-lab-mssql /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P "$PASS" -d "$DB_NAME" -W \
  -Q "SET NOCOUNT ON; SELECT TOP 10 t.name, SUM(p.rows) AS satir FROM sys.tables t JOIN sys.partitions p ON t.object_id=p.object_id AND p.index_id IN (0,1) GROUP BY t.name ORDER BY satir DESC"
