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

import { listTercihler, silTercih } from "@/lib/api-client";

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
                className="shrink-0 border border-hairline px-2 py-0.5 font-mono text-[11px] text-neutral-400 transition-colors hover:text-foreground disabled:opacity-50"
              >
                kaldır
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
