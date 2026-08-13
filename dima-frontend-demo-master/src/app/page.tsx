"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useMemo, useRef, useState } from "react";
import { apiErrorMessage, ask, askCube, getConversation, postMakro, uploadDataset } from "@/lib/api-client";
import { AnalysisCanvas } from "@/components/AnalysisCanvas";
import { ChatPanel } from "@/components/ChatPanel";
import { ConnectionReviewPanel } from "@/components/ConnectionReviewPanel";
import { DashboardsPanel } from "@/components/DashboardsPanel";
import { DashboardView } from "@/components/DashboardView";
import { FloatingControls } from "@/components/FloatingControls";
import { HelpPanel } from "@/components/HelpPanel";
import { HistoryPanel } from "@/components/HistoryPanel";
import { Landing } from "@/components/Landing";
import { NotificationsPanel } from "@/components/NotificationsBell";
import { ReportPanel } from "@/components/ReportPanel";
import { SchedulesPanel } from "@/components/SchedulesPanel";
import { SchemaPanel } from "@/components/SchemaPanel";
import { SettingsDrawer } from "@/components/SettingsDrawer";
import TercihlerPanel from "@/components/TercihlerPanel";
import { useHistory } from "@/stores/history";
import { useFeature } from "@/lib/useFeature";
import { usePermission } from "@/lib/usePermission";
import { groupIntoThreads, mintThreadId, replyAnchorLabel, sonBakilanEtiketler } from "@/lib/threads";
import type { AskResponse, CubeQuery} from "@/lib/types";
import { DcmAkisi } from "@/components/DcmAkisi";

type Drawer = "settings" | "help" | "notifications" | "history" | "dashboards" | null;

