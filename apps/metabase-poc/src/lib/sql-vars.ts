// {{variable}} support for the SQL editor. Pure, unit-tested, shared by the
// editor (which renders an input per variable) and the gateway (which turns
// them into engine template tags + parameter values).
//
//   select * from t where 1=1 [[and makine = {{makine}}]]
//     {{name}}   — a value the user fills in
//     [[ … ]]    — the clause is dropped when its variable has no value

export type VarType = "text" | "number" | "date";

export interface SqlVar {
  name: string;
  type: VarType;
  /** Label shown above the input. */
  label: string;
}

const VAR = /\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}/g;
const DATE_NAME = /(tarih|date|gun|day|ay$|month|yil|year|baslangic|bitis|start|end)/i;
const NUMBER_NAME = /(adet|sayi|count|miktar|tutar|min|max|limit|esik|threshold|yuzde|oran|vardiya|yil|year)/i;

/** Type guessed from the variable's name; the editor lets the user change it. */
export function guessType(name: string): VarType {
  if (DATE_NAME.test(name) && !/^(yil|year)$/i.test(name)) return "date";
  if (NUMBER_NAME.test(name)) return "number";
  return "text";
}

const label = (name: string) =>
  name.replace(/_/g, " ").replace(/^./, (c) => c.toLocaleUpperCase("tr-TR"));

/** Variables in the query, in first-appearance order, without duplicates. */
export function parseVariables(sql: string): SqlVar[] {
  const seen = new Set<string>();
  const out: SqlVar[] = [];
  for (const m of sql.matchAll(VAR)) {
    const name = m[1];
    if (seen.has(name)) continue;
    seen.add(name);
    out.push({ name, type: guessType(name), label: label(name) });
  }
  return out;
}

export interface VarValue {
  name: string;
  type: VarType;
  value: string;
}

/** Engine template tags for the query's variables (values become defaults when saving). */
export function templateTags(vars: SqlVar[], values: Record<string, string> = {}, asDefaults = false) {
  const tags: Record<string, Record<string, unknown>> = {};
  for (const v of vars) {
    const value = values[v.name]?.trim();
    tags[v.name] = {
      id: `tag-${v.name}`,
      name: v.name,
      "display-name": v.label,
      type: v.type,
      ...(asDefaults && value ? { default: v.type === "number" ? Number(value) : value } : {}),
    };
  }
  return tags;
}

const PARAM_TYPE: Record<VarType, string> = { text: "category", number: "number/=", date: "date/single" };

/** Engine parameter values for the filled-in variables (empty ones are left out). */
export function parameterValues(vars: SqlVar[], values: Record<string, string> = {}) {
  return vars.flatMap((v) => {
    const raw = values[v.name]?.trim();
    if (!raw) return [];
    if (v.type === "number" && Number.isNaN(Number(raw))) return [];
    return [
      {
        type: PARAM_TYPE[v.type],
        target: ["variable", ["template-tag", v.name]],
        value: v.type === "number" ? [Number(raw)] : raw,
      },
    ];
  });
}
