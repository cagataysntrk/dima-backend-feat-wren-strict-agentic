"use client";

// Root layout'un kendisi çökerse devreye girer — bu yüzden layout'a (font,
// provider, global CSS) bağımlı OLAMAZ; bağımsız html/body ve satır içi stil.
export default function GlobalError({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <html lang="tr">
      <body style={{ fontFamily: "system-ui, sans-serif", margin: 0 }}>
        <main
          style={{
            minHeight: "100vh",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: 20,
          }}
        >
          <div style={{ maxWidth: 420, textAlign: "center" }}>
            <h1 style={{ fontSize: 28, margin: 0 }}>Bir şeyler ters gitti.</h1>
            <p style={{ opacity: 0.7, marginTop: 12 }}>Uygulama başlatılamadı. Tekrar deneyin.</p>
            <button
              onClick={reset}
              style={{ marginTop: 20, padding: "10px 20px", fontSize: 15, cursor: "pointer" }}
            >
              Tekrar dene
            </button>
          </div>
        </main>
      </body>
    </html>
  );
}
