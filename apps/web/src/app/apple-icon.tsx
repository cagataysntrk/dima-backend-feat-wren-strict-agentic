import { ImageResponse } from "next/og";

// Apple touch icon (180×180) — dima "d" mark, amber i-dot on editorial ink.
// Serving this via the App Router convention adds the <link rel="apple-touch-icon">
// and stops browsers probing /apple-touch-icon.png (404).
export const size = { width: 180, height: 180 };
export const contentType = "image/png";

export default function AppleIcon() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          background: "#131312",
          color: "#f2f0ee",
          fontSize: 116,
          fontWeight: 600,
          fontFamily: "Georgia, 'Times New Roman', serif",
          position: "relative",
        }}
      >
        d
        <div
          style={{
            position: "absolute",
            width: 16,
            height: 16,
            borderRadius: 16,
            background: "#f5a524",
            top: 44,
            left: 108,
          }}
        />
      </div>
    ),
    { ...size },
  );
}
