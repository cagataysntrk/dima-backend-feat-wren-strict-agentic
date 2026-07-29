# dima Marketing Site Implementation Pack

**Hazırlanma tarihi:** 26 Temmuz 2026  
**Hedef repo:** `UpcyTech/dima-frontend`  
**Çalışma modeli:** Stage-by-stage, her aşama bağımsız doğrulanabilir  
**Referans repo:** `UpcyTech/upcyman`  
**Yerel, salt-okunur referans yolu:** `/Users/enesteve/Desktop/Coding/Upcy/upcyman/upcyman`

Bu paket, `dima-frontend` içinde profesyonel bir B2B SaaS / AI analytics marketing sitesi kurmak için hazırlanmış araştırma, mimari karar, içerik stratejisi, tasarım sistemi ve uygulama prompt setidir.

## Önerilen kullanım

1. Önce `DIMA_MARKETING_MASTER_PLAN.md` dosyasını okuyun.
2. AI coding agent oturumunun başında `MASTER_PROMPT.md` içeriğini verin.
3. Ardından yalnızca çalışılacak stage dosyasını verin.
4. Agent bir stage'i bitirmeden sonraki stage'e geçmesin.
5. Her stage sonunda `pnpm lint`, `pnpm build` ve ilgili testler çalıştırılsın.
6. Her stage ayrı commit veya ayrı PR olarak tutulabilsin; ancak agent kullanıcı açıkça istemedikçe commit/push yapmasın.

## Dosya haritası

| Dosya | Amaç |
|---|---|
| `00_RESEARCH_SYNTHESIS.md` | Repo ve internet araştırmasının sentezi |
| `01_REPOSITORY_ARCHITECTURE_AUDIT.md` | Mevcut teknik yapı, riskler ve korunacak sınırlar |
| `02_POSITIONING_AND_CLAIMS.md` | Mesajlaşma, ürün vaadi ve iddia doğruluk matrisi |
| `03_INFORMATION_ARCHITECTURE_AND_CONTENT.md` | Sayfa haritası, navigasyon ve içerik sistemi |
| `04_DESIGN_SYSTEM_DIRECTION.md` | Dima'ya özgü görsel dil ve UpcyMan'den alınacak dersler |
| `05_TARGET_TECHNICAL_ARCHITECTURE.md` | Route groups, provider ayrımı, auth ve SEO mimarisi |
| `06_QUALITY_SECURITY_SEO.md` | Erişilebilirlik, performans, test, güvenlik ve SEO kapıları |
| `MASTER_PROMPT.md` | Tüm oturumlarda kullanılacak ana agent talimatı |
| `AGENT_RUNBOOK.md` | Agent çalışma protokolü ve stage teslim formatı |
| `SOURCE_MAP.md` | İncelenen kaynaklar ve doğrulama haritası |
| `stages/` | Uygulama aşamalarının bağımsız prompt dosyaları |

## Stage sırası

0. Preflight ve repo audit
1. Route mimarisi ve auth sınırları
2. Marketing design system
3. Ortak marketing shell
4. Homepage
5. Product + How It Works
6. Solutions + Textile/Dyehouse vertical
7. Security + Integrations + Trust
8. Company + Resources + Legal + Contact
9. SEO + Analytics + Performance + Accessibility
10. Testing + Release + Handoff

## Temel karar özeti

- Marketing ana sayfası `/` olacaktır.
- Mevcut authenticated ürün arayüzü `/app` altına taşınacaktır.
- Marketing, product ve auth route'ları aynı projede fakat ayrı route group/layout sınırlarında tutulacaktır.
- Mevcut API, auth, refresh-cookie, tenant, konuşma ve rapor business logic'i yeniden yazılmayacaktır.
- Marketing sayfaları server-first olacaktır; yalnızca gerçekten etkileşim gereken küçük adalar client component olacaktır.
- UpcyMan kodu doğrudan dependency, symlink veya cross-repo import olarak kullanılmayacaktır. Yalnızca tasarım/composition referansı olarak okunacaktır.
- Sahte logo, sahte müşteri sayısı, sahte testimonial, sahte güvenlik sertifikası, kesinleşmemiş fiyat veya roadmap özelliğini “hazır” gösteren iddia kullanılmayacaktır.
- Dima'nın ayırt edici anlatısı: **LLM önerir; modellenmiş semantik katman ve doğrulama motoru karar verir.**
