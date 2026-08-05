"""**Intent-JSON ŞEMA SÖZLEŞMESİ** — `CubeQuery`'nin şema-kısıtlı biçimi.
[bayrak: `sema_kisitli` — karar `cube_router`'da kalır]

## Neden `cube_router`'dan ÇIKTI

`cube_router.py` modül tavanını **8 satır** aşmıştı (1749 / 1741). Kapının kuralı açık:
*"yeni eşleştirme kuralı bir **modüle** çıkar; tavanı yükseltme. Tavanı yükseltmek kapıyı
kapının kendisiyle çürütür."*

Ve taşınacak şey **rastgele seçilmedi**: bu fonksiyon bir **yönlendirme kararı vermez**,
bir **veri sözleşmesi tarif eder** — kataloğun o anki hâlini bir JSON Schema'ya çevirir.
`cube_router` *"hangi cube, hangi ölçü"* sorusunun sahibidir; *"bir Intent-JSON nasıl
görünür"* sorusunun sahibi değildir. **Sınır kavramsaldı, dosya onu geç yakaladı.**

⚠ **Şemanın ÜRETİLMESİ buraya taşındı, KULLANILMASI değil**: bayrak kontrolü ve reddetme
yolu (`parse_cube_query`) `cube_router`'da kaldı. *Bir kararı taşımak, onu bölmekten
farklıdır.*
"""

from __future__ import annotations

_GRAN_ENUM = ["year", "quarter", "month", "week", "day"]


def cube_query_json_schema(index: dict) -> dict:
    """FAZ 3a — CubeQuery'nin ŞEMA-KISITLI biçimi: adlar o ANKİ kataloğun **enum**'u.

    ## Neden (plan §4.6b-C)

    Bugünkü akış *"serbest JSON iste, sonra `parse_cube_query` ile REDDET"*. Reddedilen
    her sorgu bir Discovery'ye düşüştür — yani kayıp, hatanın **sonrasında** kapatılıyor.
    Bu şema hatayı **öncesinde** engellemeyi hedefler: model geçersiz bir ad üretmek için
    şemanın dışına çıkmak zorunda kalır.

    ## Kritik tasarım: enum CUBE'A GÖRE DARALIR

    Düz bir `{"measures": {"enum": [tüm 81 ölçü]}}` **çapraz sızıntı** üretirdi: model
    `parti` cube'unu seçip `oee`'nin ölçüsünü isteyebilirdi — yapısal olarak "geçerli",
    semantik olarak saçma, ve `parse_cube_query` yine reddederdi. Yani kısıt hiçbir işe
    yaramazdı. Bu yüzden `oneOf`: **her cube kendi dalını taşır** ve o dalda yalnız
    KENDİ ölçü/boyut/zaman adları listelenir.

    ## REDDETME YOLU KORUNUR — en önemli madde

    İlk dal `{"cube": null}`. Şema-kısıtlı çıktının klasik tuzağı, modeli **geçerli ama
    yanlış** bir seçime ZORLAMAKtır: seçenekler arasında "hiçbiri" yoksa model illa
    birini seçer. Bu, sistemin en pahalı hata sınıfını (§6.1 sessiz-yanlış) üretirdi.
    Bugünkü prompt zaten *"yanıtlanamıyorsa KESİNLİKLE {cube:null} döndür"* diyor; şema
    bunu **yapısal** hale getirir, gevşetmez.

    ## Kapsam: YALNIZ BEŞ ÇEKİRDEK ALAN

    `order`/`limit`/`blend` **bilerek dışarıda** — `parse_cube_query` onları zaten
    hoşgörüyle **sessizce düşürüyor** (geçersiz değer sorguyu öldürmüyor), dolayısıyla
    enum'lamak kazanç getirmez, yalnız şemayı büyütür.
    """
    dallar: list[dict] = [{
        "type": "object",
        "title": "cevaplanamaz",
        "description": "Soru TEK bir cube ile yanıtlanamıyorsa (liste, çapraz-cube, "
                       "tanımsız) BU dal seçilir. Tahmin etmek yerine reddetmek doğrudur.",
        "properties": {"cube": {"type": "null"}},
        "required": ["cube"],
        "additionalProperties": False,
    }]
    for ad, spec in (index or {}).items():
        olculer = list(spec.get("measures") or [])
        boyutlar = list(spec.get("dimensions") or [])
        zamanlar = list(spec.get("time_dimensions") or [])
        if not olculer:
            continue  # ölçüsüz cube sorgulanamaz — dal açmak yanlış seçenek sunardı
        props: dict = {
            "cube": {"const": ad},
            "measures": {"type": "array", "minItems": 1,
                         "items": {"type": "string", "enum": olculer}},
        }
        if boyutlar:
            props["dimensions"] = {"type": "array",
                                   "items": {"type": "string", "enum": boyutlar}}
        if zamanlar:
            props["timeDimensions"] = {
                "type": "array",
                "items": {"type": "object", "additionalProperties": False,
                          "properties": {
                              "dimension": {"type": "string", "enum": zamanlar},
                              "granularity": {"type": "string", "enum": _GRAN_ENUM}},
                          "required": ["dimension", "granularity"]}}
        if boyutlar:
            props["filters"] = {
                "type": "array",
                "items": {"type": "object", "additionalProperties": False,
                          "properties": {
                              "dimension": {"type": "string", "enum": boyutlar},
                              "operator": {"type": "string",
                                           "enum": ["eq", "ne", "gt", "gte", "lt", "lte", "in"]},
                              "value": {}},
                          "required": ["dimension", "operator", "value"]}}
        dallar.append({"type": "object", "title": ad,
                       "properties": props, "required": ["cube", "measures"],
                       "additionalProperties": False})
    return {"type": "object", "oneOf": dallar}
