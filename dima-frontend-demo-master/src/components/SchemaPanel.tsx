"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { getMetrics, getSchema, setMetrikSahibi } from "@/lib/api-client";
import { usePermission } from "@/lib/usePermission";

// Veri modeli (şema) — artık ana yüzeyde değil, Ayarlar drawer'ı içinde gösterilir (ADR-0007 K7).
export function SchemaPanel({ kapsam }: { kapsam?: string | null } = {}) {
  const { data, isLoading, isError } = useQuery({
    // ⚠ `kapsam` sorgu ANAHTARINDA: olmasaydı mercek değişince React Query önbellekten
    // ESKİ katalogu döndürürdü — kullanıcı seçim yapar, hiçbir şey değişmezdi.
    queryKey: ["schema", kapsam ?? "genel"],
    queryFn: () => getSchema(kapsam),
  });

  return (
    <div className="space-y-6">
      {/* FAZ 2.2b — METRİK SAHİPLİĞİ.
          🔴 YENİ PANEL AÇILMADI (K5 tavanı 13/13, pay 0): sahiplik bir KATALOG
          bilgisidir — "şu terim hangi cube'a ait" — ve yeri kataloğun kendisidir.
          Ayrı bir ekran, kullanıcıyı aynı soruyu iki yerde aramaya iterdi. */}
      <MetrikSahipligi />
      <section>
        <h3 className="text-[11px] font-semibold uppercase tracking-wide text-neutral-400 mb-3">
          Tablolar
        </h3>
        {isLoading && <p className="text-sm text-neutral-400">Yükleniyor…</p>}
        {isError && (
          <p className="text-sm text-red-500">
            {"Backend'e ulaşılamadı. dima-backend çalışıyor mu?"}
          </p>
        )}
        <ul className="space-y-3">
          {data?.models.map((model) => (
            <li key={model.name} className="border border-hairline p-3">
              <p className="font-mono text-[13px] font-semibold text-accent">{model.name}</p>
              <ul className="mt-1.5 space-y-0.5">
                {model.columns.map((col) => (
                  <li key={col.name} className="text-xs text-neutral-500">
                    <div className="flex justify-between gap-3">
                      <span className="font-mono truncate">{col.name}</span>
                      <span className="text-neutral-400 shrink-0">{col.type}</span>
                    </div>
                    {/* Doğrulama turu düzeltmesi (1 Ağustos 2026, P2-22) — düşük-kardinaliteli
                        kolonların olası değerleri (filtre chip'i adayları) ZATEN backend'den
                        geliyordu ama hiç GÖSTERİLMİYORDU. */}
                    {col.values && col.values.length > 0 && (
                      <p className="mt-0.5 truncate font-mono text-[10px] text-neutral-400">
                        {col.values.slice(0, 8).join(", ")}
                        {col.values.length > 8 ? ` +${col.values.length - 8}` : ""}
                      </p>
                    )}
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      </section>

      {data?.cubes && data.cubes.length > 0 && (
        <section>
          <h3 className="text-[11px] font-semibold uppercase tracking-wide text-neutral-400 mb-3">
            Cube&apos;lar (soru sorabileceğin ölçü/boyutlar)
          </h3>
          <ul className="space-y-3">
            {data.cubes.map((cube) => (
              <li key={cube.name} className="border border-hairline p-3">
                <p className="font-mono text-[13px] font-semibold text-accent">{cube.name}</p>
                {(cube.measures?.length ?? 0) > 0 && (
                  <p className="mt-1 text-xs text-neutral-500">
                    <span className="text-neutral-400">ölçüler: </span>
                    {cube.measures!.join(", ")}
                  </p>
                )}
                {(cube.dimensions?.length ?? 0) > 0 && (
                  <ul className="mt-1 space-y-0.5">
                    {cube.dimensions!.map((dim) => {
                      const vals = cube.dimension_values?.[dim];
                      return (
                        <li key={dim} className="text-xs text-neutral-500">
                          <span className="font-mono">{dim}</span>
                          {vals && vals.length > 0 && (
                            <span className="ml-1.5 font-mono text-[10px] text-neutral-400">
                              ({vals.slice(0, 6).join(", ")}
                              {vals.length > 6 ? ` +${vals.length - 6}` : ""})
                            </span>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {data?.relationships && data.relationships.length > 0 && (
        <section>
          <h3 className="text-[11px] font-semibold uppercase tracking-wide text-neutral-400 mb-3">
            İlişkiler
          </h3>
          <ul className="space-y-2">
            {data.relationships.map((rel) => (
              <li key={rel.name} className="text-xs text-neutral-500">
                <span className="font-mono text-neutral-700 dark:text-neutral-300">
                  {rel.models.join(" → ")}
                </span>
                <span className="block text-neutral-400">{rel.condition}</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}


/** Çakışan terimlerin **sahipliği** — hakemin tek besleme yolu.
 *
 * 🔴 **Çakışmanın kendisi bir OLGUDUR, karara bağlı değil.** Bu blok bayrak kapalıyken
 * de çakışmaları gösterir; gizlemek, kullanıcıyı *"sistem neden bazen yanlış cube
 * seçiyor"* sorusuyla **kanıtsız** bırakırdı.
 *
 * ⚠ Düğme yalnız `metric:certify` yetkisi varsa görünür — ama görünürlük bir güvenlik
 * sınırı DEĞİL: sınırı backend zorlar (`require("metric:certify")`). UI yalnız
 * yapamayacağı bir şeyi kullanıcıya **teklif etmez**.
 */
function MetrikSahipligi() {
  const qc = useQueryClient();
  const yetkili = usePermission("metric:certify");
  const { data, isLoading } = useQuery({ queryKey: ["metrics"], queryFn: getMetrics });
  const ata = useMutation({
    mutationFn: ({ terim, cube }: { terim: string; cube: string | null }) =>
      setMetrikSahibi(terim, cube),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["metrics"] }),
  });

  if (isLoading || !data) return null;
  if (data.kayit.length === 0) {
    return (
      <section>
        <h3 className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-neutral-400">
          Metrik sahipliği
        </h3>
        <p className="font-mono text-[11px] text-neutral-400">
          Çakışan terim yok — her terim tek bir cube&apos;a ait.
        </p>
      </section>
    );
  }

  return (
    <section>
      <h3 className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-neutral-400">
        Metrik sahipliği · {data.cakisan_terim_sayisi} çakışan terim
      </h3>
      <p className="mb-3 font-mono text-[10px] leading-snug text-neutral-400">
        Bir terimi birden fazla cube iddia ediyorsa yönlendirici hangisini seçeceğini
        bilemez. Sahibini seçmek, o belirsizliği <span className="text-accent">kalıcı</span>{" "}
        olarak çözer.
      </p>
      <ul className="space-y-2">
        {data.kayit.map((k) => {
          const sahip = k.sahiplenilen_terimler[0] ?? null;
          return (
            <li key={k.terim} className="border border-hairline px-2.5 py-2">
              <div className="flex items-center gap-2">
                <span className="font-mono text-[12px] text-foreground">{k.terim}</span>
                {sahip && (
                  <span className="border border-accent/40 px-1.5 font-mono text-[10px] text-accent">
                    ◉ {sahip}
                  </span>
                )}
                {/* FAZ 3.1b — PACK ÖNERİSİ. Alan bilgisi kaybolmaz, yalnız DAYATILMAZ:
                    tek tıkla kabul edilir ve o andan itibaren TENANT kararı olur. */}
                {!sahip && k.onerilen_sahip && (
                  <span
                    title="Karar kaydının önerisi — HENÜZ UYGULANMADI. Kabul etmek için ilgili küpe tıkla."
                    className="border border-hairline px-1.5 font-mono text-[10px] text-neutral-500"
                  >
                    ○ öneri: {k.onerilen_sahip}
                  </span>
                )}
                {k.gecersiz_sahip && (
                  <span
                    title="Bu cube o terimin adayı değil — karar KAYDEDİLDİ ama UYGULANMIYOR."
                    className="border border-amber-500/40 px-1.5 font-mono text-[10px] text-amber-600"
                  >
                    ⚠ geçersiz: {k.gecersiz_sahip}
                  </span>
                )}
              </div>
              <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
                {k.adaylar.map((c) => (
                  <button
                    key={c}
                    type="button"
                    disabled={!yetkili || ata.isPending || c === sahip}
                    onClick={() => ata.mutate({ terim: k.terim, cube: c })}
                    className={`border px-1.5 py-[2px] font-mono text-[10px] transition-colors disabled:opacity-50 ${
                      c === sahip
                        ? "border-accent/40 text-accent"
                        : c === k.onerilen_sahip
                          ? "border-neutral-400 text-foreground hover:border-accent hover:text-accent"
                          : "border-hairline text-neutral-500 hover:border-accent hover:text-accent"
                    }`}
                  >
                    {c}
                  </button>
                ))}
                {sahip && yetkili && (
                  <button
                    type="button"
                    disabled={ata.isPending}
                    onClick={() => ata.mutate({ terim: k.terim, cube: null })}
                    title="Sahipliği kaldır — kayıt silinmez, kararın geri alındığı da bir kayıttır."
                    className="border border-hairline px-1.5 py-[2px] font-mono text-[10px] text-neutral-400 transition-colors hover:text-foreground"
                  >
                    × kaldır
                  </button>
                )}
              </div>
            </li>
          );
        })}
      </ul>
      {!yetkili && (
        <p className="mt-2 font-mono text-[10px] text-neutral-400">
          Sahiplik değiştirmek için yetkiniz yok — bir yöneticiden isteyebilirsiniz.
        </p>
      )}
    </section>
  );
}
