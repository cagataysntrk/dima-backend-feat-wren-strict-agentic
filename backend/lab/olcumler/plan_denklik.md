# DENKLİK ÖLÇÜMÜ — `O-13`, göçün kabul kapısı (2026-08-09)

> Alet: `lab/plan_denklik.py` · payda **5** · sağlayıcı `openrouter/deepseek-v4-flash`

## Sonuç

| ölçüm | sapma |
|---|---|
| **PLAN yolu** (k=3 oylama) | **0/5** |
| **TABAN** (`select_cube`, k=3 oylama) | **1/5** |
| ölçüt: `plan ≤ taban` | ✅ **GEÇTİ** |

Yani plan yolu, bugünkü yoldan **daha kararlı**. Beş sorunun beşinde `tek_adimli()`'nin
döndürdüğü `cube_query`, bugünkü `select_cube`'un ürettiğiyle **birebir aynı**.

## 🔴🔴 Ve buraya gelene kadar AYNI HATAYI İKİ KEZ YAPTIM

| # | hata | sonuç |
|---|---|---|
| 1 | Tabanı **ham tek çağrıyla** ölçtüm | Üretim `_select_consistent` ile **3 kez oyluyor** — ölçtüğüm yol üretimde **hiç koşmuyor** |
| 2 | Planı **tek çağrıyla**, tabanı oylamalı ölçtüm | *"Plan daha kararsız"* sonucu plandan değil **asimetriden** geliyordu |

⊙ İkisi de aynı kök: **iki şeyi karşılaştırırken birine verilen imkânın ötekine de
verilmesi.** *Yoksa ölçtüğün şey fark değil, ayrımcılıktır.*

🔴 Ve bu, `EE` turunun `-10` puanını da yeniden okutuyor: o koşumda plan ve
`select_cube` **bir aradaydı** ve oy iki dağılımdan besleniyordu. `-10` planları değil
**birlikteliği** yargılamıştı. Tam göç birlikteliği kaldırdı; sayı da düzeldi.

## Kapının bulduğu ve düzeltilen üç istem kusuru

| bulgu | kök |
|---|---|
| `period_expr` her sorguya kopyalanıyordu | 🔴 **işlenmiş örneğime** `"period_expr":"bu yıl"` yazmışım — *bir örnek bir tarif değil bir kalıptır* |
| sıralama/limit ayrı adım sanılıyordu | *«tek `SORGU` içindedir»* kuralı istemde yoktu |
| `cube: "uretim"` uyduruldu | *«SADECE listelenen adları kullan»* yoktu — *bir yasak, olumlu karşılığı yazılmadan yarım kalır* |

## Aletin sınırı — yazılı

Payda **5** ve bu bir bütçe: üretim yolu ölçümü soru başına **12** LLM çağrısı yapar
(iki taraf × iki koşum × k=3). Sekiz soru ölçümü 10 dakikanın üstüne çıkarıyordu ve o
noktada **ölçüm koşulmaz olur** — koşulmayan bir kapı, olmayan bir kapıdır.

⚠ Ve denklik **doğruluğu** ölçmez, **korunmayı** ölçer: plan bugünkü cevabı bozmuyor
demektir, bugünkü cevabın doğru olduğu demek değil.
