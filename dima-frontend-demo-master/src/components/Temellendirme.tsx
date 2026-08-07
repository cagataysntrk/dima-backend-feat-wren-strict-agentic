"use client";

/**
 * 🔴 G1 — TEMELLENDİRME: *"anladığım şu…"*
 *
 * ## Neden ayrı bir bileşen
 *
 * `test_frontend_buyume.py` bu render'ı `ReportCard.tsx` içindeyken **yakaladı**:
 * tavan aşıldı. Kapının kendi talimatı: *"yeni davranışı bir **bileşene çıkar**,
 * tavanı yükseltme."* `Makbuz` · `SertifikaBandi` · `HataSeridi` tam böyle doğmuştu.
 *
 * ## Neden bu satır var
 *
 * Üretimdeki başarısızlığın **%69'u** *"SQL çalıştı, makul bir sayı döndü, ama BAŞKA
 * bir sorunun cevabıydı"* sınıfı (`WRONG_FILTER` %54,6 + `WRONG_SCOPE` %14,4).
 * Garson **siparişi tekrarlar** — hata ilk saniyede görünür olur.
 *
 * ⚠ Bu bir **garanti değil**, bir **görünürlük**: etiketi okumayan kullanıcı yanlış
 * sayıyı yine taşır. Sınır `app/temellendirme.py`'de de yazılı.
 *
 * ⚠ Ve **0 token**: kaynağı yalnız `cube_query`. LLM tamamen düşse bile bu satır gelir
 * (bozulma merdiveninin 3. basamağı).
 */

import type { AskResponse } from "@/lib/types";

/**
 * 🔴 `G1.7` — **ROZETLER TIKLANABİLİR, AMA DÜZENLEMEZ: DÜZENLEYENE GÖTÜRÜR.**
 *
 * Plan *"her rozet → o alanı değiştiren chip (`POST /cube`, 0 LLM)"* diyordu. Ölçüldü ve
 * **olduğu gibi uygulanamaz**: `InterpretationBar` o alanların **dördünü zaten
 * düzenliyor** (`next.measures` · `next.dimensions` · `next.filters` ·
 * `next.timeDimensions`). İkinci bir düzenleme yüzeyi, bu deponun bir numaralı kusurunu
 * (*aynı kuralın iki sahibi*) doğrudan üretirdi — ve iki yüzey zamanla **ayrışırdı**.
 *
 * Bu yüzden rozet bir **kısayoldur**: tıklanınca ilgili düzenleme chip'ine götürür
 * (odaklar + vurgular). Kullanıcı için sonuç aynı — *"anladığım şeyi buradan
 * değiştirebilirim"* — ama sahiplik tek yerde kalır.
 *
 * *Bir yeteneği iki yere koymak, onu iki kez kazanmak değil; iki kez bakmaktır.*
 *
 * ⚠ `cube` rozeti tıklanmaz: cube'u değiştirmek bir **düzenleme değil yeni bir sorudur**
 * (`InterpretationBar` da onu düzenlemiyor). Yanlış cube'da doğru yol netleştirmedir.
 */
export function Temellendirme({ item }: { item: AskResponse }) {
  const t = item.temellendirme;
  if (!t) return null;

  // 🔴 `DA-7` — **KAPSAM ROZETİ İLK SIRADA.** `temellendirme.cube` üretiliyor, testleniyor
  // ve tipli olduğu hâlde render EDİLMİYORDU. `G1`'in varlık gerekçesi ölçülmüş
  // `WRONG_SCOPE` **%14,4**'tü — yani *"hangi konuyu anladım"* bu rozetin tam olarak
  // cevapladığı soru. Kapsamı söylemeyen bir temellendirme, en sık yanlışı görünmez
  // bırakır. *Bir beyanın en önemli parçasını düşürmek, beyanı süse çevirir.*
  // Her rozet, düzenleme çubuğundaki karşılığının **çapasını** taşır. `null` = tıklanmaz.
  // ⚠ Çapa adları `InterpretationBar`'ın `data-capa` değerleriyle **birebir** aynı olmalı;
  // ayrışırlarsa tıklama sessizce hiçbir şey yapmaz — bu yüzden bir kapı ikisini karşılaştırır.
  const rozetler: { etiket: string; capa: string | null }[] = [
    { etiket: t.cube ?? "", capa: null },          // cube değişimi = yeni soru, düzenleme değil
    { etiket: t.olcu ?? "", capa: "olcu" },
    { etiket: t.donem ?? "", capa: "donem" },
    { etiket: t.granulerlik ?? "", capa: "granulerlik" },
    // 🔴 `G6.3` — kıyas rozeti düzenleme çubuğundaki **kıyas anahtarına** götürür.
    // ⚠ Kendisi kıyası açıp kapatmaz: o anahtar `InterpretationBar`'da ve tek sahibi o.
    { etiket: t.kiyas ?? "", capa: "kiyas" },
    ...(t.kirilim ?? []).map((x) => ({ etiket: x, capa: "kirilim" })),
    ...(t.filtreler ?? []).map((x) => ({ etiket: x, capa: "filtre" })),
  ].filter((r) => r.etiket);

  if (rozetler.length === 0) return null;

  return (
    <span className="inline-flex flex-wrap items-center gap-1">
      <span className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
        anladığım
      </span>
      {/* ⚠ Anahtar `etiket+i`: `filtreler` backend'de tekilleştirilmiyor
          (`temellendirme.py:119`), aynı filtre iki kez gelirse React anahtar çakışırdı. */}
      {rozetler.map(({ etiket, capa }, i) =>
        capa ? (
          <button
            key={`${etiket}-${i}`}
            type="button"
            onClick={() => {
              // 🔴 DÜZENLEME YAPMAZ — düzenleyene götürür. `POST /cube` çağrısı da
              // buradan gitmez: o `InterpretationBar`'ın chip'inin işi ve tek sahibi o.
              const el = document.querySelector<HTMLElement>(`[data-capa="${capa}"]`);
              if (!el) return;
              el.scrollIntoView({ behavior: "smooth", block: "nearest" });
              el.focus?.();
              // Kısa bir vurgu: kullanıcı NEREYE götürüldüğünü görmeli, yoksa tıklama
              // "hiçbir şey olmadı" gibi okunur.
              el.classList.add("ring-1", "ring-accent");
              window.setTimeout(() => el.classList.remove("ring-1", "ring-accent"), 1200);
            }}
            title={`Bunu değiştir — düzenleme çubuğundaki «${capa}» chip'ine götürür ` +
                   `(sorgu buradan DEĞİŞMEZ; tek düzenleme yüzeyi orasıdır)`}
            className="border border-hairline px-1.5 py-0.5 font-mono text-[10px] text-neutral-500 transition-colors hover:border-accent hover:text-accent"
          >
            {etiket}
          </button>
        ) : (
        <span
          key={`${etiket}-${i}`}
          className="border border-hairline px-1.5 py-0.5 font-mono text-[10px] text-neutral-500"
          title="Sistemin sorudan anladığı — deterministik, LLM'siz"
        >
          {etiket}
        </span>
        ),
      )}
    </span>
  );
}
