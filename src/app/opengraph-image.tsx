import { ImageResponse } from "next/og";

// OG/paylaşım görseli — koyu zemin, wordmark + amber imleç (landing imleciyle aynı dil),
// açılım ve alt başlık. 1200×630.
export const alt = "dima — verinle konuş";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "#08090a",
          color: "#e8e8e6",
        }}
      >
        <div style={{ display: "flex", alignItems: "flex-end", fontSize: 250, fontWeight: 600, letterSpacing: -10 }}>
          dima
          {/* amber imleç bloğu — terminal caret göndermesi */}
          <div style={{ width: 14, height: 150, background: "#f5a524", marginLeft: 20, marginBottom: 34 }} />
        </div>
        <div
          style={{
            fontSize: 30,
            letterSpacing: 14,
            color: "#8a8a8a",
            marginTop: 34,
            textTransform: "uppercase",
          }}
        >
          deterministic · intelligent · modeled · agentic
        </div>
        <div style={{ fontSize: 26, color: "#6b6b6b", marginTop: 44 }}>
          verinle konuş — güvenilir SQL, anında rapor
        </div>
      </div>
    ),
    { ...size },
  );
}
