/**
 * Generative pano katmanı — PLATFORMDAN BAĞIMSIZ kısım.
 *
 * Burada React, DOM ve OpenUI YOK. Sebep: katalog kuralları ve kompozisyon
 * mantığı web'de, mobilde ve masaüstünde AYNI olmalı. Aynı sohbetten iki
 * platformda farklı pano çıkması, iki ayrı `compose()` tutmanın kaçınılmaz
 * sonucu olurdu.
 *
 * Renderer'lar platforma özgüdür ve paylaşılmazlar — web tarafı
 * `apps/web/src/components/genui/` altında.
 */

export { catalogEntries, catalogSummary, shapeOf } from "./catalog";
export type { CatalogEntry, EntryShape } from "./catalog";

export { composeDashboard } from "./compose";
export type { ComposeOptions } from "./compose";

export { DASHBOARD_ROOT, dashboardPromptOptions } from "./prompt";
