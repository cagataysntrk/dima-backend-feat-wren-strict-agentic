# CEO demo — eksik backend sözleşmesi

`Dima-Tekstil-CEO-Demo-Senaryolari.pdf` (63 senaryo, D1–D63) için gereken ama
`dima-backend` HEAD'de **bulunmayan** uçların sözleşmesi.

Bu dosya frontend'in **bağlanacağı şekli** sabitler. Amaç, iki tarafın aynı
sözleşmeyi ayrı ayrı icat etmemesi: ekranlar buradaki tiplere göre yazıldı,
backend de bunlara göre yazılırsa entegrasyon "derlendi, çalıştı" olur.

## Yöntem

Mevcut zincir korunur — sapma yok:

```
app/schemas.py (Pydantic)
  → bun run --filter @dima/contracts codegen   (openapi.json)
  → packages/contracts/src/generated.ts
```

`dict[str, Any]` bırakılan alanlar `packages/contracts/src/types.ts`'te elle
daraltılır (bugün `CubeQuery`, `Interpretation`, `KpiCard` böyle).

**Bayrak zorunlu.** Her yeni yetenek `app/features.py › FLAG_REGISTRY` +
`demo/packs/features.yml` üzerinden `beta` ile gelir; frontend `useFeature` ile
geçitler. Bayrak kapalıyken uç hiç çağrılmaz, ekran hiç çizilmez.

---

## 1. Rapor üretimi — capability [2]

**Senaryolar:** D12 (haftalık üretim özeti) · D17 (aynı rapor İngilizce) ·
D28 (aylık sürdürülebilirlik özeti) · D34 (2 sayfalık yönetim raporu, yorumlu) ·
D42 (karbon envanteri taslağı) · D48 (CBAM gömülü emisyon) · D53 (yönetim kurulu
memosu) · D62 (oturum sentezi — "CEO Günlüğü")

**Bayrak:** `rapor_uretimi`

```python
class ReportRequest(BaseModel):
    """Rapor üretimi (D12/D34/D62). Şablon + kapsam; içerik DETERMİNİSTİK
    hesaplanır, dil katmanı yalnız cümleye çevirir."""
    template: str                          # uretim_ozeti | surdurulebilirlik | yonetim | gunluk
    period: str | None = None              # göreli dönem ("geçen hafta") — koşumda çözülür
    locale: str = "tr"                     # D17: aynı rapor, başka dil
    session_id: str | None = None          # D62: oturum sentezi bu sohbetin bulgularından
    cube_queries: list[dict[str, Any]] = Field(default_factory=list)


class ReportSection(BaseModel):
    """Rapor bölümü. `result` varsa FE mevcut <ResultView> ile çizer — yeni bir
    render yolu AÇILMAZ. `commentary` LLM'den gelebilir ama AYRI alanda durur:
    ekranda "yorumdur" etiketiyle işaretlenir (D34 açık şartı)."""
    title: str
    body: str | None = None                # deterministik metin (sayılar buradan)
    commentary: str | None = None          # LLM yorumu — etiketlenir, sayı İÇERMEZ
    result: QueryResult | None = None
    cube_query: dict[str, Any] | None = None
    view_hint: str | None = None


class ReportResponse(BaseModel):
    title: str
    period_resolved: str | None = None     # "1–7 Tem 2026" — neyin raporu olduğu belli olsun
    sections: list[ReportSection]
    contract_id: str | None = None         # kanıt kaydı (D49: her sayı bağlantılı)
    generated_at: str
```

`POST /report` → `ReportResponse` · izin `query:run`

> **Neden `commentary` ayrı alan:** D34 "sayılar altın yoldan, dil LLM'den;
> yorumların yanında 'yorumdur' etiketi" diyor. Tek bir `markdown` alanı
> döndürürsek bu ayrım kaybolur ve rapor "modelin yazdığı bir şey" olur —
> ürünün tüm iddiası bunun tersi.

---

## 2. Hafıza / tercihler — layer [M]

