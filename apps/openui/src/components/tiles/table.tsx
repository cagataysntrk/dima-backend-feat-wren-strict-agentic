"use client";

import type { AskResponse } from "@dima/contracts";
import { fmtValue } from "@dima/domain";

import { TileTitle } from "./shared";

export function Table({ response, limit = 10 }: { response: AskResponse; limit?: number }) {
  const result = response.result;
  if (!result?.rows.length) return <p className="muted">Veri yok.</p>;

  const rows = result.rows.slice(0, limit);
  const hidden = result.row_count - rows.length;

  return (
    <>
      <TileTitle>{response.question}</TileTitle>
      <div className="dima-table-wrap">
        <table className="dima-table">
          <thead>
            <tr>
              {result.columns.map((c) => (
                <th key={c}>{c}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, i) => (
              <tr key={i}>
                {result.columns.map((c) => (
                  <td key={c}>{fmtValue(row[c], c)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {hidden > 0 ? <p className="muted">+{hidden} satır daha</p> : null}
    </>
  );
}
