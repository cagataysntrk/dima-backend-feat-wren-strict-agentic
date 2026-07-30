#!/usr/bin/env bash
# .bak yedeğini lab SQL Server'ına restore eder (ADR-0017 Faz 0).
# Kullanım: ./restore_bak.sh backups/GULTEKS_FIRMALAR.bak GULTEKS_GUNCEL
set -euo pipefail
cd "$(dirname "$0")"

BAK_PATH="$1" # backups/ altındaki dosya (host yolu)
DB_NAME="$2"
PASS="${MSSQL_SA_PASSWORD:-DimaLab!2026}"
BAK_IN_CONTAINER="/backups/$(basename "$BAK_PATH")"

sql() {
  docker exec dima-lab-mssql /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P "$PASS" -W -s'|' -h -1 -Q "$1"
}

echo "== FILELISTONLY: $BAK_IN_CONTAINER"
# Mantıksal dosya adlarını ve tiplerini (D=data, L=log) oku
FILELIST=$(sql "SET NOCOUNT ON; RESTORE FILELISTONLY FROM DISK = N'$BAK_IN_CONTAINER'" | grep -v '^$')
echo "$FILELIST" | cut -d'|' -f1,3 | head -20

# MOVE cümlelerini üret: her mantıksal dosya kendi tipine göre .mdf/.ldf'e gider
MOVES=""
i=0
while IFS='|' read -r logical physical type _rest; do
  [ -z "$logical" ] && continue
  case "$type" in
    L) ext="ldf" ;;
    *) ext="mdf" ;;
  esac
  MOVES="$MOVES MOVE N'$logical' TO N'/var/opt/mssql/data/${DB_NAME}_${i}.${ext}',"
  i=$((i + 1))
done <<<"$FILELIST"

echo "== RESTORE DATABASE $DB_NAME"
sql "RESTORE DATABASE [$DB_NAME] FROM DISK = N'$BAK_IN_CONTAINER' WITH $MOVES REPLACE, STATS = 25"
sql "SELECT name, state_desc FROM sys.databases WHERE name = N'$DB_NAME'"
echo "== TAMAM: $DB_NAME"
