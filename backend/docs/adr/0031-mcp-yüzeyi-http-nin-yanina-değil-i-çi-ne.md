# ADR-0031 — **MCP yüzeyi** — HTTP'nin YANINA değil İÇİNE

**Durum:** kabul edildi · **Faz:** FAZ 4.5 · **Yazıldığı gün:** karar ile aynı tur @`312b8d3`

> ## ✅ BU KARAR **GÜNÜ YAZILDI** — rekonstrüksiyon DEĞİL
>
> `ADR-0003…0024` **rekonstrüksiyondur** (kararlar alındığı gün yazılmamıştı, atıf
> bağlamlarından türetildi). **Bu dosya öyle değil:** karar `FAZ 4.5` ile inerken, aynı
> turda, kararı veren kodun yanında yazıldı (@`312b8d3`).
>
> ⚠ Fark önemlidir ve **karıştırılmamalıdır**: bir rekonstrüksiyonun başlıkları alıntı
> değildir ve *"kod bugün şöyle davranıyor"* diye okunur; bu dosya ise **kararın
> kendisidir**. Yine de çelişkide **kod kazanır** — çünkü karar yaşayan koddur, onun
> kaydı değil.
>
> 🔴 **Denetim bulgusu (2026-08-05):** *"en yüksek numaralı karardan sonra inen
> faz-düzeyi kararların hiçbirinin kaydı yok — kayıt kodun ~2 faz gerisinde."* Bu dosya
> o boşluğun bir satırını kapatır.


## Bağlam

MCP kararlı spec'e ulaştı ve rakipler kendi sunucularını yayımlıyor — *“ajanına bağlan”* artık bir farklılaşma değil, bir **giriş bileti**. `app/tools.py`'nin kendi notu zaten şunu diyordu: *“MCP adaptörü — ileride ince bir çevirici; kendi kaydını KURMAZ.”*

## Karar

MCP **ince bir çeviricidir**: `tools.llm_araclari()`'yi ve `authorize()` süzgecini okur, **ikinci bir kayıt kurmaz**. 🔴 **Değişmez:** MCP'den çağrılan araç `Planlayici.calistir()`'in **aynı dört kapısından** geçer (`KAYIT · yetki · deterministik-önce · bütçe`) ve **aynı makbuzu** üretir.

## Sonuçlar

- Fark, jenerik MCP sunucularında **olmayan** şey: her çağrı bir **makbuz** üretir. *Bir ajan sayıyı alıp nereden geldiğini bilmiyorsa, o sayı kanıtsızdır.*
- ⚠ `importlib`/`arac.cagir`/`authorize.can` MCP tarafında **AST ile yasak** — aracı kendi çözen ya da yetkiyi kendi hesaplayan bir yol kapıları atlardı.

## Kanıt — **tek doğrulama yolu**

- `app/mcp.py`
- `app/routers/mcp.py`
- `tests/test_mcp.py`

> Bu dosya ile kod çeliştiğinde **kod kazanır**: karar yaşayan koddur, onun kaydı değil.
