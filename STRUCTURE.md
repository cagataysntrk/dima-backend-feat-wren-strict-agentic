# dima-clients — repo yapısı

Frontend istemcilerin tek monorepo'su. Backend (`dima-backend`, Python) ayrı
repoda; sınır orada çünkü dil, deploy ve çalışma zamanı gerçekten farklı.
İstemciler arasında böyle bir sınır yok.

**bun** (paket yöneticisi) + **Turborepo** (görev orkestrasyonu). İkisi
birbirinin alternatifi değil: bun bağımlılıkları çözer ve workspace'leri
birbirine bağlar, turbo görevleri sıralar/paralelleştirir/cache'ler.

```
apps/
  web/          Next 16 — ürün (:3000)
  openui/       generative UI tezgâhı (:3001)
packages/
  contracts/          backend tipleri — React/DOM/Node YOK
  domain/             chart · format · sql-format — saf iş mantığı
  api-client/         tek HTTP yüzeyi
  typescript-config/  base · library · nextjs
  eslint-config/      next · library · platform-free
```

## `apps/` mi `packages/` mi

Ölçüt **"deploy ediliyor mu"** değil — dev sunucusu olan bir şey de app
sayılabilir. Belirleyici olan **import ediliyor mu**:

> Başka bir workspace onu `import` ediyorsa **paket** olmak zorundadır.
> Çünkü kural 2 diyor ki: hiçbir app başka bir app'ten import etmez.

