# PLAN ÜRETİM ÖLÇÜMÜ — sözleşme düzeltmesinin öncesi/sonrası (2026-08-09)

> Alet: `lab/plan_uretimi.py` (**motorsuz**) · payda **8** kök-neden/rapor sondası ·
> sağlayıcı `openrouter/deepseek-v4-flash`

| | önce | **sonra** |
|---|---|---|
| istem uzunluğu | 2 111 | **3 336** |
| tarifi eksik fiil | 🔴 **6/15** | **0/15** |
| `AYRISTIR` kullanımı | 🔴 **0** | **2** |
| `HESAPLA` kullanımı | 1 | **2** |
| en uzun plan | 7 adım | **8 adım** |

## Düzeltmeden önce ne yanlıştı

İstem yalnız `- FİİL: anlam` yazıyordu; `olcu` · `hedef` · `deger` · `olculer` ·
`baslik` **bir kez bile** geçmiyordu. Model, kendisine hiç gösterilmemiş bir
sözleşmeye göre reddediliyordu. Ve reddedilen altı fiilden ikisi (`BAGLA`·`HESAPLA`)
kök-neden zincirinin **tam ortasındaydı**: sistem, en çok istediği zinciri üretmesi
**en zor** olan yerden tutuyordu.

Ayrıca `KIYASLA`·`AYRISTIR`·`TREND` **ulaşılamazdı**: gövdeleri `cube_query` okuyor,
şema yalnız `kaynak` veriyordu. Bu sütun (`fiil_kullanimi`) o üçünü **buldu**.

## Hâlâ hiç kullanılmayanlar — ve dürüst okuma

`KIYASLA` · `TREND` · `BOYUTSEC` · `MATRIS` · `GORSEL`

⚠ Bu **bir kusur kanıtı değil**: sonda kümesi kök-neden/rapor ağırlıklı; içinde
*«geçen yıla göre»* (TREND), *«yan yana koy»* (MATRIS) ya da *«grafiğe çevir»*
(GORSEL) isteyen soru **yok**. `KIYASLA`'nın yerini de `HESAPLA` dolduruyor —
ikisi akraba.

🔴 Sıradaki iş bu yüzden **sonda kümesini genişletmek**, fiili savunmak değil:
*hiç kullanılmayan bir fiil ya gereksizdir ya anlatılmamıştır — ve üçüncü bir
ihtimal daha var: hiç sorulmamıştır.* Ölçüm aracının paydası, ölçtüğü şeyin
kapsamını belirler.

## Aletin kendi sınırı — yazılı

Bu alet **planın kurulabildiğini** ölçer, **doğru** olduğunu değil. Bir plan
şema-geçerli olup yanlış boyutu kırabilir. Doğruluk ölçümü ayrı bir iştir ve
`§AA1` denkliği (aynı soruya plan yoluyla **birebir aynı** cevap) bu turun
sıradaki maddesidir.
