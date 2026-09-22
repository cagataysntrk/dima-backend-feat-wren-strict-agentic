// Küçük, bağımlılıksız SQL biçimlendirici + sözcükleyici. Amaç bir SQL motoru
// değil, OKUNAKLI gösterim: backend'in ürettiği tek satırlık SQL'i satırlara böl
// ve renklendirme için token'lara ayır. (Bir highlighter paketi eklemiyoruz:
// bundle maliyeti ve inline-style/CSP yüzeyi için — bkz. next.config.ts notu.)

export type SqlTokenType =
  | "keyword"
  | "function"
  | "string"
  | "number"
  | "comment"
  | "punct"
  | "ident"
  | "space";

export interface SqlToken {
  type: SqlTokenType;
  text: string;
}

// Satır başına alınan yan tümceler (kendi satırında, girintisiz).
const CLAUSE = new Set([
  "SELECT", "FROM", "WHERE", "HAVING", "LIMIT", "OFFSET", "UNION", "INTERSECT",
  "EXCEPT", "WITH", "VALUES", "RETURNING", "WINDOW", "FETCH",
]);
// İki sözcüklü yan tümceler (GROUP BY, ORDER BY, PARTITION BY).
const CLAUSE_2 = new Set(["GROUP", "ORDER", "PARTITION"]);
// Satır başına alınan ama girintili olanlar.
const INDENTED = new Set(["JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "FULL", "CROSS", "ON", "AND", "OR"]);

const KEYWORDS = new Set([
  ...CLAUSE, ...CLAUSE_2, ...INDENTED,
  "AS", "BY", "ASC", "DESC", "DISTINCT", "ALL", "CASE", "WHEN", "THEN", "ELSE",
  "END", "IN", "IS", "NOT", "NULL", "LIKE", "ILIKE", "BETWEEN", "EXISTS", "OVER",
  "USING", "INTERVAL", "DATE", "CAST", "FILTER", "TRUE", "FALSE", "NULLS", "FIRST", "LAST",
]);

const FUNCTIONS = new Set([
  "COUNT", "SUM", "AVG", "MIN", "MAX", "ROUND", "ABS", "COALESCE", "NULLIF",
  "DATE_TRUNC", "EXTRACT", "TO_CHAR", "NOW", "GREATEST", "LEAST", "LOWER",
  "UPPER", "CONCAT", "LENGTH", "SUBSTRING", "RANK", "ROW_NUMBER", "DENSE_RANK", "LAG", "LEAD",
]);

const MULTI_OPS = new Set([">=", "<=", "<>", "!=", "||", "::"]);
// JOIN'den önce gelebilen niteleyiciler — "LEFT JOIN" tek satırda kalmalı.
const JOIN_PREFIX = new Set(["LEFT", "RIGHT", "INNER", "OUTER", "FULL", "CROSS"]);

/** Split SQL into typed tokens (whitespace preserved as "space"). */
export function tokenizeSql(sql: string): SqlToken[] {
  const out: SqlToken[] = [];
  let i = 0;
  while (i < sql.length) {
    const c = sql[i];

    if (/\s/.test(c)) {
      let j = i;
      while (j < sql.length && /\s/.test(sql[j])) j++;
      out.push({ type: "space", text: sql.slice(i, j) });
      i = j;
      continue;
    }
    // Şablon değişkeni {{ad}} ve isteğe bağlı blok [[ … ]] — biçimlendirici
    // bunları bölerse sorgu çalışmaz; tek token olarak geçsinler.
    if (c === "{" && sql[i + 1] === "{") {
      const j = sql.indexOf("}}", i + 2);
      if (j !== -1) {
        out.push({ type: "ident", text: sql.slice(i, j + 2) });
        i = j + 2;
        continue;
      }
    }
    if ((c === "[" || c === "]") && sql[i + 1] === c) {
      out.push({ type: "punct", text: c + c });
      i += 2;
      continue;
    }
    if (c === "-" && sql[i + 1] === "-") {
      const j = sql.indexOf("\n", i);
      const end = j === -1 ? sql.length : j;
      out.push({ type: "comment", text: sql.slice(i, end) });
      i = end;
      continue;
    }
    if (c === "/" && sql[i + 1] === "*") {
      const j = sql.indexOf("*/", i + 2);
      const end = j === -1 ? sql.length : j + 2;
      out.push({ type: "comment", text: sql.slice(i, end) });
      i = end;
      continue;
    }
    if (c === "'" || c === '"' || c === "`") {
      let j = i + 1;
      while (j < sql.length) {
        if (sql[j] === c) {
          if (sql[j + 1] === c) j += 2;
          else break;
        } else j++;
      }
      out.push({ type: c === "'" ? "string" : "ident", text: sql.slice(i, Math.min(j + 1, sql.length)) });
      i = j + 1;
      continue;
    }
    if (/[0-9]/.test(c)) {
      let j = i;
      while (j < sql.length && /[0-9._]/.test(sql[j])) j++;
      out.push({ type: "number", text: sql.slice(i, j) });
      i = j;
      continue;
    }
    if (/[A-Za-z_]/.test(c)) {
      let j = i;
      while (j < sql.length && /[\w$]/.test(sql[j])) j++;
      const word = sql.slice(i, j);
      const upper = word.toUpperCase();
      // fonksiyon = bilinen ad ya da hemen ardından "(" gelen tanımlayıcı
      let k = j;
      while (k < sql.length && /\s/.test(sql[k])) k++;
      const isCall = sql[k] === "(";
      out.push({
        type: KEYWORDS.has(upper) ? "keyword" : FUNCTIONS.has(upper) || isCall ? "function" : "ident",
        text: word,
      });
      i = j;
      continue;
    }
    // çok karakterli operatörler tek token olmalı (>=, <=, <>, !=, ||, ::)
    const two = sql.slice(i, i + 2);
    if (MULTI_OPS.has(two)) {
      out.push({ type: "punct", text: two });
      i += 2;
      continue;
    }
    out.push({ type: "punct", text: c });
    i++;
  }
  return out;
}

/**
 * Reflow one-line SQL onto readable lines: clauses start a line, JOIN/ON/AND/OR
 * are indented, and top-level commas break the select list. Commas inside
 * parentheses (function arguments) are deliberately left alone.
 */
export function formatSql(sql: string): string {
  const tokens = tokenizeSql(sql.trim()).filter((t) => t.type !== "space");
  let out = "";
  let depth = 0;
  let atLineStart = true;
  let prev: SqlToken | null = null;
  let inJoin = false; // "LEFT" yazıldı, ardından gelen JOIN aynı satırda kalsın
  let optOpen = false; // "[[" yazıldı — ardından gelen AND/OR satır açmasın

  const nl = (indent: number) => {
    // Zaten satır başındaysak (ör. yorum satırı kapattı) boş satır açma.
    if (atLineStart) {
      out = out.replace(/[ \t]+$/, "") + "  ".repeat(indent);
      return;
    }
    out = out.replace(/[ \t]+$/, "");
    out += "\n" + "  ".repeat(indent);
    atLineStart = true;
  };
  const push = (s: string) => {
    const noSpaceBefore =
      atLineStart ||
      /^[),;.]/.test(s) || // kapanış, virgül, nokta
      s === "]]" ||
      s === "::" || // tür dönüşümü operatörü iki yana da yapışır
      out.endsWith("[[") ||
      out.endsWith("::") ||
      out.endsWith("(") ||
      out.endsWith(".") ||
      // fonksiyon çağrısı: ad ile "(" bitişik
      (s === "(" && (prev?.type === "function" || prev?.type === "ident"));
    if (!noSpaceBefore) out += " ";
    out += s;
    atLineStart = false;
  };

  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    const upper = t.text.toUpperCase();
    const emit = (s: string) => {
      push(s);
      prev = t;
    };

    if (t.type === "punct") {
      // İsteğe bağlı blok kendi satırında başlar; içindeki AND/OR ona yapışır.
      if (t.text === "[[") {
        if (out) nl(1);
        optOpen = true;
        emit("[[");
        continue;
      }
      if (t.text === "(") {
        depth++;
        emit("(");
        continue;
      }
      if (t.text === ")") {
        depth = Math.max(0, depth - 1);
        emit(")");
        continue;
      }
      if (t.text === "," && depth === 0) {
        out += ",";
        prev = t;
        nl(1);
        continue;
      }
      emit(t.text);
      continue;
    }

    if (t.type === "keyword" && depth === 0) {
      // GROUP BY / ORDER BY / PARTITION BY — iki sözcüğü birlikte yaz
      if (CLAUSE_2.has(upper) && tokens[i + 1]?.text.toUpperCase() === "BY") {
        if (out) nl(0);
        push(`${upper} BY`);
        i++;
        continue;
      }
      if (CLAUSE.has(upper)) {
        if (out) nl(0);
        push(upper);
        continue;
      }
      if (INDENTED.has(upper)) {
        // "LEFT JOIN" / "INNER JOIN" — niteleyici satırı açar, JOIN aynı satırda kalır
        if (upper === "JOIN" && inJoin) {
          inJoin = false;
          emit(upper);
          continue;
        }
        if (out && !optOpen) nl(1);
        optOpen = false;
        inJoin = JOIN_PREFIX.has(upper);
        emit(upper);
        continue;
      }
      emit(upper);
      continue;
    }

    if (t.type === "comment") {
      if (out && !atLineStart) out += " ";
      out += t.text;
      atLineStart = false;
      prev = t;
      // Satır yorumu satır sonuna kadar sürer: kapatmazsak ardındaki kod da
      // yorumun içinde kalır.
      if (t.text.startsWith("--")) nl(depth > 0 ? 1 : 0);
      continue;
    }

    emit(t.type === "keyword" || t.type === "function" ? upper : t.text);
  }

  return out.trim();
}
