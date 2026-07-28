"use client";

import type { AskResponse } from "@dima/contracts";

/**
 * Kanıt rozeti — her karoda görünür.
 *
 * Panoyu model kompoze etti diye kanıt zinciri kaybolmaz: SQL'i kimin ürettiği
 * (`source`: "cube" deterministik, "llm:*", "rule") ve varsa sözleşme kimliği
 * karonun üstünde kalır. Generative yerleşim, denetlenebilirliği düşürmemeli.
 */
export function Provenance({ response }: { response: AskResponse }) {
  const source = response.source ?? "bilinmiyor";
  const deterministic = source.startsWith("cube");
  return (
    <footer className="dima-provenance">
      <span className={deterministic ? "ok" : "warn"}>
        {deterministic ? "deterministik" : source}
      </span>
      {response.contract_id ? <span className="muted">#{response.contract_id}</span> : null}
    </footer>
  );
}

/**
 * Model katalogda olmayan bir kimliğe atıf yaptı.
 *
 * Sessizce boş dönmek ya da örnek veriyle doldurmak en kötü davranış olurdu —
 * kullanıcı gerçek bir pano gördüğünü sanardı. Eksik olan görünür olmalı; bu
 * mesaj aynı zamanda modele geri beslenecek düzeltme sinyalidir.
 */
export function Missing({ resultId }: { resultId: string }) {
  return (
    <article className="dima-tile dima-missing">
      <strong>Sonuç bulunamadı: {resultId}</strong>
      <p>Bu kimlik katalogda yok. Karo boş bırakıldı — veri uydurulmadı.</p>
    </article>
  );
}

/** Backend'in deterministik yorumu. Metin modelden GELMEZ. */
export function Insight({ response }: { response: AskResponse }) {
  if (!response.interpretation) {
    return <p className="muted">Bu sonuç için yorum üretilmedi.</p>;
  }
  return (
    <div className="dima-insight">
      <p>{response.interpretation.summary}</p>
      {response.interpretation.facts?.length ? (
        <ul>
          {response.interpretation.facts.map((f, i) => (
            <li key={i}>{f.text}</li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

export function TileTitle({ children }: { children: string }) {
  return <h3 className="dima-tile-title">{children}</h3>;
}
