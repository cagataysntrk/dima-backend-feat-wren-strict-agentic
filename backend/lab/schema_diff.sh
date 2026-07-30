#!/usr/bin/env bash
# İki lab DB'sinin şema farkı (ADR-0017 K6 — versiyon stratejisinin verisi).
# Kullanım: ./schema_diff.sh GULTEKS_2021 GULTEKS_GUNCEL
# Logo'da tablo adları firma/dönem öneki taşıdığı için önek normalize edilir:
# LG_113_01_INVOICE ve LG_001_01_INVOICE aynı "LG_FFF_PP_INVOICE" satırına düşer.
set -euo pipefail
cd "$(dirname "$0")"

DB_A="$1"
DB_B="$2"
PASS="${MSSQL_SA_PASSWORD:-DimaLab!2026}"
OUT="reports/schema_diff_${DB_A}_vs_${DB_B}.txt"
mkdir -p reports

dump() { # normalize edilmiş tablo|kolon|tip listesi
  docker exec dima-lab-mssql /opt/mssql-tools18/bin/sqlcmd -C -S localhost -U sa -P "$PASS" \
    -d "$1" -W -s'|' -h -1 -Q "SET NOCOUNT ON;
      SELECT
        CASE WHEN t.name LIKE 'LG[_]%[_]%[_]%'
             THEN 'LG_FFF_PP' + SUBSTRING(t.name, 10, 200)
             WHEN t.name LIKE 'LG[_]%[_]%'
             THEN 'LG_FFF' + SUBSTRING(t.name, 7, 200)
             ELSE t.name END,
        c.name, ty.name, c.max_length
      FROM sys.tables t
      JOIN sys.columns c ON c.object_id = t.object_id
      JOIN sys.types ty ON ty.user_type_id = c.user_type_id
      ORDER BY 1, c.column_id" | grep -v '^$' | sort -u
}

dump "$DB_A" >/tmp/schema_a.txt
dump "$DB_B" >/tmp/schema_b.txt

{
  echo "# Şema diff: $DB_A (A) vs $DB_B (B) — $(date +%F)"
  echo
  echo "## Yalnız A'da olan tablolar"
  comm -23 <(cut -d'|' -f1 /tmp/schema_a.txt | sort -u) <(cut -d'|' -f1 /tmp/schema_b.txt | sort -u)
  echo
  echo "## Yalnız B'de olan tablolar"
  comm -13 <(cut -d'|' -f1 /tmp/schema_a.txt | sort -u) <(cut -d'|' -f1 /tmp/schema_b.txt | sort -u)
  echo
  echo "## Ortak tablolarda kolon/tip farkları (satır düzeyi: tablo|kolon|tip|uzunluk)"
  comm -3 /tmp/schema_a.txt /tmp/schema_b.txt |
    grep -Ff <(comm -12 <(cut -d'|' -f1 /tmp/schema_a.txt | sort -u) <(cut -d'|' -f1 /tmp/schema_b.txt | sort -u)) |
    head -400
} >"$OUT"

echo "Yazıldı: $OUT ($(wc -l <"$OUT" | tr -d ' ') satır)"