**Senaryolar:** D30 ("bundan sonra aralık söylemezsem son 30 günü al, tutarları €
göster") · D58 ("her pazartesi bana nasıl bir özet vermelisin?") · D11 (bağlam)

**Bayrak:** `hafiza`

```python
class Preference(BaseModel):
    """Kullanıcının SÖZLE kurduğu kalıcı tercih. `scope` neyi etkilediğini söyler;
    `value` deterministik olarak uygulanır (LLM her seferinde yeniden yorumlamaz)."""
    id: str
    scope: str          # default_period | currency | granularity | summary_style
    value: str          # "son 30 gün" | "EUR" | "week" | ...
    source_question: str            # tercihin doğduğu cümle — geri alınabilir olsun
    created_at: str


class PreferencesResponse(BaseModel):
    preferences: list[Preference]
```

- `GET /preferences` → `PreferencesResponse`
- `POST /preferences` `{scope, value, source_question}` → `Preference`
- `DELETE /preferences/{id}` → `{removed: bool}`

Ayrıca `AskResponse`'a **bir alan** eklenir:

```python
    applied_preferences: list[str] = Field(default_factory=list)  # ["son 30 gün", "EUR"]
```

> **Neden yanıtta geri bildirilir:** D30'un "vay" anı, tercihin **sessizce
> uygulandığını CEO'nun fark etmesi**. Sessizce uygulayıp hiç söylemezsek bu sefer
> de "neden bu tarih aralığı?" sorusu doğar. Uygulanan tercih cevapta rozet olarak
> görünmeli — hem sihir hem denetlenebilirlik.

---

## 3. Analist — layer [+]

**Senaryolar:** D43 (çeyrek karnesi) · D44 (veriye dayalı SWOT) · D47
(karbon-başabaş OEE) · D50 (müşteri büyütme skoru) · D54 (kestirimci bakım) ·
D59 (ihracat riski) · D61 (OEE artırma planı) · D63 (final: "önce neyi
düzeltirdin?")

**Bayrak:** `analist`

```python
class AnalysisClaim(BaseModel):
    """Analizin TEK bir iddiası. Her iddia kanıta bağlıdır: `evidence` o iddiayı
    üreten cube_query'dir → FE tıklanır yapar, kullanıcı sayıya iner (D44 şartı:
    'her maddeyi sayıya bağla', D49: 'her sayı kanıt bağlantılı')."""
    text: str
    kind: str                              # strength | weakness | opportunity | threat | action
    metric: str | None = None
    value: float | None = None
    unit: str | None = None
    evidence: dict[str, Any] | None = None # cube_query — tıklanınca /cube ile koşar
    confidence: str = "deterministic"      # deterministic | estimated | model


class AnalysisResponse(BaseModel):
    kind: str                              # swot | scorecard | plan | risk | breakeven
    title: str
    summary: str
    claims: list[AnalysisClaim]
    # ❗ D45/D46/D52 dürüstlük şartı: tahmin/projeksiyon içeren analizler
    # parametrelerini AÇIKÇA taşır (referans.xlsx'ten), böylece "uydurmuyor".
    assumptions: list[str] = Field(default_factory=list)
    contract_id: str | None = None
```

`POST /analysis` `{kind, period?, session_id?, cube_queries?}` → `AnalysisResponse`
· izin `query:run`

> **`confidence` ve `assumptions` pazarlık konusu değil.** PDF'in *dürüstlük
> listesi* açıkça diyor: D45 (projeksiyon), D46 (tahmin), D52 (what-if) ya referans
> parametrelerle deterministik ön-pişirilir ya da "yol haritası" diye sunulur —
> **demoda asla canlı LLM'e serbest tahmin yaptırılmaz**. Bu iki alan o kuralı
> sözleşmeye gömer: parametresiz bir tahmin dönemez.

---

## 4. Cümleden pano — capability [3]

**Senaryolar:** D19 ("panoya bugünkü ciro, OEE ve RFT kartlarını ekle; adı 'Genel
Bakış' olsun") · D29 ("bir 'Üretim' panosu kur: OEE trendi, duruş paretosu,
vardiya kıyası, günlük üretim sayacı") · D35 (sürdürülebilirlik panosu)

**Bayrak:** mevcut `dashboards`

```python
class DashboardComposeRequest(BaseModel):
    """Tek cümleden ÇOK KAROLU pano. Karolar deterministik çözülür: cümledeki her
    metrik katalogda bir cube_query'ye eşlenir."""
    instruction: str                       # "ciro, OEE ve RFT kartları; adı Genel Bakış"
    session_id: str | None = None


class DashboardComposeResponse(BaseModel):
    title: str
    widgets: list[dict[str, Any]]          # WidgetCreate şekli — mevcut /dashboards/{id}/widgets ile aynı
    unresolved: list[str] = Field(default_factory=list)  # eşlenemeyen metrikler
```

`POST /dashboards/compose` → `DashboardComposeResponse`

> `unresolved` şart: "RFT" katalogda yoksa pano sessizce 2 karoyla gelmemeli.
> Eşlenemeyeni söylemek, D20'nin ("verinizde yok; uydurmam") aynı dürüstlüğü.

---

## Öncelik

20 dakikalık omurga (`D1 → D3–D5 → D8 → D11 → D16 → D19 → D30 → D32 → D44 → D47
→ D60 → D63`) için gereken sıra:

| # | uç | omurgada karşılığı |
|---|---|---|
| 1 | `POST /analysis` | D44 (SWOT), D47 (karbon-başabaş), D63 (final) — omurganın 3 maddesi |
| 2 | `GET/POST /preferences` + `applied_preferences` | D30 |
| 3 | `POST /dashboards/compose` | D19 |
| 4 | `POST /report` | omurgada değil ama Seviye 1–2'nin 8 senaryosu |

## Frontend tarafı

Bu uçlar gelene kadar ekranlar **bayrak arkasında karanlık** durur ve
bağlanmadığını dürüstçe söyler — boş bir panel "veri yok" demez, "bu yetenek
henüz bağlı değil" der. Sahte çıktı üretilmez.
