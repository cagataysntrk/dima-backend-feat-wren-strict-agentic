"use client";

/** **KART ZAMANLAMA** — 🔔 alarm + periyot açılır kutusu. (FAZ 4)
 *
 * ## 🔴 Neden ayrı bir dosya
 *
 * `ReportCard` büyüme tavanının **48 satır üstündeydi** (996/948) ve büyüme kapısı
 * doğru cevabı kendi mesajında yazıyor: *"yeni davranışı bir bileşene çıkar, tavanı
 * yükseltme."*
 *
 * ⚠ Bu bileşen **yeni bir yetenek getirmiyor**: `ReportCard`'ın başlık şeridindeki
 * 81 satırlık açılır kutu buraya taşındı. Alarm türü · ölçü · operatör · eşik ·
 * alıcılar · üç periyot preset'i — hepsi aynen.
 *
 * ## ⚠ Durum YUKARIDA kalır, burada DEĞİL
 *
 * Alarm alanları `ReportCard`'ın durumunda yaşamaya devam ediyor ve buraya **prop**
 * olarak geliyor. Sebebi: açılır kutu kapanıp açıldığında kullanıcının girdiği eşik
 * **kaybolmamalı**. Durumu bileşenin içine almak, her kapanışta sıfırlardı —
 * *bir formu kapatmak, doldurulanı silmek değildir.*
 */

import type { Dispatch, SetStateAction } from "react";

export function KartZamanlama({
  measures,
  alarmType,
  setAlarmType,
  alarmMeasure,
  setAlarmMeasure,
  alarmOp,
  setAlarmOp,
  alarmValue,
  setAlarmValue,
  emails,
  setEmails,
  schedule,
}: {
  measures: string[];
  alarmType: "none" | "threshold" | "anomaly";
  setAlarmType: Dispatch<SetStateAction<"none" | "threshold" | "anomaly">>;
  alarmMeasure: string;
  setAlarmMeasure: Dispatch<SetStateAction<string>>;
  alarmOp: "gt" | "lt";
  setAlarmOp: Dispatch<SetStateAction<"gt" | "lt">>;
  alarmValue: string;
  setAlarmValue: Dispatch<SetStateAction<string>>;
  emails: string;
  setEmails: Dispatch<SetStateAction<string>>;
  schedule: (p: { every: "hour" | "day" | "week"; at?: string; weekday?: number; period: string; name: string }) => void;
}) {
  return (

  <span className="absolute right-0 top-full z-30 mt-1 flex w-64 flex-col gap-2 border border-hairline bg-background p-2 shadow-lg">
    {/* #56 alarm (opsiyonel) — eşik / anomali; ölçü rapor ölçülerinden. */}
    <div className="flex flex-col gap-1">
      <span className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
        alarm (opsiyonel)
      </span>
      <div className="flex gap-1 font-mono text-[11px]">
        {(["none", "threshold", "anomaly"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setAlarmType(t)}
            className={`border px-1.5 py-0.5 transition-colors ${
              alarmType === t
                ? "border-accent/40 text-accent"
                : "border-hairline text-neutral-400 hover:text-foreground"
            }`}
          >
            {t === "none" ? "yok" : t === "threshold" ? "eşik" : "anomali"}
          </button>
        ))}
      </div>
      {alarmType !== "none" && (
        <div className="flex items-center gap-1 font-mono text-[11px]">
          <select
            value={alarmMeasure || measures[0] || ""}
            onChange={(e) => setAlarmMeasure(e.target.value)}
            className="min-w-0 flex-1 border border-hairline bg-background px-1 py-0.5"
          >
            {measures.map((m) => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
          {alarmType === "threshold" ? (
            <>
              <select
                value={alarmOp}
                onChange={(e) => setAlarmOp(e.target.value as "gt" | "lt")}
                className="border border-hairline bg-background px-1 py-0.5"
              >
                <option value="gt">&gt;</option>
                <option value="lt">&lt;</option>
              </select>
              <input
                value={alarmValue}
                onChange={(e) => setAlarmValue(e.target.value)}
                inputMode="decimal"
                placeholder="değer"
                className="w-16 border border-hairline bg-background px-1 py-0.5"
              />
            </>
          ) : (
            <span className="text-neutral-400">z-skoru (olağandışı)</span>
          )}
        </div>
      )}
    </div>
    {/* #56 e-posta teslim (opsiyonel) — in-app bell her zaman düşer. */}
    <input
      value={emails}
      onChange={(e) => setEmails(e.target.value)}
      placeholder="e-posta (virgülle, opsiyonel)"
      className="border border-hairline bg-background px-1.5 py-1 font-mono text-[11px]"
    />
    {/* Periyot preset'i — tıklama mevcut alarm+e-posta ile zamanlar. */}
    <div className="flex flex-col border-t border-hairline pt-1">
      {[
        { name: "her sabah 08:00 · dünün verisi", every: "day" as const, at: "08:00", period: "dün" },
        { name: "her saat · bugünün verisi", every: "hour" as const, period: "bugün" },
        { name: "her pazartesi 08:00 · geçen hafta", every: "week" as const, at: "08:00", weekday: 1, period: "geçen hafta" },
      ].map((pr) => (
        <button
          key={pr.name}
          onClick={() => schedule(pr)}
          className="px-2 py-1.5 text-left font-mono text-[11px] text-neutral-500 hover:bg-neutral-500/[0.06] hover:text-foreground"
        >
          {pr.name}
        </button>
      ))}
    </div>
  </span>
  );
}