Bu yüzden React Email şablonları `packages/email` olur (marketing onları
import edip Resend'e verecek) ama önizleme sunucusu o paketin `dev`
script'i olarak kalabilir. Aynı şekilde OpenUI kütüphanesi `packages/genui`
olacak (web onu import edecek), `apps/openui` ise tezgâh olarak kalır.

## Bağımlılık yönü

```
apps/*  →  ui-web / ui-native  →  tokens
   ↓
domain · api-client · contracts        ← React yok, DOM yok, Node yok
```

Üç kural — **dokümanda değil, lint'te**
(`packages/eslint-config/boundaries.js`):

1. `packages/*` → `apps/*` import edemez. Paket tüketicisine bağımlı olursa
   ikinci bir uygulama onu alamaz.
2. App → app import edemez. `../../web/src/...` gibi göreli sıçramalar build
   sınırını deler.
3. `contracts` ve `domain` platform API'si tanımaz. Mobil bu ikisini birebir
   alacak; içine `window` girdiği an alamaz.

`api-client` 3. kuralın **dışında**, bilerek: bir taşıma katmanı, tarayıcı
API'lerine erişmesi meşru. Platformdan bağımsız olması gereken paketler
`platform-free` ESLint katmanını açıkça seçer.

> ESLint `files` globlarını çalıştığı dizine göre çözer. Her paket kendi
> dizininde lint olduğu için kök-göreli desenler (`packages/domain/**`)
> **sessizce hiçbir şeyle eşleşmez**. Bu yüzden kurallar filtre değil,
> opt-in katman. Kural eklerken bunu doğrula: bozuk bir dosya enjekte et,
> lint'in patladığını gör.

## Paketler build edilmez ("JIT paket")

Paketler ham TypeScript dışa aktarır; derlemeyi tüketen Next uygulaması
yapar (`transpilePackages`). Bu yüzden paket build'lerini sıraya dizen bir
orkestrasyon yok ve pakete yapılan düzenleme dev'de anında görünür.

Derlenmiş çıktıya geçmek gerekirse (RN Metro bazı durumlarda ister) `exports`
alanı `dist`'e yönlendirilir ve pakete `build` görevi eklenir; turbo grafiği
zaten `dependsOn: ["^build"]` ile hazır.

## On-prem kısıtları

dima kurumsal müşterinin kendi altyapısına kuruluyor. Yapıyı etkileyenler:

| kural | nerede karşılığı var |
|---|---|
| **Build sırdan bağımsız olmalı** | CI hiçbir anahtar vermez; `apps/openui` istemcisi istek başına kurulur, modül seviyesinde değil |
| **Config build'e gömülmez** | `NEXT_PUBLIC_*` build'e **inline** olur → `turbo.json`'da build `env`'inde (cache'i düşürsün diye). `BACKEND_ORIGIN` runtime → `globalPassThroughEnv` |
| **Egress yok (air-gap)** | Ürün tarafında dış çağrı yok. Tüm dış URL'ler ve Resend **marketing**'te — bu yüzden marketing ayrı bir app olmalı, on-prem imajına girmemeli |
| **Sağlayıcı değiştirilebilir** | `OPENAI_BASE_URL` ile Azure OpenAI / vLLM / Ollama |
| **Backend adresi runtime'da** | `configureApiClient({ baseURL })` |

## Açık kararlar

Bilinçli olarak çözülmedi — yeri belli, zamanı değil:

- ~~`contracts` elle senkron.~~ **Çözüldü** — bkz. aşağıdaki bölüm.
- **Masaüstü refresh token.** Bugün HTTP-only cookie — tarayıcıda doğru olan
  bu. Tauri/Electron'da same-origin sunucu olmadığı için cookie kurulamaz;
  OS anahtarlığına geçmesi gerekecek. Değişecek yer `api-client`'ın
  `doRefresh()`'i. Erişim token'ı her platformda bellekte, localStorage'a asla.
- **`apps/marketing` ayrımı.** Yukarıdaki air-gap gerekçesiyle en yakın adım.
- **`packages/tokens`.** Tokenlar şu an `globals.css`'te 131 CSS değişkeni.
  React Native CSS değişkeni okuyamaz; mobil geldiğinde kaynak JS olup CSS'i
  **üretmeli**. Şimdi JS token dosyası açmak ikinci bir doğruluk kaynağı
  yaratır — mobil gelene kadar yapılmayacak.
- **`ui-web`.** `components/ui/` altındaki shadcn primitifleri bizim
  düzenlediğimiz dosyalar; paket yapılırsa her küçük düzenleme paketler arası
  değişikliğe döner. İkinci gerçek tüketici (desktop/storybook) çıkınca.

## Sözleşme üretimi (`packages/contracts`)

Tipler artık backend'in `app/schemas.py`'sinden üretiliyor:

```bash
DIMA_BACKEND_PATH=../../backend bun run --filter @dima/contracts codegen
# ya da backend çalışıyorsa:
DIMA_BACKEND_URL=http://localhost:8000 bun run --filter @dima/contracts codegen
```

Backend yolu **açıkça verilir**, varsayılan yok: komşu bir çalışma ağacının
hangi dalda olduğu bilinemez ve eski bir kopyadan üretmek sözleşmeyi geriye
alır.

**Tüm app import edilmez.** `from app.main import app` FastAPI'nin tam
belgesini verirdi ama sqlmodel/DB katmanını da çeker. `app/schemas.py` yalnız
pydantic'e bağlı ve sözleşme yüzeyi zaten orada.

**Codegen ancak backend'in tiplediği kadar iyi.** Backend `kpi`,
`interpretation`, `cube_query`, `rows`, `cubes` alanlarını `dict[str, Any]`
bırakıyor; openapi-typescript bunları `Record<string, never>` — yani "hiç
anahtar kabul etmeyen nesne" — olarak üretiyor. Bu işe yaramaz değil,
**zararlı**: daraltmasak `rows[0].ay` derlenmezdi. Bu yüzden:

| dosya | ne | kim yazar |
|---|---|---|
| `src/generated.ts` | yapı | codegen — elle düzenlenmez |
| `src/types.ts` | `dict[str, Any]` alanlarının kullanılabilir şekilleri | elle |
| `src/index.ts` | ikisini birleştiren daraltmalar | elle |

Backend bir alanı düzgün tiplediği gün, `types.ts`'teki karşılığı ve
`index.ts`'teki daraltma **silinir**.

**İstek/yanıt ayrımı.** openapi-typescript varsayılanı olan alanları zorunlu
üretir. Bu *yanıtlar* için doğru (sunucu Pydantic varsayılanını da serileştirir)
ama *istekler* için yanlış (istemci atlar, sunucu doldurur). `index.ts`'teki
`RequestOf<>` bunu düzeltir.

**Kayma denetimi iki kademeli** (`codegen:check`):

1. Backend erişilebilirse — commit'lenmiş şema backend'le uyuşuyor mu? Asıl
   kontrol bu.
2. Erişilemiyorsa (CI) — commit'lenmiş şemadan üretilen TS, commit'lenmiş TS
   ile aynı mı? Backend kaymasını göremez, ama `generated.ts`'in elle
   düzenlenmiş olmasını yakalar. Neyi **kapsamadığını** açıkça yazdırır;
   sessizce geçen bir kontrol, olmayan kontrolden kötüdür.

## Komutlar

```bash
bun install
bun run dev         # tüm app'ler (web :3000, openui :3001)
bun run build
bun run lint
bun run typecheck
bun run test
```

Tek pakete: `bunx turbo run dev --filter @dima/web`
