"use client";

/** **YAN ÇUBUK** — sağdaki ikon şeridinin ve beş çekmecenin yerini alan tek yüzey.
 *
 * ## 🔴 Neden bu bileşen var
 *
 * Bugüne kadar arayüzün *"kabuğu"* **iki ayrı yerde** yaşıyordu: sağda bir ikon şeridi
 * (`FloatingControls`) ve `layout.tsx`'te sabit duran **dört öge** (bağlantı rozeti ·
 * kimlik şeridi · çıkış · tema). Bir envanter denetimi bu dördünün *"rail'i taşıdım"*
 * diyen birinin **atlayacağı ilk şey** olduğunu ölçtü — çünkü rail'de değiller.
 *
 * > ⚠ *Bir kabuk iki yerde yaşıyorsa, taşınırken yarısı geride kalır.*
 *
 * ## Neden `…Panel` DEĞİL
 *
 * Panel tavanı **13/13 dolu** (`test_panel_sayisi.py`). Bu bileşen bir panel **açmıyor**,
 * beş çekmeceyi **birleştiriyor** — ve `HistoryPanel` içine eriyerek sayıyı **12'ye**
 * düşürüyor. *Bir yetenek yeni panel doğurmaz; bir sadeleştirme panel eritir.*
 *
 * ## Kapalıyken **kalıcı ray** — hover-flyout değil
 *
 * 🔴 Ölçülmüş kusur (Anthropic'in kendi hata kaydı): hover ile açılan bir çubukta imleç
 * hedefe varmadan panel kapanıyor ve kullanıcı *"listeye bakmak"* yerine **avlanıyor**.
 * Ray **her zaman** görünür: ✏ yeni sohbet · ara · geçmiş.
 *
 * ## Durum **çerezde**, localStorage'da değil
 *
 * ⚠ localStorage ilk boyamada okunamaz → çubuk yanlış genişlikte çizilip **zıplar**.
 * Çerez SSR'da okunabildiği için ilk kare doğru genişlikte gelir.
 */