// Oturum kimliği — crypto.randomUUID yalnız güvenli bağlamda (https/localhost) var;
// http://*.localtld'de yok, bu yüzden fallback.
function makeSessionId(): string {
  try {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
      return crypto.randomUUID();
    }
  } catch {
    /* güvenli bağlam değil */
  }
  return `s-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
}

// Dosya → base64 (data-url önekini at) — /ask/upload multipart yerine JSON+base64 alır.
function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(String(r.result).split(",")[1] ?? "");
    r.onerror = () => reject(r.error);
    r.readAsDataURL(file);
  });
}

export default function Home() {
  // §B (1 Ağustos 2026) — konu/thread modeli: eski tek-rapor `active` state'i YERİNE
  // `activeThreadId` — sağ panel artık TEK bir AskResponse değil, aktif thread'in TÜM
  // item dizisini (bkz. `activeThread` altta) gösterir.
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  // Takip bağlamı: bir sonraki mesajla gönderilecek CubeQuery. Rapor VE clarify notu (kısmi
  // cube_query) bunu günceller — "bu ay" chip'i doğru sorguya uygulansın (ADR-0007 Faz C).
  const [contextCq, setContextCq] = useState<AskResponse["cube_query"]>(null);
  // 🔴🔴 `§RD` — **BELGE BAĞLAMI: `contextCq`'nun KARDEŞİ.**
  //
  // ⊙ Ölçüldü (curl, 2026-08-10): *«rapora kârlılık da ekle»* → sıradan bir sorgu; `rapor`
  // yok. Sebep: bağlam olarak yalnız **son fiş** gidiyordu ve bir raporun son fişi, raporun
  // **kendisi değildir**. Backend `previous_rapor`'u okur; sunucu belgeyi **saklamaz**
  // (`PANO` fiilinin kendi kuralı) — bağlamı istemci taşır, tıpkı `cube_query` gibi.
  //
  // ⚠ Ve bu alan bir demet boyunca **yetim** kaldı: backend okuyordu, istemci
  // doldurmuyordu. Kapı yakaladı (`test_K2c`) — *tanım GÖNDERİM DEĞİLDİR.*
  const [contextRapor, setContextRapor] = useState<AskResponse["rapor"]>(null);
  // 🔴 `G2` — DİYALOG DURUMU YANKISI. `contextCq`'nun KARDEŞİ: aynı yaşam döngüsü, aynı
  // sıfırlanma noktaları. Sunucu oturum saklamaz; *"sorduğunu hatırlamak"* bu yankıya
  // bağlıdır (`backend/app/schemas.py:82-86` · `context.py::KURAL_DEVAM`).
  // ⚠ Bir demet boyunca EKSİKTİ → `KURAL_DEVAM` üretimde hiç ateşlenmedi.
  const [diyalogDurumu, setDiyalogDurumu] =
    useState<AskResponse["diyalog_durumu"]>(null);
  // Strict-agentic (wren_sql) takip bağlamı: bir önceki /ask cevabının SQL'i — cube_query'den
  // AYRI (bkz. lib/types.ts AskRequest.prev_sql); "aylara göre" gibi bir takip mesajı backend'de
  // bu SQL'i düzenleyerek yanıtlanır (generate_followup_sql), sıfırdan bağlamsız üretmez.
  const [prevSql, setPrevSql] = useState<string | null>(null);
  // Görünüm ipucu ("grafik ver") — sağ paneldeki raporun görünümünü değiştirir.
  const [viewHint, setViewHint] = useState<{ kind: string; nonce: number } | null>(null);
  const [drawer, setDrawer] = useState<Drawer>(null);
  /** 🔴 FAZ 7.6 — **dar ekran sekmesi** (<1024). Masaüstünde bu durum HİÇ okunmaz;
   *  iki bölme yan yanadır. ⚠ Varsayılan: dar bir ekranda ilk gösterilecek şey **soru
   *  sorma yeridir** — boş bir sonuç bölmesi, kullanıcıya ne yapacağını söylemez.
   *
   *  🔴 **TEK CHAT (2026-08-13): varsayılan `"sohbet"` → `"sonuc"`.** Kural değişmedi,
   *  **adresi** değişti: soru kutusu artık `ReportPanel`'in altında. Eski varsayılan
   *  bırakılsaydı dar ekranda açılan ilk bölme, içinde **hiçbir girdi kutusu olmayan**
   *  thread listesi olurdu — kuralın harfi korunup amacı kaybedilirdi. */
  const [darSekme, setDarSekme] = useState<"sohbet" | "sonuc">("sonuc");
  // YOL SINIRI (Faz F2) — oturum boyunca kalıcı bir tercih: "yalnız küpün kanıtladığı
  // cevapları göster". `null` = sınır yok (bugünkü davranış, hiçbir şey değişmez).
  const [yolSiniri, setYolSiniri] = useState<"deterministik" | "llm" | null>(null);
  /** FAZ 7.11 — DCM modu. ⚠ Bir **kısıtlamadır**: varsayılanı `off` ve istemeden
   *  açılırsa kullanıcı ürünü bozuk sanar (*"neden yazamıyorum?"*). */
  const dcmModu = useFeature("ui_dcm_modu");
  // 🔴 FAZ 5.14 — HIZLI ↔ DERİN. ⚠ Seçim **thread'e değil SORUYA** bağlıdır ve her
  // mesajda **sıfırlanır** (aşağıda `onSettled`): bir mod'u yapıştırmak, kullanıcının
  // bir kez verdiği kararı ona sormadan her turda yeniden uygulamak olurdu — ve o karar
  // bir sonraki soruda yanlış olabilir. *Yapışkan bir ayar, unutulmuş bir ayardır.*
  const [mod, setMod] = useState<"hizli" | "derin" | null>(null);
  const hizliDerinAcik = useFeature("hizli_derin");
  // FAZ 2.3 — KAPSAM MERCEĞİ. Bayrak kapalıysa anahtar HİÇ çizilmez (onKapsam verilmez):
  // bir görünürlük aracı, kapalıyken kullanıcıya var olduğunu bile söylememelidir.
  const [kapsam, setKapsam] = useState<"departman" | "genel" | "portfoy">("genel");
  const kapsamAcik = useFeature("kapsam_mercegi") !== "off";
  // "Ayarlar" drawer'ı içi iki sekmeli (Faz 4.5): mevcut şema görünümü + DB bağlama
  // sihirbazı — YENİ bir rail ikonu/Drawer değeri EKLEMEDEN, en düşük riskli entegrasyon.
  const [settingsTab, setSettingsTab] =
    useState<"sema" | "baglanti" | "zamanlamalar" | "tercihler">("sema");
  // Açık pano (main-area overlay) — set ise chat/rapor yerine pano grid'i gösterilir (§9).
  const [openDashboard, setOpenDashboard] = useState<string | null>(null);
  const dashStage = useFeature("dashboards");
  const canReview = usePermission("measure:read");
  const router = useRouter();
  const [startedLatch, setStarted] = useState(false);
  const [sessionId, setSessionId] = useState(makeSessionId);
  const qc = useQueryClient();
  const items = useHistory((s) => s.items);
  const addHistory = useHistory((s) => s.add);
  const loadHistory = useHistory((s) => s.load);
  const clearHistory = useHistory((s) => s.clear);
  // §B Adım 1 — `items` store'da YENİ→ESKİ (bkz. stores/history.ts); groupIntoThreads
  // KRONOLOJİK (eski→yeni) girdi bekler (ChatPanel'in bugün zaten yaptığı AYNI çevirme).
  const threads = useMemo(() => groupIntoThreads([...items].reverse()), [items]);
  const activeThread = useMemo(
    () => threads.find((t) => t.id === activeThreadId) ?? null,
    [threads, activeThreadId],
  );
  // Aktif thread'in EN SON raporlanabilir (result/kpi taşıyan) item'ı — "tuval'e ekrandaki
  // mevcut raporu ekle" butonunun hedefi (eski tek-rapor `active`'in yerini alır).
  const latestReportable = useMemo(() => {
    if (!activeThread) return null;
    for (let i = activeThread.items.length - 1; i >= 0; i--) {
      const it = activeThread.items[i];
      if (it.result || it.kpi) return it;
    }
    return null;
  }, [activeThread]);

  // Faz 4.11 — Analiz Tuvali (dış yol haritası 2.6+2.10): EKLEYİCİ, opsiyonel ikinci görünüm.
  // Thread akışı (activeThread) HİÇ değişmiyor; tuval modu açıkken ÜSTÜNE, her yeni gerçek
  // rapor (soru/chip/sonraki-adım/öneri) `canvasItems`'a da eklenir — üsttekini SİLMEZ.
  // §B'nin thread'i "AYNI konunun akışı", tuval ise "FARKLI konuları birleştirme" içindir
  // (kullanıcının kendi ayrımı) — ikisi BAĞIMSIZ, bu dosyada birbirine dokunmaz.
  const [canvasMode, setCanvasMode] = useState(false);
  const [canvasItems, setCanvasItems] = useState<AskResponse[]>([]);
  const addToCanvas = (data: AskResponse) => {
    if (!canvasMode) return;
    if (!(data.result || data.kpi)) return; // yalnız gerçek rapor/KPI (not/clarify değil)
    setCanvasItems((prev) => [...prev, data]);
  };
  const reorderCanvas = (from: number, to: number) => {
    setCanvasItems((prev) => {
      const next = [...prev];
      const [moved] = next.splice(from, 1);
      next.splice(to, 0, moved);
      return next;
    });
  };
  const removeFromCanvas = (index: number) => {
    setCanvasItems((prev) => prev.filter((_, i) => i !== index));
  };

  // Resume: kayıtlı sohbeti yükle — mesajlar (seq eski→yeni) store'a newest-first konur;
  // session_id o sohbete geçer (takip soruları aynı sohbete eklenir).
  const resumeConversation = async (id: string) => {
    const det = await getConversation(id);
    const msgs = [...det.messages].reverse(); // seq artan → store newest-first
    loadHistory(msgs);
    setSessionId(det.session_id);
    // NOT: `note` bir raporun VARLIĞINI dışlamaz (Faz 1.5 — konu-değişimi cevapları hem
    // `note` hem gerçek `result` taşıyabilir, KPI kartlarıyla aynı desen). "Son rapor" =
    // gerçek sonuç taşıyan (ya da KPI) SON mesaj, notu olsun ya da olmasın.
    const lastReport = msgs.find((m) => m.result || m.kpi) ?? null;
    // §B — "sohbetin en son içinde olduğu thread" (bugünkü "son raporu göster"
    // mantığının thread-seviyesine genellenmesi). det.messages ZATEN kronolojik (seq artan).
    // Bağlam (contextCq) ÖNCEDEN hep null'a sıfırlanıyordu (küçük bir tutarsızlık) — artık
    // "eski bir thread'e yeniden girme" (onSelectThread) ile AYNI ilke: thread'in KENDİ SON
    // item'ından geri yüklenir, "kaldığı yerden devam" tutarlı çalışır.
    const resumedThreads = groupIntoThreads(det.messages);
    setActiveThreadId(resumedThreads.at(-1)?.id ?? null);
    setContextCq(lastReport?.cube_query ?? null);
    setContextRapor(lastReport?.rapor ?? null);   // `§RD` — kardeş alan, aynı yaşam döngüsü
    setDiyalogDurumu(lastReport?.diyalog_durumu ?? null);
    setCanvasItems([]); // tuval sohbet-oturumu kapsamlı — devralınan sohbette sıfırdan başlar
    setViewHint(lastReport?.view_hint ? { kind: lastReport.view_hint, nonce: Date.now() } : null);
    setPrevSql(lastReport?.sql || null);
    setStarted(true);
    setDrawer(null);
  };

  const newChat = () => {
    setSessionId(makeSessionId());
    clearHistory();
    setActiveThreadId(null);
    setContextCq(null);
    setContextRapor(null);
    setDiyalogDurumu(null);
    setPrevSql(null);
    setCanvasItems([]); // tuval sohbet-oturumu kapsamlı — yeni sohbet sıfırdan başlar
    setStarted(false);
    setDrawer(null);
  };

  // Faz 4.12 (1 Ağustos 2026) — dış yol haritası 2.9 "canlı düşünme adımları": backend
  // Discovery'yi arka-plana kuyrukladıysa (ask_async_discovery bayrağı) api-client.ts
  // bunu poll ederken biriken adımları BURAYA iletir; ChatPanel statik "yürütülüyor…"
  // yerine SON adımı gösterir. Bayrak kapalıyken (varsayılan) callback hiç tetiklenmez.
  const [liveTrace, setLiveTrace] = useState<string[]>([]);
  // FAZ 1.12 · AI Act Md.14 — DURDURMA. Yalnız arka-plana kuyruklanan (uzun Discovery)
  // işlerde dolar; senkron yolda `job_id` hiç gelmez → düğme de hiç görünmez. `ask()`
  // bunu iş bitince/hata alınca `null`'a çeker (finally) — düğme asılı kalmaz.
  const [aktifJobId, setAktifJobId] = useState<string | null>(null);

  // §B düzeltmesi (1 Ağustos 2026) — REDDEDİLEN ilk sürümün hatası: `is_new_topic`
  // (yalnızca "bu cevap bağlam taşıdı mı" anlamına gelen bir backend sinyali) yanlışlıkla
  // thread sınırı kararına da karıştırılmıştı. ARTIK thread sınırları YALNIZCA kullanıcının
  // HANGİ komposer'ı kullandığına bağlı — bu discriminated-union bunu somutlaştırır:
  // "new" (sol komposer, HER ZAMAN taze/bağlamsız — aktif thread olsun ya da olmasın),
  // "continue" (sağ panelin kendi komposer'ı, aktif thread'in GÜNCEL bağlamıyla devam),
  // "reply"/"reply-multi" (bir karta/kartlara "yanıtla" — bağlam o ÇAPA kart(lar)dan gelir,
  // sonuç yine de thread'in SONUNA eklenir, yalnız `reply_to_label` ile hangi karta
  // bağlandığı görünür kalır — kullanıcı kronolojinin bozulmasını istemedi).
  // FAZ S · STEERING — her isteğe bir SIRA numarası. Komposer koşarken kilitli DEĞİL
  // (bilerek: "dur, onu değil" diyebilmek ürünün vaadi), dolayısıyla iki istek aynı anda
  // uçabilir. Ölçülen kusur: YAVAŞ olan SONRA çözülünce `onSuccess` bağlamı/thread'i
  // GERİ ALIYOR — kullanıcı yön veriyor, sistem sessizce eski cevaba dönüyor.
  //
  // Sıra numarası bunu kapatır: geç gelen cevap KAYBOLMAZ (geçmişe yazılır — "sessiz
  // iptal YOK") ama AKTİF bağlamı ele geçiremez.
  const istekSirasi = useRef(0);

  type AskMutationVars =
    | { kind: "new"; question: string; sira?: number }
    | { kind: "continue"; question: string; sira?: number }
    // `hucre` (Faz G2): kullanıcı grafikte BİR HÜCREYE tıklayıp onun hakkında sorduysa
    // koordinat backend'e gider ve konuşma O hücrenin alt-sorgusu üstünde yürür.
    | { kind: "reply"; question: string; threadId: string; anchorIndex: number;
        hucre?: { dimension: string; value: string }; sira?: number }
    | { kind: "reply-multi"; question: string; threadId: string; anchorIndex: number;
        extraIndices: number[]; sira?: number };

  const mutation = useMutation<AskResponse, unknown, AskMutationVars>({
    mutationFn: (vars) => {
      setLiveTrace([]);
      if (vars.kind === "new") {
        // Sol komposer: cube_query/prev_sql/history/thread_id HEPSİ boş — gerçekten taze
        // bir istek, aktif thread'in bağlamından TAMAMEN bağımsız.
        return ask(
          // ⚠ `diyalog_durumu` de BİLEREK yok: sol komposer "gerçekten taze" demektir,
          // bekleyen bir soruyu oradan cevaplamak yeni bir konu açmaktır.
          { question: vars.question, cube_query: null, prev_sql: null, history: [],
            diyalog_durumu: null, session_id: sessionId, thread_id: null },
          setLiveTrace,
          setAktifJobId,
        );
      }
      if (vars.kind === "continue") {
        // Sağ panelin kendi komposer'ı — eski TEK komposer'ın bağlamsal davranışının
        // AYNISI, yalnız artık ayrı bir giriş noktasından tetikleniyor.
        return ask(
          {
            question: vars.question,
            cube_query: contextCq,
            previous_rapor: raporKimlikleri(contextRapor),   // `§RD`+`§RY`
            // 🔴 `G2` — bekleyen soru bu turda cevaplanıyor olabilir. Yankı olmadan
            // sunucu turu `KURAL_TAZE` sayar ve "mart" tanınmayan bir soru olur.
            diyalog_durumu: diyalogDurumu,
            prev_sql: prevSql,
            history: (activeThread?.items ?? []).map((i) => i.question).slice(-8),
            session_id: sessionId,
            thread_id: activeThreadId,
          },
          setLiveTrace,
          setAktifJobId,
        );
      }
      // "reply" | "reply-multi" — bağlam ÇAPA karttan gelir, thread'in GÜNCEL bağlamından
      // DEĞİL (thread'in son mesajı bambaşka bir konuda olabilir). `history` de anchor'ın
      // KENDİ index'ine kadar kesilir — backend'in `body.history[-1]`'i "önceki soru" sayan
      // İKİ noktası (Discovery takip + VQR chip-öğrenme) `prev_sql` ile TUTARLI kalsın diye.
      const t = threads.find((th) => th.id === vars.threadId) ?? null;
      const anchor = t?.items[vars.anchorIndex] ?? null;
      const historyThroughAnchor = (t?.items ?? [])
        .slice(0, vars.anchorIndex + 1)
        .map((i) => i.question)
        .slice(-8);
      const extraContext =
        vars.kind === "reply-multi"
          ? vars.extraIndices
              .map((idx) => t?.items[idx])
              .filter((it): it is AskResponse => Boolean(it))
              .map((it) => `${it.question} → ${it.result?.row_count ?? 0} satır`)
          : undefined;
      // FAZ 0.5 — ÇAPA KİMLİĞİYLE: `extra_context` insan-okur ÖZETLER taşır (Discovery
      // grounding'i), bu ise KESİŞTİRİLECEK yapısal sorgulardır. İkisi farklı iştir ve
      // ayrı alanlarda durur — birini ötekinin yerine kullanmak, sunucunun "kesişim mi
      // yoksa metin bağlamı mı" sorusunu belirsiz bırakırdı.
      const extraCubeQueries =
        vars.kind === "reply-multi"
          ? vars.extraIndices
              .map((idx) => t?.items[idx]?.cube_query)
              .filter((cq): cq is CubeQuery => Boolean(cq))
          : undefined;
      return ask(
        {
          question: vars.question,
          cube_query: anchor?.cube_query ?? null,
          // 🔴 `G2` — bağlam ÇAPADAN gelir, thread'in güncelinden değil (bu dalın kendi
          // ilkesi). Diyalog durumu da öyle: çapa bir netleştirme kartıysa ona verilen
          // cevap o bekleyen yuvayı doldurur. *Bir bağlamın parçalarını farklı
          // yerlerden toplamak, bağlamı bozmanın en sessiz yoludur.*
          diyalog_durumu: anchor?.diyalog_durumu ?? null,
          prev_sql: anchor?.sql || null,
          history: historyThroughAnchor,
          session_id: sessionId,
          thread_id: vars.threadId,
          reply_to_label: anchor ? replyAnchorLabel(anchor.question) : null,
          // Çapa KİMLİĞİ — `cube_query` alanı yukarıda AYNEN duruyor (GERİ AL).
          reply_to_cube_query: anchor?.cube_query ?? null,
          reply_to_extra_cube_queries: extraCubeQueries ?? null,
          extra_context: extraContext,
          yol_siniri: yolSiniri,
          mod: hizliDerinAcik ? mod : null,
          anchor: vars.kind === "reply" ? (vars.hucre ?? null) : null,
        },
        setLiveTrace,
        setAktifJobId,
      );
    },
    // 🔴 FAZ 5.14 — **SEÇİM HER MESAJDA SIFIRLANIR.** Başarı da hata da olsa: bir
    // sonraki soru yeni bir karardır. Yapışkan bırakmak, kullanıcının unuttuğu bir
    // ayarın onun cevabını sessizce kesmesi demekti.
    onSettled: () => setMod(null),
    onSuccess: (data, vars) => {
      // FAZ S · STEERING KAPISI — bu cevap HÂLÂ güncel mi?
      // Değilse: geçmişe YAZILIR (kaybolmaz) ama aktif thread/bağlam/görünüm ONUN
      // eline geçmez. Sessizce yutmak da, bağlamı geri almak da yanlış olurdu.
      const guncel = (vars.sira ?? 0) >= istekSirasi.current;
      if (!guncel) {
        data.steering_golgede = true;
        data.thread_id = data.thread_id ?? activeThreadId ?? mintThreadId();
        addHistory(data);
        qc.invalidateQueries({ queryKey: ["conversations"] });
        return;
      }
      // Thread sınırı ARTIK YALNIZCA `vars.kind`'a bağlı — `data.is_new_topic` burada HİÇ
      // OKUNMAZ (reddedilen ilk sürümün TAM olarak bu satırdaki hatası düzeltildi).
      const targetThreadId =
        vars.kind === "new" ? mintThreadId()
        : vars.kind === "continue" ? (activeThreadId ?? mintThreadId())
        : vars.threadId;
      data.thread_id = targetThreadId;
      setActiveThreadId(targetThreadId);
      addHistory(data);
      // Rapor paneli artık `activeThread`'den (yukarıda türetilir) OTOMATİK güncellenir —
      // sayfa-seviyeli AYRI bir "aktif rapor" state'i GEREKMEZ (Faz 1.5'in "note VARLIĞI tek
      // başına raporu göstermeyi engellemez" ilkesi ReportPanel'in kendi `it.result||it.kpi`
      // filtresinde zaten KORUNUYOR).
      addToCanvas(data); // Faz 4.11 — tuval modu açıksa üste EKLENİR (thread akışını değiştirmez)
      // Görünüm ipucu: yeni raporla geldiyse onunla; salt-görünüm yanıtında mevcut rapora.
      if (data.view_hint) setViewHint({ kind: data.view_hint, nonce: Date.now() });
      else if (data.result) setViewHint(null);
      // Bağlam: rapor ya da clarify (kısmi cube_query) her ikisi de bir sonraki mesaj için.
      setContextCq(data.cube_query ?? null);
      setContextRapor(data.rapor ?? null);
      // 🔴 `G2` — durumu yankıla: bir sonraki tur "kaldığı yerden" devam edebilsin.
      setDiyalogDurumu(data.diyalog_durumu ?? null);
      // wren_sql takip bağlamı: sql yoksa (meta/katalog/hata notu) bir sonraki soru
      // bağlamsız (fresh) sayılır — stale SQL'e "düzenleme" uygulanmaz.
      setPrevSql(data.sql || null);
      qc.invalidateQueries({ queryKey: ["conversations"] }); // geçmiş listesi tazelensin
    },
  });

  // 🔴🔴 **TEK CHAT (2026-08-13) — «yeni konu» EDİMİNİN TEK SAHİBİ.**
  //
  // İki düğme bunu çağırır ve ikisi de aynı şeyi söyler: `ChatPanel`'in `+ yeni sohbet`i
  // (eski sol komposer'ın yerine geçti) ve `ReportPanel` çapa çubuğundaki
  // `✕ bağlamı bırak` (`§5.1`). ⚠ İki ayrı gövde yazmak, bir gün yalnız birinin bir
  // alanı sıfırlaması demekti — ve bu depoda o desen (`contextRapor`/`diyalog_durumu`)
  // zaten **iki kez** yetim bıraktı.
  //
  // ⊙ `diyalogDurumu` da sıfırlanır ve bu bir DÜZELTMEDİR: eski satır-içi gövdede yoktu,
  // yani bırakılan bağlamın **bekleyen sorusu** bir sonraki taze soruya sızıyor ve sunucu
  // turu `KURAL_DEVAM` sayıyordu. *Bir bağlamı bırakmak, parçalarından birini elde
  // tutmakla tamamlanmaz.*
  //
  // ⊘ Sohbet GEÇMİŞİNİ silmez (o `newChat`): thread listesi durur, tıklanınca yeniden
  // girilebilir. *«Yeni konu» ile «yeni oturum» aynı şey değildir.*
  const yeniKonu = () => {
    setContextCq(null); setContextRapor(null); setDiyalogDurumu(null);
    setPrevSql(null); setActiveThreadId(null); setViewHint(null);
  };
  const submitNew = (q: string) => {
    setDrawer(null);
    setStarted(true); // ilk sorudan sonra çalışma alanında kal (hata olsa da landing'e dönme)
    mutation.mutate({ kind: "new", question: q, sira: ++istekSirasi.current });
  };
  const submitContinue = (q: string) => {
    setDrawer(null);
    setStarted(true);
    mutation.mutate({ kind: "continue", question: q, sira: ++istekSirasi.current });
  };
  const submitReply = (
    threadId: string,
    anchorIndex: number,
    q: string,
    hucre?: { dimension: string; value: string },
  ) => {
    setDrawer(null);
    setStarted(true);
    mutation.mutate({ kind: "reply", question: q, threadId, anchorIndex, hucre,
                      sira: ++istekSirasi.current });
  };
  const submitReplyMulti = (threadId: string, anchorIndex: number, extraIndices: number[], q: string) => {
    setDrawer(null);
    setStarted(true);
    mutation.mutate({ kind: "reply-multi", question: q, threadId, anchorIndex, extraIndices,
                      sira: ++istekSirasi.current });
  };
  // §B DÜZELTMESİ (1 Ağustos 2026, 2. tur) — öneri-chip'leri ARTIK yalnız sağ panelde
  // (ReportPanel) render ediliyor, HER ZAMAN aktif thread'in İÇİNDE — bu yüzden ayrı bir
  // "pasif thread'i bul" dolambacına GEREK KALMADI, ReportPanel doğrudan `onReply`'i
  // (thread.id zaten elinde) çağırıyor. Eski `submitSuggestionReply`/`threadContaining`
  // KALDIRILDI (dead code).

  // Yorum çubuğu chip düzenlemesi → deterministik /cube (LLM yok); transkripte de düşer.
  //
  // 🔴🔴 `§7 ②` — **ADLANDIRILMIŞ MAKRO DA BURADAN GEÇER, KENDİ MUTASYONUNU AÇMAZ.**
  //
  // İki yol da aynı şeyi yapıyor: **sıfır LLM** ile bir cevap üretip onu aktif thread'e
  // koymak. `onSuccess` gövdesinin tamamı (thread damgası · `addHistory` · `addToCanvas` ·
  // `contextCq`/`contextRapor`/`diyalog_durumu` yankısı · `prevSql` temizliği) ikisi için
  // de **birebir** doğrudur. İkinci bir `useMutation` yazmak o gövdenin ikinci bir sahibi
  // demekti ve bu depoda o desen (`contextRapor` · `diyalog_durumu`) **iki kez** bir alanı
  // yetim bıraktı: biri güncellenir, öteki unutulur.
  //
  // ⊙ Ve bedava iki kazanç: ① `pending` zaten `cubeMutation.isPending`i içeriyor → makro
  // koşarken **bekleme göstergesi** (plan 5 adım koşuyor) kendiliğinden çalışır; ② cevap
  // `raporlanabilir` ise normal `ReportCard`, `source: null` + `note` ise saf-not dalı —
  // yani **dürüst ret** de yeni bir gösterim icat edilmeden görünür.
  //
  // ⚠ `label` makro dalında **kullanılmaz** (uç onu okumaz): kartın başlığı `soru`dur,
  // yani kullanıcının şeritte gördüğü cümle. Bkz. `postMakro`'nun şerhi.
  const cubeMutation = useMutation<AskResponse, unknown, { cq: NonNullable<AskResponse["cube_query"]>; label: string; makro?: { ad: string; soru: string; boyut: string } }>({
    mutationFn: ({ cq, label, makro }) =>
      makro ? postMakro({ ad: makro.ad, capa: cq, boyut: makro.boyut, soru: makro.soru })
      : askCube({ cube_query: cq, label, session_id: sessionId, thread_id: activeThreadId }),
    onSuccess: (data) => {
      // §B — chip düzenlemesi HER ZAMAN aktif thread'e etiketlenir (chip UI'ı zaten yalnız
      // aktif thread'in kartlarında var), asla yeni thread AÇMAZ. `activeThreadId` null
      // olamayacak durumda (savunmacı) yeni bir thread mint edilir.
      const targetThreadId = activeThreadId ?? mintThreadId();
      data.thread_id = targetThreadId;
      setActiveThreadId(targetThreadId);
      addHistory(data);
      addToCanvas(data); // Faz 4.11 — chip/sonraki-adım/öneri tıklaması da tuvale eklenir
      // chip düzenlemesi RAPOR ŞEKLİNİ küçük değiştirir — mevcut görünüm tercihi
      // (ör. panelli) KORUNUR; yeni ipucu yalnız /ask cevabından gelir.
      setContextCq(data.cube_query ?? null);
      setContextRapor(data.rapor ?? null);
      setDiyalogDurumu(data.diyalog_durumu ?? null);
      // /cube deterministik cube_query akışıdır — wren_sql takip bağlamıyla ilgisiz;
      // bir sonraki /ask sıfırdan (fresh) başlasın diye temizlenir.
      setPrevSql(null);
    },
  });

  // Chat-scoped Excel/CSV yükleme (base modu) → dataset hazır notu + örnek sorgular sohbete düşer.
  const uploadMut = useMutation<import("@/lib/types").UploadResponse, unknown, File>({
    mutationFn: async (file) =>
      uploadDataset({
        session_id: sessionId,
        filename: file.name,
        content_b64: await fileToBase64(file),
      }),
    onSuccess: (r, file) => {
      setStarted(true);
      setContextCq(null);
    setContextRapor(null); // yeni veri kaynağı — eski cube bağlamı düşer
      setDiyalogDurumu(null);   // …ve bekleyen soru da o kaynağa aitti
      setPrevSql(null); // yeni veri kaynağı — eski wren_sql takip bağlamı da düşer
      // §B Adım 1 — yeni veri kaynağı = yeni konu: yeni thread mint edilir, pseudo-
      // AskResponse'a AÇIKÇA is_new_topic+thread_id set edilir (ÖNCEDEN ikisi de set
      // edilmiyordu — sessizce eski aktif thread'e karışma riski taşıyordu).
      const newThreadId = mintThreadId();
      setActiveThreadId(newThreadId);
      const cols = r.columns.map((c) => c.orig).join(", ");
      addHistory({
        question: `📎 ${file.name}`,
        sql: "",
        result: null,
        source: null,
        cube_query: null,
        note: `"${r.dataset}" yüklendi — ${r.row_count.toLocaleString("tr-TR")} satır. ` +
          `Kolonlar: ${cols}. Örnek sorularla başlayın:`,
        suggestions: r.suggestions,
        trace: [] as string[],
        is_new_topic: true,
        thread_id: newThreadId,
      } as unknown as AskResponse);
    },
  });
  const onUpload = (file: File) => uploadMut.mutate(file);

  const started = startedLatch || items.length > 0 || mutation.isPending || uploadMut.isPending;
  // §B DÜZELTMESİ (1 Ağustos 2026, 2. tur) — "pending" ARTIK hangi panelin bunu göstereceğine
  // göre AYRILIYOR: "new" (sol komposer, YENİ bir panel/thread yaratıyor) solda; "continue"/
  // "reply"/"reply-multi" (aktif thread'e ekleniyor) sağda (bkz. ReportPanel'in kendi
  // `pending` kullanımı) — ikisi ASLA aynı anda gerçek olamaz (tek `mutation`).
  const isPendingNew = mutation.isPending && mutation.variables?.kind === "new";
  const pendingQuestion = isPendingNew ? mutation.variables?.question : undefined;

  return (
    // pr-12: sağdaki kalıcı ikon kolonu (rail) içeriği örtmesin.
    <div className="h-full pr-12 max-md:pb-12 max-md:pr-0">
      {/* 🔴 FAZ 7.11 — DCM. Bayrak açıkken sohbet yüzeyine **hiç girilmez**: serbest
          metni gizlemek bir görünüm kararıdır, akışı hiç kurmamak bir GARANTİDİR. */}
      {dcmModu ? (
        <DcmAkisi
          sessionId={sessionId}
          onSonuc={(r) => {
            // ⚠ Sonuç **var olan** geçmiş deposuna yazılır: DCM ayrı bir sonuç yolu
            // AÇMAZ — ikinci bir depo, aynı cevabın iki farklı geçmişte yaşaması
            // demek olurdu ve kullanıcı hangisinin doğru olduğunu bilemezdi.
            setStarted(true);
            addHistory(r);
          }}
        />
      ) : openDashboard ? (
        <DashboardView id={openDashboard} onClose={() => setOpenDashboard(null)} />
      ) : !started ? (
        <Landing onSubmit={submitNew} onUpload={onUpload} uploading={uploadMut.isPending} />
      ) : (
        <div className="flex h-full min-h-0 max-lg:flex-col">
          {/* 🔴 Sekme çubuğu YALNIZ dar ekranda. ⚠ `lg:hidden` yeterli değil — çubuk
              DOM'da kalırsa masaüstünde de yükseklik payı ayırır. */}
          <div
            data-no-print
            role="tablist"
            aria-label="Görünüm"
            className="hidden shrink-0 border-b border-hairline max-lg:flex"
          >
            {(["sohbet", "sonuc"] as const).map((k) => (
              <button
                key={k}
                role="tab"
                aria-selected={darSekme === k}
                onClick={() => setDarSekme(k)}
                className={`flex-1 px-3 py-2 font-mono text-[11px] transition-colors ${
                  darSekme === k
                    ? "border-b-2 border-accent text-foreground"
                    : "text-muted"
                }`}
              >
                {k === "sohbet" ? "sohbet" : "sonuç"}
              </button>
            ))}
          </div>
          <section
            data-no-print
            // max-lg: tek sütun — `min-w`/`max-w` MUTLAKA sıfırlanır, yoksa 375px'lik
            // bir ekranda `min-w-[320px]` + sağ bölme yatay taşma üretirdi (V-2'nin
            // ölçtüğü tam kusur).
            className={`flex shrink-0 flex-col border-r border-hairline transition-[width] duration-200 max-lg:w-full max-lg:min-w-0 max-lg:max-w-none max-lg:border-r-0 ${
              darSekme === "sonuc" ? "max-lg:hidden" : ""
            } ${
              activeThreadId
                ? "w-[26%] min-w-[260px] max-w-[340px]"
                : "w-[38%] min-w-[320px] max-w-[440px]"
            }`}
          >
            <ChatPanel
              threads={threads}
              activeThreadId={activeThreadId}
              pending={isPendingNew}
              pendingQuestion={pendingQuestion}
              liveTrace={liveTrace}
              aktifJobId={aktifJobId}
              kapsam={kapsam}
              onKapsam={kapsamAcik ? setKapsam : undefined}
              compact={activeThreadId !== null}
              yolSiniri={yolSiniri}
              onYolSiniri={setYolSiniri}
              mod={hizliDerinAcik ? mod : null}
              onMod={setMod}
              onSelectThread={(t) => {
                // §B (Madde 4+6) — bir thread satırına tıklamak O THREAD'İ sağda aktive
                // eder; bağlam THREAD'İN KENDİ SON item'ından geri yüklenir (tıklanan
                // tarihsel noktadan DEĞİL) — "istediği zaman tekrar girebilir, kaldığı
                // yerden devam eder" sözünün en doğal okunuşu.
                setActiveThreadId(t.id);
                const last = t.items.at(-1) ?? null;
                setContextCq(last?.cube_query ?? null);
                setPrevSql(last?.sql || null);
                setViewHint(null); // yeniden girişte zorla remount YOK — kartlar kendi view_hint'ini kullanır
              }}
              onYeniSohbet={yeniKonu}
              onUpload={onUpload}
              uploading={uploadMut.isPending}
            />
          </section>
          <section
            className={`flex min-w-0 flex-1 flex-col overflow-auto ${
              darSekme === "sohbet" ? "max-lg:hidden" : ""
            }`}
          >
            <div
              data-no-print
              className="flex shrink-0 items-center justify-end gap-2 border-b border-hairline px-3 py-1.5"
            >
              {/* Kullanıcı tuval moduna GEÇ bir noktada geçmiş olabilir — ekrandaki mevcut
                  raporu (soru/chip/geçmiş-seçimi FARK ETMEKSİZİN) elle de ekleyebilsin, yalnız
                  otomatik-eklemenin (chip/sonraki-adım) başladığı ANDAN sonrasına bağlı kalmasın. */}
              {canvasMode && latestReportable && (
                <button
                  onClick={() =>
                    setCanvasItems((prev) =>
                      prev[prev.length - 1] === latestReportable ? prev : [...prev, latestReportable],
                    )
                  }
                  title="Ekrandaki mevcut raporu tuvale ekle"
                  className="flex h-[22px] items-center border border-hairline px-2 font-mono text-[11px] text-neutral-400 transition-colors hover:border-accent hover:text-accent"
                >
                  + şu anki raporu ekle
                </button>
              )}
              <button
                onClick={() => setCanvasMode((m) => !m)}
                title="Tıklanan sonraki-adım/öneri raporlarını biriktiren, sürükle-sıralanabilir ek görünüm"
                className={`flex h-[22px] items-center border px-2 font-mono text-[11px] transition-colors ${
                  canvasMode
                    ? "border-accent/40 text-accent"
                    : "border-hairline text-neutral-400 hover:text-foreground"
                }`}
              >
                🗂 tuval{canvasItems.length > 0 ? ` (${canvasItems.length})` : ""}
              </button>
            </div>
            <div className="min-h-0 flex-1 overflow-auto">
              <ReportPanel
                thread={activeThread}
                pending={(mutation.isPending && !isPendingNew) || cubeMutation.isPending}
                aktifJobId={isPendingNew ? null : aktifJobId}
                viewHint={viewHint}
                onCubeEdit={({ cq, label }) => cubeMutation.mutate({ cq, label })}
                // 🔴 `§7 ②` — makro, `/cube` ile **aynı** mutasyondan geçer (gerekçesi
                // yukarıda). `label` yalnız `/cube` dalının işine yarar; makro dalında
                // kartın başlığını `soru` verir.
                // 🔴 `§45` — öngörü tıklaması **hazır sorguyu koşar** (0 LLM);
                // gerekçe `OneriSeridi.sec()` içinde. İki dal da AYNI koşum
                // yolunu kullanır (`cubeMutation`) — ikinci bir yol `KAT-1`'i
                // bozardı ㊲: makro `makro` alanıyla, öngörü onsuz gider.
                onMakro={(ad, soru, cq, boyut) => cubeMutation.mutate({ cq, label: soru, makro: { ad, soru, boyut } })}
                onSorguKos={(cq, label) => cubeMutation.mutate({ cq, label })}
                // 🔴 `cubeMutation` HATASI DA GÖRÜNÜR OLDU. Eskiden yalnız `mutation`
                // okunuyordu; `/cube` sessizce düşerse kullanıcı **hiçbir şey** görmüyordu.
                // Makro ile bu bir kusurdan bir **ürün boşluğuna** dönüşürdü: boyutsuz bir
                // çapada sunucu 400 + Türkçe gerekçe döner (*«… bir kırılım boyutu ister»*)
                // ve o cümlenin ekrana ulaşması `§7`'nin *«dürüst ret»* şartıdır.
                error={mutation.isError || cubeMutation.isError ? apiErrorMessage(mutation.error ?? cubeMutation.error) : null}
                sessionId={sessionId}
                contextLabel={contextCq ? String(contextCq.cube ?? "rapor") : null}
                // §B — "konudan çık": HEPSİ BİRLİKTE sıfırlanır → panel BOŞALIR ve
                // sonraki soru YENİ bir thread başlatır. Gövde `yeniKonu`'da (yukarıda),
                // çünkü `ChatPanel`'in `+ yeni sohbet` düğmesi AYNI edimdir — iki
                // düğme, TEK sahip.
                onClearContext={yeniKonu}
                onContinue={submitContinue}
                onReply={submitReply}
                onReplyMulti={submitReplyMulti}
                sonBakilanlar={sonBakilanEtiketler(threads)}
                tuval={canvasMode ? (
                  // 🔴🔴 **ÖLÇÜLMÜŞ GERİLEME KAPANDI (2026-08-13).** Tuval eskiden
                  // `ReportPanel`'in **YERİNE** çiziliyordu; «tek chat» kararıyla sol
                  // besteci kaldırılınca bu, tuval kipinde ekranda **hiçbir girdi
                  // kutusu bırakmıyordu** — kullanıcı yazamıyordu. Bir kapsam kararı
                  // değil, taşımanın yan hasarı.
                  //
                  // ⚠ Çare **ikinci bir besteci değil**: tuval artık panelin GÖVDESİ
                  // olarak geçiyor, besteci (ve çapa · öneri şeridi · bekleme/hata)
                  // tek sahibinde kalıyor. Üçüncü bir besteci yazmak, aynı özelliği
                  // üçüncü kez bakmak olurdu — «tek chat» kararının tam sebebi buydu.
                  //
                  // ⊙ Bedava bir kazanç: tuval kipinde sorulan soru `submitContinue`
                  // yolundan geçtiği için cevabı `addToCanvas` **tuvale de** ekler —
                  // yani kullanıcı tuvali artık tuvalden büyütebilir.
                  <AnalysisCanvas
                    items={canvasItems}
                    onReorder={reorderCanvas}
                    onRemove={removeFromCanvas}
                    onClear={() => setCanvasItems([])}
                  />
                ) : null}
              />
            </div>
          </section>
        </div>
      )}

      {/* Aynı ikona ikinci tıklama sheet'i KAPATIR (toggle); farklıysa içerik değişir. */}
      <FloatingControls
        onHistory={() => setDrawer((d) => (d === "history" ? null : "history"))}
        onNotifications={() => setDrawer((d) => (d === "notifications" ? null : "notifications"))}
        onDashboards={
          dashStage
            ? () => setDrawer((d) => (d === "dashboards" ? null : "dashboards"))
            : undefined
        }
        onReview={canReview ? () => router.push("/review") : undefined}
        onHelp={() => setDrawer((d) => (d === "help" ? null : "help"))}
        onSettings={() => setDrawer((d) => (d === "settings" ? null : "settings"))}
      />

      <SettingsDrawer
        open={drawer !== null}
        onClose={() => setDrawer(null)}
        title={
          drawer === "help"
            ? "dima · yardım"
            : drawer === "notifications"
              ? "Bildirimler"
              : drawer === "history"
                ? "Sohbet Geçmişi"
                : drawer === "dashboards"
                  ? "Panolar"
                  : "Ayarlar · Veri Modeli"
        }
      >
        {drawer === "help" ? (
          <HelpPanel onPick={submitNew} />
        ) : drawer === "notifications" ? (
          <NotificationsPanel />
        ) : drawer === "history" ? (
          <HistoryPanel
            onResume={resumeConversation}
            onNewChat={newChat}
            activeSessionId={sessionId}
          />
        ) : drawer === "dashboards" ? (
          <DashboardsPanel
            onOpen={(id) => {
              setOpenDashboard(id);
              setDrawer(null);
            }}
          />
        ) : (
          <div>
            <div className="mb-4 flex gap-1 border-b border-hairline text-xs">
              <button
                onClick={() => setSettingsTab("sema")}
                className={`px-3 py-2 ${settingsTab === "sema" ? "border-b-2 border-accent text-foreground" : "text-muted"}`}
              >
                Şema
              </button>
              <button
                onClick={() => setSettingsTab("baglanti")}
                className={`px-3 py-2 ${settingsTab === "baglanti" ? "border-b-2 border-accent text-foreground" : "text-muted"}`}
              >
                Veri Kaynağı Bağla
              </button>
              <button
                onClick={() => setSettingsTab("zamanlamalar")}
                className={`px-3 py-2 ${settingsTab === "zamanlamalar" ? "border-b-2 border-accent text-foreground" : "text-muted"}`}
              >
                Zamanlamalar
              </button>
              <button
                onClick={() => setSettingsTab("tercihler")}
                className={`px-3 py-2 ${settingsTab === "tercihler" ? "border-b-2 border-accent text-foreground" : "text-muted"}`}
              >
                Tercihler
              </button>
            </div>
            {settingsTab === "sema" ? (
              <SchemaPanel kapsam={kapsamAcik ? kapsam : null} />
            ) : settingsTab === "baglanti" ? (
              <ConnectionReviewPanel />
            ) : settingsTab === "zamanlamalar" ? (
              <SchedulesPanel />
            ) : (
              <TercihlerPanel />
            )}
          </div>
        )}
      </SettingsDrawer>
    </div>
  );
}

/** 🔴🔴 `§RY` — **BELGE BAĞLAMI: SATIRLAR BOŞUNA GİDİYORDU.**
 *
 * ⊙ Ölçüldü (2026-08-10): `previous_rapor` **tam** gönderiliyordu — `pages[][].result.rows`
 * dâhil. Ölçüm aracı `Argüman listesi çok uzun` ile düştü ve kusuru o gösterdi.
 *
 * 🔴 Oysa sunucu yalnız **kimlikleri** okuyor (`plan_tuketici._belge_bolumleri` → yalnız
 * `cube_query`) ve `§RD`'nin kendi şerhi bunu yazıyor: *«planlayıcıya satır gitmez
 * (`G0b`)»*. Yani sunucunun **az önce ürettiği** satırlar bir sonraki turda **geri**
 * taşınıyordu.
 *
 * ⚠ Kırpma **istemcide**: veriyi göndermemek, gönderip sunucuda atmaktan farklıdır —
 * ikincisi bant genişliğini zaten harcamıştır.
 *
 * *Bir aracın sınırına çarpmak, bazen ölçtüğü şeyin kusurunu gösterir.*
 */
function raporKimlikleri(r: AskResponse["rapor"]): AskResponse["rapor"] {
  if (!r) return null;
  return {
    ...r,
    pages: (r.pages ?? []).map((sayfa) =>
      (sayfa ?? []).map((b) => ({ ...b, result: null, viz: null })),
    ),
  };
}
