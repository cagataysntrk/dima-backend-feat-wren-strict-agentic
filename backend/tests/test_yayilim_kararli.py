"""🔴🔴 **MASKELEME SÜREÇLER ARASI KARARLI OLMALI.**

## Ölçülen kusur

`yayilim` sayı/boyut maskelemesi `sorted(set(...), key=len, reverse=True)` yapıyordu:
yalnız **uzunluğa** göre. Aynı uzunluktaki değerler `set`'in sırasında kalıyor ve
Python dizge hash'ini süreç başına rastgeleleştirdiği için (`PYTHONHASHSEED`) o sıra
her koşumda değişiyordu.

⊙ Kaset ıskası olarak ortaya çıktı — aynı kasetin **iki ardışık** oynatması `48` ve
`50` isabet verdi — ama zararı ölçümle sınırlı değildi: loglarda
`yayılım bozuldu: eksik:{{NUM_1}}` uyarısı zaten vardı, yani **kullanıcıya giden
anlatı** aynı soruda bazen düşüyordu.

*Kararsız bir sıralama, olmayan bir sıralama değildir — her koşumda başka bir
sıralamadır ve bu daha kötüdür: kusur ancak tekrarlandığında görünür.*
"""

from __future__ import annotations

import subprocess
import sys


_KOD = (
    "import sys; sys.path.insert(0,'/app');"
    "from app.yayilim import perdele;"
    "m,h = perdele(['A: kirmizi 10 · B: yesill 20 · C: maviii 30'],"
    "              degerler=['kirmizi','yesill','maviii']);"
    "print(m[0], sorted(h.items()))"
)


def test_AYNI_UZUNLUKTA_DEGERLER_KARARLI_MASKELENIR():
    """🔴 Farklı `PYTHONHASHSEED` ile **aynı** çıktı gelmeli.

    ⚠ Tek süreç içinde tekrar etmek YETMEZ: kusur tam olarak **süreçler arası**dır ve
    aynı süreçte hiç görünmez. Bu yüzden kapı gerçekten ayrı süreçler doğurur.
    """
    ciktilar = set()
    for tohum in ("0", "1", "12345"):
        r = subprocess.run([sys.executable, "-c", _KOD], capture_output=True, text=True,
                           env={"PYTHONHASHSEED": tohum, "PATH": "/usr/local/bin:/usr/bin:/bin"})
        assert r.returncode == 0, r.stderr[-400:]
        ciktilar.add(r.stdout.strip())
    assert len(ciktilar) == 1, (
        f"maskeleme hash tohumuna göre DEĞİŞİYOR — {len(ciktilar)} farklı çıktı: "
        f"{ciktilar}")
