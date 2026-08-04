"""Kullanıcının iddiasını ÜRETMEYE çalış: «sinonim önerisi yüzünden hiçbir şeyi anlamıyor».

Korpus soruları KATALOGDAN üretiliyor — yani hepsi DOĞRU YAZILMIŞ. Bu betik tam tersini
sorar: gerçek insanın yazdığı gibi, biraz hatalı/gündelik Türkçe.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import tests.conftest as _conf  # noqa: E402,F401
from tests.conftest import make_tenant_user  # noqa: E402

SORULAR = [
    # (soru, kullanıcının beklentisi)
    ("bu yıl fire ne kadar arttı", "fire trendi"),
    ("bu yil fire ne kadar artti", "fire trendi (şapkasız/noktasız)"),
    ("ocak ile haziran arasında makine bazında fire değişimi", "kıyas"),
    ("geçen ay ciro", "ciro"),
    ("gecen ay ciro", "ciro (noktasız)"),
    ("bu yıl toplam fire kg", "fire"),
    ("makinalara göre fire", "kırılım (makina/makine)"),
    ("en çok fire veren makine", "top-N"),
    ("bu ay kaç parti işledik", "sayım"),
    ("bu yıl bakiye", "bakiye"),
    ("fire orani nedir", "oran"),
    ("bu sene ne kadar sattık", "ciro (gündelik)"),
]


def main() -> int:
    import sys as _s
    _s.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from lab.nl_accuracy import _client

    c = _client("owner@dima.local", "owner-parola-123", None)
    try:
        sayac = {"cevap": 0, "typo": 0, "netlestirme": 0, "bos": 0}
        for soru, beklenti in SORULAR:
            d = c.post("/ask", json={"question": soru, "execute": False}).json()
            cq = d.get("cube_query") or {}
            note = (d.get("note") or "").strip()
            if d.get("sql") or cq.get("cube"):
                sinif = "✅ CEVAP"
                sayac["cevap"] += 1
                ek = f"{cq.get('cube')}·{(cq.get('measures') or ['—'])[0]}"
            elif "demek istedin" in note:
                sinif = "🔴 TYPO-ÖNERİSİ"
                sayac["typo"] += 1
                ek = note[:60]
            elif note:
                sinif = "◐ NETLEŞTİRME"
                sayac["netlestirme"] += 1
                ek = note[:60]
            else:
                sinif = "⊘ BOŞ"
                sayac["bos"] += 1
                ek = ""
            print(f"{sinif:16} {soru!r:52} → {ek}")
        print()
        print(f"TOPLAM {len(SORULAR)}: cevap={sayac['cevap']} · "
              f"TYPO-ÖNERİSİ={sayac['typo']} · netleştirme={sayac['netlestirme']} · "
              f"boş={sayac['bos']}")
    finally:
        c.__exit__(None, None, None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
