"""🔴 `§54` — **BOŞ KUTU DA KONUŞUR** (`5.9`), ama motoru uyandırmadan.

## Ölçülen durum

| ölçüm | sonuç |
|---|---|
| `oneri.ara("")` | **0 aday** — ve bu **bilinçli** 🅡 |
| boş `q` ile `GET /oneri` | **0 cümle**: ekrandaki *«son bakılanlar»* tamamen `localStorage` |

İkincisi bir kusurdur: plan `5.9` çekirdek listeyi **motorda** istiyor, çünkü *«son
bakılanlar»* **kiracıya** göre değişir ve istemcide tutulursa çok kiracılı kurulumda
**yanlış** olur.

⚠ Ama birincisi bir karardır ve kapısı var (`test_bos_ve_ANLAMSIZ_girdi_PATLAMIYOR`:
*«typeahead her tuşta çağrılır; boş dize en sık gelen girdidir»*). Bu yüzden çekirdek
liste **uçta** kurulur — şemadan okunur, **hiçbir arama koşulmaz**. Motor susar, ürün
konuşur.

## 🅖 Yayına yazılan eksik: SIRA bir hiyerarşi DEĞİL

Bugünkü sıra **katalog sırasıdır**. Katalogda önem işareti aranmıştı ve **yok**:
`cekirdek_metrik` **hiçbir küpte dolu değil** (ölçüldü, 0/23). Doğru sıra **kullanım
sıklığından** gelmeli (`İŞ 6` · plan `5.5`) — o gelene kadar bu liste bir **başlangıçtır**,
bir öneri hiyerarşisi değil. *Bir sırayı ölçmeden koymak, ölçülmüş gibi görünen bir
sıra üretir* ㊱.
"""

from __future__ import annotations

from app import oneri


def test_BOS_GIRDI_CEKIRDEK_CUMLE_DONER(client):
    d = client.get("/oneri", params={"q": ""}).json()
    cumleler = d.get("oneriler") or []
    assert cumleler, "🔴 boş kutu sustu — `5.9` yine istemcide"
    assert len(cumleler) <= 5, f"🔴 çekirdek liste {len(cumleler)} satır — plan «5» diyor"


def test_CEKIRDEK_HER_SATIR_KOSULABILIR(client):
    """🆘 Cevaplanamayan bir öneri, tüketicisiz bir yetenektir: her satır sorgu taşımalı."""
    for o in (client.get("/oneri", params={"q": ""}).json().get("oneriler") or []):
        assert o.get("cube_query"), f"🔴 sorgusuz çekirdek satır: {o.get('metin')}"
        assert str(o.get("metin", "")).endswith("?"), (
            f"🔴 çekirdek satır tam cümle değil: {o.get('metin')} 🆡")


def test_ZIT_OLCUT_MOTOR_BOS_GIRDIDE_SUSAR(schema):
    """🆃 Kapının **kurbanı** da yazılır: motor boş girdide **hâlâ** hiçbir şey yapmamalı.

    Çekirdek listeyi `ara()`'ya taşımak kolay olurdu ve **yanlış** olurdu: en sık gelen
    istek için en pahalı yolu seçmek demekti. Bu yüklem o kısayolu kapatır.
    """
    assert oneri.ara("", schema, izinliler=None) == [], (
        "🔴 motor boş girdide çalışmaya başlamış — `5.9` yanlış katmana kondu 🆪")
