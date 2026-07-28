"use client";

import type { AskResponse } from "@dima/contracts";
import { analyze, fmtValue, kpiCards } from "@dima/domain";

import { TileTitle } from "./shared";

/**
 * KPI karosu. İki kaynağı da destekler:
 *  - `response.kpi` — cross-cube KPI kartı (CCC, likidite): değer + bileşenler
 *  - tek satırlık normal sonuç — `kpiCards()` ile ölçülere ayrılır
 */
export function Kpi({ response }: { response: AskResponse }) {
  const kpi = response.kpi;

  if (kpi) {
    return (
      <>
        <TileTitle>{kpi.label}</TileTitle>
        <p className="dima-kpi-value">
          {kpi.value == null ? "—" : kpi.value.toLocaleString("tr-TR")}
          {kpi.unit ? <span className="dima-kpi-unit"> {kpi.unit}</span> : null}
        </p>
        {kpi.components.length ? (
          <dl className="dima-kpi-components">
            {kpi.components.map((c) => (
              <div key={c.key}>
                <dt>{c.label}</dt>
                <dd>
                  {c.value == null ? "—" : c.value.toLocaleString("tr-TR")}
                  {c.unit ? ` ${c.unit}` : ""}
                </dd>
              </div>
            ))}
          </dl>
        ) : null}
      </>
    );
  }

  if (!response.result?.rows.length) return <p className="muted">Veri yok.</p>;

  const cards = kpiCards(response.result, analyze(response.result));
  return (
    <>
      <TileTitle>{response.question}</TileTitle>
      <dl className="dima-kpi-components">
        {cards.map((c) => (
          <div key={c.label}>
            <dt>{c.label}</dt>
            <dd className="dima-kpi-value">{c.value}</dd>
            {c.ctx ? <dd className="muted">{c.ctx}</dd> : null}
          </div>
        ))}
      </dl>
    </>
  );
}

/** Tek değeri birimiyle biçimler — tablo/grafik dışındaki yerlerde kullanılır. */
export function formatOne(value: unknown, column: string): string {
  return fmtValue(value, column);
}
