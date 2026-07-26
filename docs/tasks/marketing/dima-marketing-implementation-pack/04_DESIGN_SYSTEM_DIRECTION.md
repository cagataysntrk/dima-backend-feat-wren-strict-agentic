# 04 — Design System Direction

## 1. Creative direction

**Editorial Industrial Intelligence**

Dima'nın marketing görünümü:
- sofistike fakat gösterişsiz,
- veri ve doğrulama hissi veren,
- endüstriyel yazılım güveni taşıyan,
- sıcak editorial yüzeylerle teknik monospaced detayları birleştiren,
- gerçek ürün proof'unu dekorasyonun önüne koyan
bir dil olmalıdır.

## 2. Existing tokens as foundation

Mevcut Dima token'ları zaten güçlü bir temel sağlar:

- Warm off-white light background
- Editorial near-black dark background
- Monochrome primary
- Indigo-violet brand accent
- OKLCH color authoring
- Hairline borders
- Subtle shadows
- Chart palette
- `--font-sans`, `--font-mono`, `--font-display`

Marketing yeni, paralel bir renk sistemi üretmemeli. Gerekirse yalnızca semantic marketing token alias'ları eklenmeli:

```css
--marketing-surface-raised
--marketing-surface-inverse
--marketing-grid
--marketing-proof-glow
--marketing-section-rule
```

Bunlar mevcut root tokens'tan türemelidir.

## 3. Typography

### Display
Playfair Display yalnızca:
- hero H1,
- büyük section statement,
- kısa editorial quote
için.

### Sans
Plus Jakarta Sans:
- navigation,
- body,
- card headings,
- forms,
- CTA,
- FAQ.

### Mono
JetBrains Mono:
- SQL,
- query status,
- source labels,
- “dry-plan verified”,
- metric/code labels.

### Scale
Öneri:
- Hero: clamp(3rem, 7vw, 6.5rem), çok uzun Türkçe satırlarda kontrollü.
- H2: clamp(2rem, 4vw, 4.25rem).
- H3: 1.25–1.5rem.
- Body large: 1.125–1.25rem.
- Body: minimum 1rem.
- Eyebrow: 0.75rem uppercase/letter spacing, erişilebilir contrast.

Line length:
- Body max 65–75 karakter.
- Hero subhead max 55–65 karakter.

## 4. Layout

### Grid
- Max content width: 1200–1280px.
- Reading column: 680–760px.
- Desktop 12-column grid.
- Tablet 6-column.
- Mobile single-column.
- Section spacing: 96–144px desktop, 64–96px mobile.
- Header fixed/sticky ise page offset ve focus visibility test edilmeli.

### Section rhythm
Alternating:
- open editorial section,
- bordered proof surface,
- dense bento/use-case section,
- open trust section.

Her section'ın aynı card grid görünümüne dönüşmesinden kaçının.

## 5. Component grammar

### MarketingSection
- semantic `section`
- optional eyebrow/title/description
- predictable spacing
- anchor `scroll-mt-*`

### ProofFrame
- browser/app frame
- data source status
- query prompt
- validation timeline
- result view
- optional callout annotations

### PillarCard
- Letter D/I/M/A
- single mechanism
- status
- deep link

### EvidenceLabel
Monospace mini label:
- `MODELED`
- `SELECT ONLY`
- `DRY-PLAN VERIFIED`
- `TENANT SCOPED`

### CTA
- Primary: brand/ink high contrast
- Secondary: outline/ghost
- No rainbow
- No constant shimmer
- Hover transform max 1–2px, no layout shift

### Bento
Bento yalnızca farklı content density gerekiyorsa:
- large proof card
- narrow process card
- metric/card sample
- integration map
- trace snippet

## 6. Motion language

Mevcut Dima motion prensiplerini koruyun:

- transform + opacity
- fast ease-out
- 150–300ms microinteraction
- 350–550ms section reveal
- one-time viewport animation
- no scale-from-zero
- no continuous animation except subtle status pulse
- `prefers-reduced-motion` respected
- motion is never the sole carrier of meaning

Hero:
- text stagger minimal,
- proof frame enters after copy,
- no particle canvas,
- no scroll-jacking,
- no auto-rotating headline required.

## 7. Product proof visual

En güçlü visual bir “real UI choreography” olmalıdır:

1. Prompt typed or revealed.
2. Context tags appear.
3. Validation steps show.
4. Result chart/table renders.
5. SQL/trace detail is visible.

Public page gerçek API'ye bağlanmamalı. Bu akış:
- static typed data,
- deterministic local state,
- no PII,
- no network dependency,
- reduced-motion'da final state
ile çalışmalıdır.

## 8. UpcyMan reference protocol

Agent şu local path'i salt-okunur inceleyebilir:

`/Users/enesteve/Desktop/Coding/Upcy/upcyman/upcyman`

Öncelikli referanslar:
- marketing page composition
- navbar/footer
- hero structure
- bento grid
- feature mockups
- responsive section spacing
- i18n organization
- reduced-motion and animation primitives

Kurallar:
1. UpcyMan'de hiçbir dosyayı değiştirme.
2. Symlink oluşturma.
3. Cross-repo import yapma.
4. Dima repo'suna büyük klasör kopyalama.
5. Component fikrini Dima tokens ve semantics ile yeniden uygula.
6. Third-party primitive ise resmi source ve license'ı kullan.
7. UpcyMan brand/copy/assets taşınmaz.

## 9. Anti-patterns

- Her kartta glow/border beam.
- Hero'da canvas particles + grid + gradient + moving beam aynı anda.
- Çok sayıda font.
- Gradient text'in ana H1 okunabilirliğini bozması.
- Küçük muted text.
- Desktop screenshot'ı mobile'da sadece küçültmek.
- Hover-only content.
- Carousel içinde kritik bilgi.
- Infinite marquee içinde okunması gereken metin.
- Mockup'larda sahte/gerçek dışı numbers.
- Farklı sayfalarda farklı radius/shadow sistemi.
