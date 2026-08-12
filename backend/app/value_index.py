"""Bulanık değer/sözlük indeksi (literatür #4): typo toleransı.

Kapsam kapısından TANINMADAN çıkan token'lar için katalogdan aday üretir.
Politika (ADR-0008, seçici tahmin):
    tek aday + YÜKSEK benzerlik  → soru görünür şekilde düzeltilir (trace'te),
                                   normal deterministik boru hattı devam eder
    orta benzerlik / çok aday    → "şunu mu demek istedin?" chip'leri
    aday yok                     → mevcut dürüst not (değişmez)

Birebir eşleşme yolları DEĞİŞMEZ — indeks yalnız bugün zaten başarısız olan
sorgularda (tanınmayan kelime varken) çalışır; %100 answered-precision'a
dokunma riski bilinçli olarak sıfıra yakın tutulur.

Kaynaklar: kategorik boyut DEĞERLERİ (müşteri/renk/kumaş adları — şema
zenginleştirmede problanır) + tüm SÖZLÜK (cube/ölçü/boyut sinonimleri).
Benzerlik: önek-hizalı Levenshtein oranı — Türkçe çekim eki taşıyan token'da
("müterileri" ≈ müşteri) kuyruk cezası oluşmaz. Bağımlılık yok, saf Python;
Egemen ölçeğinde (binlerce değer) gerekirse üçlü-gram ters-indeks eklenir.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.llm import _norm

AUTO_SCORE = 0.8   # tek aday + bu benzerlik + yeterli uzunluk → otomatik düzeltme
AUTO_MARGIN = 0.08  # ikinci FARKLI adaya asgari fark (belirsizse otomatik düzeltme YOK)
CHIP_SCORE = 0.65  # altı: aday bile sayılmaz ("tedar"≈"tutar" 0.60 gürültüsü elenir)
MIN_SURF_LEN = 4   # bundan kısa yüzeylere bulanık eşleşme yapılmaz (gürültü)
MIN_AUTO_LEN = 5   # otomatik düzeltme için asgari yüzey uzunluğu


def _lev(a: str, b: str) -> int:
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[-1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _ratio(tok: str, surf: str) -> float:
    """Önek-hizalı benzerlik: token çekim eki taşıyabilir → yüzey uzunluğuna kırpılmış
    halleri de denenir, en iyisi alınır. Kırpma yalnız YETERİNCE UZUN yüzeylerde —
    kısa yüzeyde token'ın yarısını atmak sahte benzerlik üretir ("tedar"≈"tutar")."""
    variants = {tok}
    if len(surf) >= 6:
        variants |= {tok[: len(surf)], tok[: len(surf) + 1]}
    best = 0.0
    for t in variants:
        if not t:
            continue
        m = max(len(t), len(surf))
        if m:
            best = max(best, 1.0 - _lev(t, surf) / m)
    return best


@dataclass
class Candidate:
    surface: str  # normalize yüzey ("efe dokuma") — soru düzeltmede kullanılır
    label: str    # insan-okur etiket ("Efe Dokuma" / "müşteri")
    span: str     # sorudaki düzeltilecek parça (normalize)
    score: float
    kind: str     # "value" | "vocab"


class FuzzyIndex:
    def __init__(self, schema: dict):
        self._entries: list[tuple[str, str, str]] = []  # (surface_norm, label, kind)
        seen: set[tuple[str, str]] = set()

        def _add(surface: str, label: str, kind: str) -> None:
            s = _norm(surface).strip()
            if len(s) < MIN_SURF_LEN or (s, kind) in seen:
                return
            seen.add((s, kind))
            self._entries.append((s, label, kind))

        for c in schema.get("cubes", []):
            for vals in (c.get("dimension_values") or {}).values():
                for v in vals or []:
                    _add(str(v), str(v), "value")
            vocab = list(c.get("synonyms") or [])
            for syns in (c.get("measure_synonyms") or {}).values():
                vocab += syns or []
            for syns in (c.get("dimension_synonyms") or {}).values():
                vocab += syns or []
            for s0 in vocab:
                plain = s0[:-1] if s0.endswith("!") else s0
                _add(plain, plain, "vocab")

    # ------------------------------------------------------------------ #

    def _spans(self, q_norm: str, unknown: list[str]) -> list[str]:
        """Aday parçalar: tanınmayan token'lar + onları içeren komşu ikilemeler
        ("efe dokma" → çok-kelimeli değer 'efe dokuma' ancak ikilemeyle bulunur)."""
        toks = q_norm.split()
        unk = set(unknown)
        spans: list[str] = []
        for i, t in enumerate(toks):
            if t not in unk:
                continue
            spans.append(t)
            if i > 0:
                spans.append(f"{toks[i - 1]} {t}")
            if i + 1 < len(toks):
                spans.append(f"{t} {toks[i + 1]}")
        return spans

    def suggest(self, q_norm: str, unknown: list[str], top: int = 3) -> list[Candidate]:
        """Tanınmayan parçalara en yakın katalog adayları (skor sırasıyla, ≥CHIP_SCORE)."""
        best: dict[str, Candidate] = {}  # surface → en iyi aday
        for span in self._spans(q_norm, unknown):
            for surf, label, kind in self._entries:
                # uzunluk ön-eleme: çok farklı uzunluklar hesaba girmesin
                if abs(len(span) - len(surf)) > max(4, len(surf)):
                    continue
                sc = _ratio(span, surf)
                if sc < CHIP_SCORE or sc >= 1.0:
                    continue  # 1.0 zaten birebir yol; buraya düşmüşse kapsam sorunu değil
                cur = best.get(surf)
                if cur is None or sc > cur.score:
                    best[surf] = Candidate(surf, label, span, sc, kind)
        return sorted(best.values(), key=lambda c: -c.score)[:top]

    def auto_fix(self, q_norm: str, unknown: list[str]) -> Candidate | None:
        """Tek ve açık ara önde aday → otomatik düzeltme; aksi halde None (chip'e kalır)."""
        cands = self.suggest(q_norm, unknown)
        if not cands:
            return None
        c = cands[0]
        # ⚠ Uzunluk ön koşulu **burada kalır** (`KAT-1`): *«kaç harften kısa bir yüzey
        # otomatik düzeltilmez»* bu indeksin alan bilgisidir, ortak *«emin miyim»*
        # sorusu değil. Eşik aritmetiğinin tek sahibi ise artık `emin_miyim.karar`.
        if len(c.surface) < MIN_AUTO_LEN:
            return None
        from app.emin_miyim import Karar, karar
        if karar([x.score for x in cands],
                 taban=AUTO_SCORE, marj=AUTO_MARGIN) is not Karar.OTO_ICRA:
            return None  # düşük skor ya da yakın ikinci aday → belirsiz, sorulur
        return c
