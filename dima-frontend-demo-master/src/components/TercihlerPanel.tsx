"use client";

// KALICI SUNUM TERCİHLERİ (Faz E) — kullanıcı NE sakladığımızı görebilmeli ve tek
// tıkla silebilmeli. Görünmeyen ve kaldırılamayan bir tercih, bir hafızadan çok bir
// hataya benzer: aylar sonra "bu rapor neden aylık?" sorusu cevapsız kalır.
//
// Bu panelde YAZMA YOK ve bu bilinçli: tercih yazmak /ask/eylem ONAY kademesinden
// geçer (Faz H değişmezi — "onaysız hiçbir yazma"). Kullanıcı tercihi konuşarak
// koyar ("bundan sonra hep aylık göster"), onay kartından onaylar; buradan görür ve
// kaldırır.

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  deleteBildirimTercihi,
  getBildirimTercihleri,
  listTercihler,
  setBildirimTercihi,
  silTercih,
} from "@/lib/api-client";

const KATEGORI_ETIKET: Record<string, string> = {
  report: "Rapor", alert: "Alarm", anomaly: "Anomali", system: "Sistem",
};

const ANAHTAR_ETIKET: Record<string, string> = {
  granularity: "Zaman kırılımı",
  view: "Görünüm",
};

export default function TercihlerPanel() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({
    queryKey: ["tercihler"],
    queryFn: listTercihler,
  });
  const sil = useMutation({
    mutationFn: (anahtar: string) => silTercih(anahtar),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tercihler"] }),
  });

  if (isLoading) return <p className="font-mono text-xs text-muted">yükleniyor…</p>;
  const tercihler = data ?? [];

  return (
    <div className="flex flex-col gap-3">
      <p className="font-mono text-[11px] leading-snug text-muted">
        Sohbette <span className="text-foreground">“bundan sonra hep aylık göster”</span> gibi
        bir şey söylediğinizde onay isteriz; onayladıklarınız burada durur. Tercihler
        yalnız <span className="text-foreground">görünümü</span> etkiler — hangi ölçünün
        ya da hangi konunun raporlandığına asla karışmaz.
      </p>
      {tercihler.length === 0 ? (
        <p className="font-mono text-xs text-muted">Kayıtlı tercih yok.</p>
      ) : (
        <ul className="flex flex-col gap-2">
          {tercihler.map((t) => (
            <li
              key={t.anahtar}
              className="flex items-start justify-between gap-3 border border-hairline p-2"
            >
              <div className="min-w-0">
                <div className="font-mono text-[11px] uppercase tracking-wider text-neutral-400">
                  {ANAHTAR_ETIKET[t.anahtar] ?? t.anahtar}
                </div>
                <div className="font-mono text-[13px] text-foreground">{t.etiket}</div>
                {t.kaynak_ifade && (
                  // Kullanıcı "bunu ne zaman söylemişim?" diye sorabilmeli.
                  <div className="mt-0.5 font-mono text-[10px] text-muted">
                    kaynak: “{t.kaynak_ifade}”
                  </div>
                )}
              </div>
              <button
                onClick={() => sil.mutate(t.anahtar)}
                disabled={sil.isPending}
                className="shrink-0 border border-hairline px-2 py-0.5 font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
              >
                kaldır
              </button>
            </li>
          ))}
        </ul>
      )}

      {/* 🔴 FAZ 5.9b — BİLDİRİM TERCİHLERİ. Yeni bir PANEL DEĞİL: var olan tercih
          panelinin ikinci bölümü (K5 tavanı 13/13 — *bir yetenek bir panel doğurmaz*).
          `NotificationPreference` YETİM bir tabloydu: kullanıcı bir kategoriyi
          kapatabileceğini sanıyordu ama onu yazacağı hiçbir yüzey yoktu. */}
      <BildirimTercihleri />
    </div>
  );
}

function BildirimTercihleri() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ["bildirim-tercihleri"],
    queryFn: getBildirimTercihleri,
  });
  const yaz = useMutation({
    mutationFn: setBildirimTercihi,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["bildirim-tercihleri"] }),
  });
  const sil = useMutation({
    mutationFn: (v: { category: string; channel: string }) =>
      deleteBildirimTercihi(v.category, v.channel),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["bildirim-tercihleri"] }),
  });
  if (!data?.length) return null;

  // ⚠ Yalnız DIŞ kanallar gösterilir: `inapp` bu fazda her zaman açıktır ve onu
  // kapatılabilir göstermek, tutulamayacak bir söz vermek olurdu.
  const satirlar = data.filter((t) => t.channel !== "inapp");

  return (
    <div className="mt-6 border-t border-hairline pt-3">
      <h3 className="font-mono text-[11px] uppercase tracking-wider text-muted">
        bildirim tercihleri
      </h3>
      <p className="mt-1 font-mono text-[10px] leading-snug text-neutral-400">
        Kaydı olmayan bir satır <span className="text-foreground">varsayılan</span>dır:
        açık. “Kaldır” kapatmaz — tercihi <span className="text-foreground">hiç
        verilmemiş</span> hâline döndürür.
      </p>
      <ul className="mt-2 space-y-1">
        {satirlar.map((t) => (
          <li
            key={`${t.category}-${t.channel}`}
            className="flex items-center justify-between gap-3 border border-hairline px-2 py-1"
          >
            <span className="font-mono text-[11px] text-foreground">
              {KATEGORI_ETIKET[t.category] ?? t.category}
              <span className="ml-1 text-neutral-400">· {t.channel}</span>
              {t.varsayilan && (
                <span className="ml-1 text-[10px] text-neutral-500">(varsayılan)</span>
              )}
            </span>
            <span className="flex shrink-0 items-center gap-1">
              <button
                onClick={() =>
                  yaz.mutate({ category: t.category, channel: t.channel,
                               enabled: !t.enabled })
                }
                disabled={yaz.isPending}
                className={`border px-2 py-0.5 font-mono text-[11px] transition-colors disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)] ${
                  t.enabled
                    ? "border-accent/50 text-accent"
                    : "border-hairline text-neutral-500"
                }`}
              >
                {t.enabled ? "açık" : "kapalı"}
              </button>
              {!t.varsayilan && (
                <button
                  onClick={() => sil.mutate({ category: t.category, channel: t.channel })}
                  disabled={sil.isPending}
                  title="Tercihi kaldır — varsayılana (açık) döner"
                  className="border border-hairline px-2 py-0.5 font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground disabled:cursor-not-allowed disabled:opacity-[var(--opacity-disabled)]"
                >
                  kaldır
                </button>
              )}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
