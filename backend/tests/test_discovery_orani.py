"""FAZ O-9 — DISCOVERY ORANI ALETİNİN KAPISI.

Bu aletin **kendisi** bir ölçüttür; kusuru bir sayıyı yanlış yapar ve o sayıya bakılarak
faz kararı verilir. En pahalı iki kusuru burada kapatılıyor: **payda kayması** ve
**ad-hoc'un cube sayılması**.
"""

from __future__ import annotations

import json

from lab import discovery_orani as D


def test_ADHOC_CUBE_SAYILMAZ():
    """🔴 Rozet dürüstlüğü — veri incelenmemiş LLM SQL'inden türemişse `cube` değildir.

    ⚠ Sıra kritik: `adhoc` kontrolü `cube`den ÖNCE olmazsa arıza raporu görünmez olur.
    """
    assert D.sinifla({"source": "cube", "cube_query": {"cube": "adhoc"}}) == D.SINIF_ADHOC
    assert D.sinifla({"source": "cube", "cube_query": {"cube": "oee"}}) == D.SINIF_CUBE


def test_MERDIVEN_BASAMAKLARI_AYRIK():
    assert D.sinifla({"source": "cube+llm"}) == D.SINIF_GARSON
    assert D.sinifla({"source": "llm:gemini"}) == D.SINIF_DISCOVERY
    assert D.sinifla({"source": None}) == D.SINIF_CEVAPSIZ


def test_ARIZA_ORANI_UC_SINIFI_TOPLAR():
    """⊙ Cevapsızlık da bir arıza raporudur — yalnız *sessiz* olanı."""
    d = D.dagilim([{"source": "cube"}, {"source": "llm:x"},
                   {"source": None}, {"source": "cube+llm"}])
    assert d[D.SINIF_DISCOVERY] == 1 and d[D.SINIF_CEVAPSIZ] == 1
    assert D.oran(d) == 50.0


def test_BOZUK_SATIR_PAYDADAN_DUSMEZ(tmp_path):
    """🔴🔴 **PAYDA KUTSALDIR.** Sessizce düşen bir satır paydayı gizlice küçültür ve
    *«sistem bozulurken sayı iyileşir»* desenini üretir (ölçüldü: `gitas` 445→342)."""
    p = tmp_path / "t.jsonl"
    p.write_text(json.dumps({"source": "cube"}) + "\n{bozuk\n", encoding="utf-8")
    assert len(D.oku(p)) == 2, "bozuk satır atlandı — payda küçüldü"
    assert D.dagilim(D.oku(p))[D.SINIF_CEVAPSIZ] == 1


def test_ALET_ISTEK_ATMAZ():
    """⚠ Senaryolar `curl` ile koşulur (döngü kuralı); alet yalnız çıktıyı okur.
    *Ölçen ile ölçülenin aynı süreç olması, ikisinin de aynı arızaya düşmesi demektir.*"""
    kaynak = open(D.__file__, encoding="utf-8").read().split('"""')[-1]
    for yasak in ("requests", "httpx", "urlopen", "TestClient"):
        assert yasak not in kaynak, f"alet {yasak} ile istek atıyor"
