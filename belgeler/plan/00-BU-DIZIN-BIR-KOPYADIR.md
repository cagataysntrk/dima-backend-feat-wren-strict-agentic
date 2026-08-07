# ✅ BU DİZİN ARTIK **KAYNAKTIR** — kopya değil

> ⚠ **Dosya adı bilerek değiştirilmedi.** Bir gün *"kopyadır"* diyordu; bugün kaynak.
> Adı korumak, bu geçişin **olduğunu** görünür bırakır — ve bu depoda kural şudur:
> *kapananlar işaretlenir, silinmez.*

## Bugünkü durum

| belge | rol |
|---|---|
| `DIMA-GARSON-ARA-FAZ.md` | garson ara fazının **tek** planı |
| `DIMA-V1-YOL-HARITASI.md` | v1'in **tek** yol haritası |

`~/.claude/plans/` altındaki eski dosyalar **silinmedi**, birer **yönlendirmeye**
çevrildi: o yola mutlak yolla işaret eden eski bir atıf ya da bağlamı sıfırlanmış bir
ajan, boşluk yerine **adres** bulsun diye.

## Neden taşındı — iki ölçülmüş risk

**1 · Sürüm bağı yoktu.** Kod bir commit'te ilerlerken plan başka bir zamandaydı; *"bu
kod hangi plana göre yazıldı"* sorusu **sorulamıyordu**. Artık plan da commit'lerle
birlikte geziyor: `git log belgeler/plan/` planın kendi tarihini verir.

**2 · Kopya, iki sahip demektir.** Bir süre hem `~/.claude/plans/` hem `belgeler/plan/`
altında iki nüsha vardı. Kopya, kaynak güncellenince **sessizce** bayatlar — ve bayat bir
plan, olmayan bir plandan **daha kötüdür**: bağlamı sıfırlanan bir ajan onu okur, güvenir
ve **yanlış fazdan** devam eder. Bu depoda o kusur `OPERASYON-DURUM.md` başlığında **iki
kez** yaşandı.

> *İki gerçek, sıfır gerçekten kötüdür: sıfır gerçek arattırır, iki gerçek yanıltır.*

## Güncellenen atıflar

`backend/CLAUDE.md` · `OPERASYON.md` · `OPERASYON-DENETIM.md` ·
`belgeler/mimari/V1-MIMARI-HARITASI.md` — dördü de artık `belgeler/plan/`'a işaret ediyor.

⚠ **Tarihsel belgelere DOKUNULMADI** (`belgeler/denetim/*` · `belgeler/devir/*`): onlar
bir günün fotoğrafıdır ve o gün belge gerçekten oradaydı. Geçmişi bugünkü yola göre
düzeltmek, kaydı **yanlış** yapardı.

## Kapı

`backend/tests/test_plan_kopyasi_taze.py` — plan repoda mı, ve dışarıda **rakip bir
nüsha** kalmış mı diye bakar. *Bir taşımanın tamamlandığını, taşınan şeyin arkasında bir
şey kalmadığı kanıtlar.*