import { useCallback, useEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";

import { useIstemciDegeri } from "@/lib/istemci";

import { ConnectionBadge } from "@/components/ConnectionBadge";
import { GeriAlSeridi } from "@/components/GeriAlSeridi";
import { HataSeridi } from "@/components/HataSeridi";
import { KimlikSeridi } from "@/components/KimlikSeridi";
import { LogoutButton } from "@/components/LogoutButton";
import { NotificationsBell } from "@/components/NotificationsBell";
import { deleteConversation, listConversations, restoreConversation } from "@/lib/api-client";
import { hataMetni } from "@/lib/mutasyonHatasi";
import { type Tema, temaAbone, temaBaslat, temaOku, temaUygula } from "@/lib/tema";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

/** Açık genişlik. ⚠ 240px altında orta uzunluktaki başlıklar kırpılmaya başlar. */
export const CUBUK_GENIS = "16rem"; // 256px
/** Ray genişliği. ⚠ 48px'te 40px'lik dokunma hedefi + kenar boşluğu sıkışıyor. */
export const CUBUK_RAY = "3.5rem"; // 56px

const CEREZ = "sidebar_state";

function cerezOku(): boolean | null {
  if (typeof document === "undefined") return null;
  const m = document.cookie.match(new RegExp(`(?:^|; )${CEREZ}=([^;]*)`));
  return m ? m[1] === "acik" : null;
}

/** İlk açılış değeri: **çerez varsa o**, yoksa ≥1440px'te açık.
 *  ⚠ Modül düzeyinde tanımlı — `useIstemciDegeri` her render'da yeni kimlikli bir
 *  okuyucu alırsa `useSyncExternalStore` sonsuz döngüye girer. */
function baslangicAcik(): boolean {
  const c = cerezOku();
  return c ?? (typeof window !== "undefined" && window.innerWidth >= 1440);
}

function cerezYaz(acik: boolean) {
  // 1 yıl — bir düzen tercihi oturumdan uzun yaşamalı.
  document.cookie = `${CEREZ}=${acik ? "acik" : "ray"}; path=/; max-age=31536000; SameSite=Lax`;
}

/** 🔴 Geçmiş gruplaması: **göreli yakın, mutlak uzak** — insanın zaman zihin modeli.
 *
 * ⚠ Sıralama `updated_at` ile: `created_at` olsaydı, bugün devam ettiğin altı ay
 * önceki sohbet listenin **dibinde** kalırdı. */
function grupla(ts: string): string {
  const g = new Date(ts);
  const bugun = new Date();
  const gunFarki = Math.floor(
    (new Date(bugun.getFullYear(), bugun.getMonth(), bugun.getDate()).getTime() -
      new Date(g.getFullYear(), g.getMonth(), g.getDate()).getTime()) / 86_400_000);
  if (gunFarki <= 0) return "Bugün";
  if (gunFarki === 1) return "Dün";
  if (gunFarki <= 7) return "Son 7 gün";
  if (gunFarki <= 30) return "Son 30 gün";
  return g.toLocaleDateString("tr-TR", { month: "long", year: "numeric" });
}

type Bolum = "bildirimler" | "panolar" | "yardim" | "ayarlar" | null;

export function YanCubuk({
  aktifSessionId,
  onYeniSohbet,
  onResume,
  onBolum,
  onKanitArsivi,
  acikBolum,
  panolarVar,
  incelemeVar,
  onInceleme,
}: {
  aktifSessionId?: string | null;
  onYeniSohbet: () => void;
  onResume: (id: string) => void;
  /** Bölüm çekmecesini açar/kapatır — çubuk **kendisi** çekmece render etmez. */
  onBolum: (b: Bolum) => void;
  /** 🔴 FAZ 6 · KAPANIŞ DENETİMİ — **kanıt arşivinin giriş kapısı.**
   *  `ContractDetailPanel` arşiv listesini ve JSON-LD ihracını yalnız `contractId=""`
   *  iken çiziyordu ve **hiçbir çağıran** boş dize geçmiyordu: kod tamdı, kapısı yoktu.
   *  ⚠ `Bolum` durum makinesine karıştırılmadı — o `SettingsDrawer`ı açar, bu ise
   *  var olan bir paneli açar. *İki farklı davranışı tek bir duruma yüklemek, o durumu
   *  okuyan herkesi hangi dalda olduğunu tahmin etmeye zorlar.* Panel sayısı **sabit**. */
  onKanitArsivi?: () => void;
  acikBolum: Bolum;
  /** `dashboards` bayrağı — yoksa giriş **hiç çizilmez**. */
  panolarVar: boolean;
  /** `measure:read` izni. */
  incelemeVar: boolean;
  onInceleme: () => void;
}) {
  // 🔴 Çerez + ekran genişliği **sunucuda okunamaz**. Eskiden effect gövdesinde senkron
  // `setState` ile okunuyordu — React'ın uyardığı basamaklı-render deseni ve depoda
  // **dört kopya** hâlindeydi. `useIstemciDegeri` aynı işi `useSyncExternalStore`
  // üzerinden yapar; hidrasyon uyumu React'ın garantisi olur, bizim dikkatimiz değil.
  //
  // ⚠ Ve **effect'e geri düşmemek** için tercih bir *"elle seçim"* katmanı olarak
  // tutuluyor: `null` = *"kullanıcı henüz dokunmadı"* → başlangıç değeri geçerli.
  // *Türetilebilen bir değeri duruma kopyalamak, iki kaynağı senkron tutma borcudur.*
  const baslangic = useIstemciDegeri(baslangicAcik, false);
  const [elleSecim, setElleSecim] = useState<boolean | null>(null);
  const acik = elleSecim ?? baslangic;
  const [ara, setAra] = useState("");
  const [hata, setHata] = useState<string | null>(null);
  const [silinen, setSilinen] = useState<{ id: string; title: string } | null>(null);
  const acKapaRef = useRef<HTMLButtonElement>(null);

  const degistir = useCallback(() => {
    setElleSecim((a) => {
      const yeni = !(a ?? baslangicAcik());
      cerezYaz(yeni);
      return yeni;
    });
  }, []);

  // 🔴 `Ctrl/Cmd+B` — ⚠ composer odaktayken **DEVRE DIŞI**.
  // `Ctrl+B` metin kutusunda "kalın" demektir; yakalamak kullanıcıya yanlış davranış
  // verir. Bu çakışma ölçülmüş bir kusurdur, varsayım değil.
  useEffect(() => {
    const f = (e: KeyboardEvent) => {
      if (!(e.ctrlKey || e.metaKey) || e.key.toLowerCase() !== "b") return;
      const h = document.activeElement;
      const yaziyor =
        h instanceof HTMLTextAreaElement ||
        h instanceof HTMLInputElement ||
        (h instanceof HTMLElement && h.isContentEditable);
      if (yaziyor) return;
      e.preventDefault();
      degistir();
    };
    window.addEventListener("keydown", f);
    return () => window.removeEventListener("keydown", f);
  }, [degistir]);

  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["conversations"], queryFn: listConversations });

  const geriAl = useMutation({
    onError: (e) => setHata(hataMetni(e, "Geri alma")),
    mutationFn: (id: string) => restoreConversation(id),
    onSuccess: () => {
      setSilinen(null);
      qc.invalidateQueries({ queryKey: ["conversations"] });
    },
  });
  const sil = useMutation({
    onError: (e) => {
      // 🔴 Silme başarısızsa geri-al şeridi **gösterilmez**: olmayan bir silmeyi geri
      // almayı teklif etmek, kullanıcıya yanlış bir dünya tarif eder.
      setSilinen(null);
      setHata(hataMetni(e, "Sohbet silme"));
    },
    mutationFn: (id: string) => deleteConversation(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["conversations"] }),
  });

  const gruplar = useMemo(() => {
    const q = ara.trim().toLocaleLowerCase("tr");
    const liste = (data ?? [])
      .filter((c) => !q || (c.title || "").toLocaleLowerCase("tr").includes(q))
      // ⚠ `updated_at` — bkz. `grupla()` başlığındaki gerekçe.
      .slice()
      .sort((a, b) => (a.updated_at < b.updated_at ? 1 : -1));
    const out = new Map<string, typeof liste>();
    for (const c of liste) {
      const g = grupla(c.updated_at);
      out.set(g, [...(out.get(g) ?? []), c]);
    }
    return [...out.entries()];
  }, [data, ara]);

  const ikonBtn =
    "flex h-10 w-10 items-center justify-center rounded-[var(--radius-btn)] text-muted " +
    "transition-colors hover:bg-[var(--surface-3)] hover:text-foreground";

  return (
    <>
      {/* ── 📱 MOBİL ÜST ŞERİT — 🔴 ÇUBUK KÜÇÜK EKRANDA ÇUBUK DEĞİLDİR ─────────
          375px'lik bir ekranda 256px'lik bir çubuk **ekranın üçte ikisidir**;
          56px'lik bir ray ise %15'ini yer ve başparmakla en zor ulaşılan kenardadır.
          Küçük ekranda çubuk bir **katmana** dönüşür ve yerini her zaman görünen
          iki düğme tutar: ☰ ve ✏.

          ⚠ Bu düzeltme bir gerilemenin karşılığı: FAZ 2'de çubuğa `max-md:hidden`
          koymuştum ve mobilde **yeni sohbet/geçmiş/ayarlara hiçbir giriş
          kalmamıştı**. Eski ikon şeridi mobilde alt çubuğa dönüşüyordu; onu
          kaldırırken karşılığını koymamıştım.
          *Bir yüzeyi kaldırmak, onun taşıdığı girişleri de kaldırmaktır — yerine
          bir şey konmadıysa.* */}
      <div
        data-no-print
        className="fixed inset-x-0 top-0 z-40 hidden h-12 items-center gap-1 border-b border-[var(--surface-kenar)] bg-[var(--surface-1)]/95 px-2 backdrop-blur-sm max-md:flex"
      >
        <button
          onClick={degistir}
          aria-expanded={acik}
          aria-controls="yan-cubuk-govde"
          aria-label="Menü"
          title="Menü"
          className={ikonBtn}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <path d="M3 6h18M3 12h18M3 18h18" />
          </svg>
        </button>
        <button onClick={onYeniSohbet} aria-label="Yeni sohbet" title="Yeni sohbet" className={ikonBtn}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 20h9" />
            <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z" />
          </svg>
        </button>
        <span className="ml-1 flex-1 truncate font-mono text-[var(--text-meta)] text-muted">dima</span>
        <ConnectionBadge gomulu />
        <LogoutButton gomulu />
      </div>

      {/* Mobil perde — katman açıkken arkaya dokunmak kapatır. ⚠ Yalnız mobilde:
          masaüstünde çubuk **reflow** yapar, perde gerekmez. */}
      {acik && (
        <div
          onClick={degistir}
          aria-hidden
          className="fixed inset-0 z-40 hidden bg-black/40 max-md:block"
        />
      )}

    <nav
      data-no-print
      data-kayan-cubuk
      role="navigation"
      aria-label="Sohbet geçmişi ve ayarlar"
      style={{ width: acik ? CUBUK_GENIS : CUBUK_RAY }}
      className={`flex h-full shrink-0 flex-col border-r border-[var(--surface-kenar)] bg-[var(--surface-1)] transition-[width] duration-[var(--motion-md)] ease-[var(--ease-standard)] max-md:fixed max-md:inset-y-0 max-md:left-0 max-md:z-50 max-md:!w-[18rem] max-md:transition-transform ${
        acik ? "max-md:translate-x-0" : "max-md:-translate-x-full"
      }`}
    >
      {/* ── ÜST: aç/kapa + yeni sohbet — ikisi de rayda GÖRÜNÜR ────────────────
          🔴 Aç/kapa düğmesi **görünür**: Claude Desktop'ta pin durumu yalnız bir
          kısayolun arkasındaydı ve kullanıcılar özelliğin *hiç var olmadığı* sonucuna
          varıyordu. *Görünmez bir durum, olmayan bir özelliktir.* */}
      <div className="flex h-14 shrink-0 items-center gap-1 px-2">
        <button
          ref={acKapaRef}
          onClick={degistir}
          aria-expanded={acik}
          aria-controls="yan-cubuk-govde"
          title={`${acik ? "Çubuğu daralt" : "Çubuğu genişlet"} · Ctrl+B`}
          aria-label={acik ? "Çubuğu daralt" : "Çubuğu genişlet"}
          className={ikonBtn}
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
            <rect x="3" y="4" width="18" height="16" rx="2" />
            <path d="M9 4v16" />
          </svg>
        </button>
        {acik && (
          <span className="truncate font-mono text-[var(--text-meta)] text-muted">geçmiş</span>
        )}
      </div>

      <div id="yan-cubuk-govde" className="flex min-h-0 flex-1 flex-col">
        {/* ✏ YENİ SOHBET — kapalıyken bile görünür (kullanıcının açık şartı). */}
        <div className="px-2 pb-2">
          <button
            onClick={onYeniSohbet}
            title="Yeni sohbet"
            aria-label="Yeni sohbet"
            className={
              acik
                ? "flex h-10 w-full items-center gap-2 rounded-[var(--radius-btn)] border border-[var(--surface-kenar)] bg-[var(--surface-2)] px-3 text-left text-[var(--text-panel)] text-foreground transition-colors hover:border-accent/50"
                : ikonBtn
            }
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
              <path d="M12 20h9" />
              <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z" />
            </svg>
            {acik && <span>Yeni sohbet</span>}
          </button>
        </div>

        {/* 🔍 ARA — rayda ikon, açıkken alan. */}
        <div className="px-2 pb-2">
          {acik ? (
            <input
              value={ara}
              onChange={(e) => setAra(e.target.value)}
              placeholder="Sohbetlerde ara"
              aria-label="Sohbetlerde ara"
              className="h-9 w-full rounded-[var(--radius-btn)] border border-[var(--surface-kenar)] bg-[var(--surface-2)] px-3 text-[var(--text-panel)] outline-none placeholder:text-muted focus:border-accent/60"
            />
          ) : (
            <button onClick={degistir} title="Sohbetlerde ara" aria-label="Sohbetlerde ara" className={ikonBtn}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                <circle cx="11" cy="11" r="7" />
                <path d="m20 20-3.5-3.5" />
              </svg>
            </button>
          )}
        </div>

        {/* ── GEÇMİŞ — `HistoryPanel` buraya ERİDİ (panel 13 → 12) ───────────── */}
        <div className="min-h-0 flex-1 overflow-auto px-2">
          {acik && (
            <>
              <HataSeridi metin={hata} onKapat={() => setHata(null)} />
              <GeriAlSeridi
                etiket={silinen?.title ?? null}
                onGeriAl={async () => {
                  await geriAl.mutateAsync(silinen!.id);
                }}
              />
              {isLoading ? (
                <p className="px-1 py-2 text-[var(--text-meta)] text-muted">yükleniyor…</p>
              ) : gruplar.length === 0 ? (
                <p className="px-1 py-2 text-[var(--text-meta)] text-muted">
                  {ara ? "eşleşen sohbet yok" : "henüz kayıtlı sohbet yok"}
                </p>
              ) : (
                gruplar.map(([baslik, satirlar]) => (
                  <section key={baslik} className="mb-3">
                    <h3 className="px-1 pb-1 text-[var(--text-meta)] uppercase tracking-wide text-muted">
                      {baslik}
                    </h3>
                    <ul className="space-y-0.5">
                      {satirlar.map((c) => (
                        <li
                          key={c.id}
                          className={`group flex items-center gap-1 rounded-[var(--radius-chip)] transition-colors ${
                            c.session_id === aktifSessionId
                              ? "bg-accent/[0.10]"
                              : "hover:bg-[var(--surface-3)]"
                          }`}
                        >
                          <button
                            onClick={() => onResume(c.id)}
                            // ⚠ Kırpılmış başlığın tam hâli `title`'da: *kırpılmış bir
                            // metni ipucusuz göstermek, kullanıcıyı tahmine zorlar.*
                            title={`${c.title || "(başlıksız)"} — ${new Date(c.updated_at).toISOString()}`}
                            className="min-w-0 flex-1 px-2 py-2 text-left"
                          >
                            {/* 🔴 Başlık = ilk kullanıcı sorusu; asla "Yeni sohbet".
                                Jenerik başlık tanımayı imkânsızlaştırır. */}
                            <div className="truncate text-[var(--text-panel)] text-foreground">
                              {c.title || "(başlıksız)"}
                            </div>
                          </button>
                          <button
                            onClick={() => {
                              // ⚠ Ad silmeden ÖNCE yakalanır: silindikten sonra liste
                              // tazelenir ve satır kaybolur — o an adı sormanın yeri kalmaz.
                              setSilinen({ id: c.id, title: c.title || "Sohbet" });
                              sil.mutate(c.id);
                            }}
                            disabled={sil.isPending}
                            title="Sohbeti sil"
                            aria-label="Sohbeti sil"
                            className="shrink-0 px-2 py-2 font-mono text-sm text-muted opacity-0 transition-opacity hover:text-[var(--negative)] group-hover:opacity-100 focus:opacity-100"
                          >
                            ×
                          </button>
                        </li>
                      ))}
                    </ul>
                  </section>
                ))
              )}
            </>
          )}
        </div>

        {/* ── ALT: kabuk — 🔴 SİNSİ DÖRTLÜ dahil ──────────────────────────────
            Bağlantı rozeti · kimlik şeridi · çıkış · tema bugüne kadar `layout.tsx`'te
            sabit duruyordu ve rail'in İÇİNDE DEĞİLDİ. Envanter bunları *"rail'i
            taşıdım"* diyen birinin atlayacağı ilk dört şey diye işaretledi. */}
        <div className="shrink-0 border-t border-[var(--surface-kenar)] p-2">
          <div className={acik ? "grid grid-cols-2 gap-1" : "flex flex-col gap-1"}>
            <BolumDugmesi acik={acik} etiket="Bildirimler" secili={acikBolum === "bildirimler"}>
              <NotificationsBell onOpen={() => onBolum(acikBolum === "bildirimler" ? null : "bildirimler")} />
            </BolumDugmesi>
            {panolarVar && (
              <CubukDugmesi
                acik={acik}
                etiket="Panolar"
                secili={acikBolum === "panolar"}
                onClick={() => onBolum(acikBolum === "panolar" ? null : "panolar")}
                ikon={
                  <>
                    <rect x="3" y="3" width="7" height="9" />
                    <rect x="14" y="3" width="7" height="5" />
                    <rect x="14" y="12" width="7" height="9" />
                    <rect x="3" y="16" width="7" height="5" />
                  </>
                }
              />
            )}
            {incelemeVar && (
              <CubukDugmesi
                acik={acik}
                etiket="Ölçü inceleme"
                onClick={onInceleme}
                ikon={
                  <>
                    <path d="M9 11l3 3L22 4" />
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                  </>
                }
              />
            )}
            <TemaDugmesi acik={acik} />
            <CubukDugmesi
              acik={acik}
              etiket="Yardım"
              secili={acikBolum === "yardim"}
              onClick={() => onBolum(acikBolum === "yardim" ? null : "yardim")}
              ikon={<><circle cx="12" cy="12" r="9" /><path d="M9.5 9a2.5 2.5 0 1 1 3 2.4V13" /><path d="M12 17h.01" /></>}
            />
            {onKanitArsivi && (
              <CubukDugmesi
                acik={acik}
                etiket="Kanıt geçmişi"
                onClick={onKanitArsivi}
                ikon={<><path d="M9 12h6M9 16h6M9 8h2" /><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" /><path d="M14 3v5h5" /></>}
              />
            )}

            <CubukDugmesi
              acik={acik}
              etiket="Ayarlar"
              secili={acikBolum === "ayarlar"}
              onClick={() => onBolum(acikBolum === "ayarlar" ? null : "ayarlar")}
              ikon={<><circle cx="12" cy="12" r="3" /><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" /></>}
            />
          </div>

          {/* ── KİMLİK · DURUM · ÇIKIŞ — 🔴 SİNSİ ÜÇLÜ, artık kabuğun İÇİNDE ────
              Bunlar `layout.tsx`'te **sabit konumlu** duruyordu ve `right-2`
              değeriyle **ikon şeridinin içini** işaret ediyordu. FAZ 2 şeridi
              kaldırınca öksüz kaldılar: kaybolmadılar ama **dayandıkları yüzey
              gitti**.

              ⚠ *Sabit konumlu bir öge, dayandığı yüzey kaldırıldığında kaybolmaz —
              öksüz kalır. Ve öksüz bir öge, hatalı bir öğeden daha zor fark edilir,
              çünkü hâlâ görünür.*

              Öteki sayfalarda (`/review`, `/brand`) sabit kopyaları çizmeye devam
              ediyor; ana sayfada susuyorlar (`gomulu` kipi). */}
          <div className="mt-2 flex items-center gap-1 border-t border-[var(--surface-kenar)] pt-2">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center">
              <ConnectionBadge gomulu />
            </div>
            {acik && (
              <div className="min-w-0 flex-1 truncate">
                <KimlikSeridi gomulu />
              </div>
            )}
            <div className="shrink-0">
              <LogoutButton gomulu />
            </div>
          </div>
        </div>
      </div>
    </nav>
    </>
  );
}

/** Rayda ikon, açıkken ikon + etiket. */
function CubukDugmesi({
  acik, etiket, ikon, onClick, secili,
}: {
  acik: boolean; etiket: string; ikon: React.ReactNode; onClick: () => void; secili?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      title={etiket}
      aria-label={etiket}
      aria-pressed={secili}
      className={`flex h-10 items-center gap-2 rounded-[var(--radius-btn)] px-2 text-muted transition-colors hover:bg-[var(--surface-3)] hover:text-foreground ${
        secili ? "bg-[var(--surface-3)] text-foreground" : ""
      } ${acik ? "" : "w-10 justify-center"}`}
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
        {ikon}
      </svg>
      {acik && <span className="truncate text-[var(--text-meta)]">{etiket}</span>}
    </button>
  );
}

/** Zil bileşeni kendi rozetini taşıdığı için sarmalanır (okunmamış sayacı kaybolmasın). */
function BolumDugmesi({
  acik, etiket, children, secili,
}: { acik: boolean; etiket: string; children: React.ReactNode; secili?: boolean }) {
  return (
    <div
      title={etiket}
      className={`flex h-10 items-center gap-2 rounded-[var(--radius-btn)] px-2 transition-colors hover:bg-[var(--surface-3)] ${
        secili ? "bg-[var(--surface-3)]" : ""
      } ${acik ? "" : "w-10 justify-center"}`}
    >
      {children}
      {acik && <span className="truncate text-[var(--text-meta)] text-muted">{etiket}</span>}
    </div>
  );
}

/** Tema anahtarı — **üç** durumlu: sistem → açık → karanlık → sistem.
 *
 * ⚠ *"Karar vermedim"* hâlini yok etmek, kullanıcının işletim sistemi tercihini
 * sessizce ezmek olurdu. İkon duruma göre değişir ve `title` o durumu **söyler**:
 * bir toggle'ın hangi konumda olduğunu tahmin ettirmek, onu bir sürprize çevirir. */
function TemaDugmesi({ acik }: { acik: boolean }) {
  // 🔴 Tema artık bir **dış depodur** (`lib/tema.ts`), bileşen durumu değil: iki
  // anahtar da (bu ve ötekisi) aynı değeri okur ve biri değişince öteki **anında**
  // güncellenir. Eskiden her biri kendi `useState`ini tutuyordu ve ayrışıyorlardı.
  // ⚠ `useSyncExternalStore` hidrasyonu da çözer: sunucuda `"sistem"`, istemcide
  // gerçek değer — React'ın garantisi, bizim dikkatimiz değil.
  const tema = useSyncExternalStore(temaAbone, temaOku, () => "sistem" as Tema);
  useEffect(() => { temaBaslat(); }, []);
  const setTema = (t: Tema) => temaUygula(t);
  const sonraki: Record<Tema, Tema> = { sistem: "light", light: "dark", dark: "sistem" };
  const etiket: Record<Tema, string> = {
    sistem: "Tema: sistem (işletim sistemine uyar)",
    light: "Tema: açık",
    dark: "Tema: karanlık",
  };
  const isaret: Record<Tema, string> = { sistem: "◐", light: "☀", dark: "☾" };
  return (
    <button
      onClick={() => {
        const y = sonraki[tema];
        temaUygula(y);
        setTema(y);
      }}
      aria-label={etiket[tema]}
      title={`${etiket[tema]} — değiştirmek için tıkla`}
      className={`flex h-10 items-center gap-2 rounded-[var(--radius-btn)] px-2 text-muted transition-colors hover:bg-[var(--surface-3)] hover:text-foreground ${
        acik ? "" : "w-10 justify-center"
      }`}
    >
      <span className="font-mono text-[13px]" aria-hidden>{isaret[tema]}</span>
      {acik && <span className="truncate text-[var(--text-meta)]">Tema</span>}
    </button>
  );
}
