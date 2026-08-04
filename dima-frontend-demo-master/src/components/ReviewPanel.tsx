"use client";

// Discovery→Promote (Faz 2d) reviewer arayüzü: Discovery (ham-SQL LLM) yolunun ürettiği
// "ölçü adayları" (MeasureCandidate) burada incelenir. analyst yalnız GÖRÜNTÜLER
// (measure:read); admin+ onaylar/reddeder/deprecate eder (measure:approve) — buton
// görünürlüğü backend authorize matrisinden (usePermission), rol semantiği burada
// KOPYALANMAZ. Onay backend'de dry_plan + ad-çakışma kontrolü + altın-vaka zorunluluğu
// taşır; bu form yalnız o alanları toplar, doğrulamayı backend yapar (400/409 mesajı
// olduğu gibi gösterilir).

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import {
  apiErrorMessage,
  approveMeasureCandidate,
  deprecateMeasureCandidate,
  getMeasureBlastRadius,
  previewMeasureCandidate,
  getMeasureCandidate,
  getTerfiKapanis,
  listMeasureCandidates,
  rejectMeasureCandidate,
} from "@/lib/api-client";
import { usePermission } from "@/lib/usePermission";
import type { MeasureCandidate, MeasurePreview } from "@/lib/types";

const STATUS_LABEL: Record<string, string> = {
  draft: "taslak",
  pending_review: "incelemede",
  approved: "onaylandı",
  rejected: "reddedildi",
  deprecated: "gizlendi",
};

const STATUS_TABS = ["draft", "pending_review", "approved", "rejected", "deprecated"] as const;

function StatusBadge({ status }: { status: string }) {
  const cls =
    status === "approved"
      ? "text-emerald-600 border-emerald-600/40"
      : status === "rejected" || status === "deprecated"
        ? "text-neutral-400 border-neutral-400/40"
        : "text-accent border-accent/40";
  return (
    <span className={`border px-1.5 py-0.5 font-mono text-[10px] uppercase ${cls}`}>
      {STATUS_LABEL[status] ?? status}
    </span>
  );
}

function CandidateList({
  status,
  setStatus,
  selected,
  onSelect,
}: {
  status: string;
  setStatus: (s: string) => void;
  selected: string | null;
  onSelect: (id: string) => void;
}) {
  const { data, isLoading } = useQuery({
    queryKey: ["measure-candidates", status],
    queryFn: () => listMeasureCandidates(status || undefined),
  });
  const list = data ?? [];

  return (
    <div className="flex h-full flex-col border-r border-hairline">
      <div className="flex flex-wrap gap-1 border-b border-hairline p-2">
        <button
          onClick={() => setStatus("")}
          className={`border px-2 py-1 font-mono text-[11px] ${
            status === "" ? "border-accent text-accent" : "border-hairline text-neutral-400"
          }`}
        >
          tümü
        </button>
        {STATUS_TABS.map((s) => (
          <button
            key={s}
            onClick={() => setStatus(s)}
            className={`border px-2 py-1 font-mono text-[11px] ${
              status === s ? "border-accent text-accent" : "border-hairline text-neutral-400"
            }`}
          >
            {STATUS_LABEL[s]}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-y-auto">
        {isLoading ? (
          <p className="p-3 font-mono text-[12px] text-neutral-400">yükleniyor…</p>
        ) : list.length === 0 ? (
          <p className="p-3 font-mono text-[12px] leading-relaxed text-neutral-400">
            bu filtrede aday yok — Discovery (ham-SQL) yolu bir soruyu cevapladığında
            burada otomatik biriktirilir.
          </p>
        ) : (
          <ul>
            {list.map((c) => (
              <li key={c.id}>
                <button
                  onClick={() => onSelect(c.id)}
                  className={`w-full border-b border-hairline p-2 text-left transition-colors hover:bg-neutral-500/[0.04] ${
                    selected === c.id ? "bg-neutral-500/[0.06]" : ""
                  }`}
                >
                  <div className="mb-1 flex items-center justify-between gap-2">
                    <StatusBadge status={c.status} />
                    <span className="font-mono text-[10px] text-neutral-400">
                      {new Date(c.created_at).toLocaleDateString("tr-TR")}
                    </span>
                  </div>
                  <div className="truncate font-mono text-[12px] text-foreground">
                    {c.question}
                  </div>
                  {c.cube && c.measure_name && (
                    <div className="truncate font-mono text-[10px] text-neutral-400">
                      {c.cube}.{c.measure_name}
                    </div>
                  )}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function SampleRowsTable({ sample }: { sample: MeasureCandidate["sample_rows"] }) {
  if (!sample || !sample.columns?.length) return null;
  return (
    <div className="overflow-x-auto border border-hairline">
      <table className="w-full font-mono text-[11px]">
        <thead>
          <tr className="border-b border-hairline text-neutral-400">
            {sample.columns.map((c) => (
              <th key={c} className="px-2 py-1 text-left font-normal">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sample.rows.map((row, i) => (
            <tr key={i} className="border-b border-hairline last:border-0">
              {row.map((v, j) => (
                <td key={j} className="px-2 py-1 text-foreground">
                  {String(v ?? "—")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ApproveForm({ candidate }: { candidate: MeasureCandidate }) {
  const qc = useQueryClient();
  const [cube, setCube] = useState(candidate.cube ?? "");
  const [measureName, setMeasureName] = useState(candidate.measure_name ?? "");
  const [expression, setExpression] = useState(candidate.expression ?? "");
  const [type, setType] = useState(candidate.measure_type || "DOUBLE");
  const [label, setLabel] = useState(candidate.label ?? "");
  const [synonyms, setSynonyms] = useState(candidate.synonyms?.join(", ") ?? "");
  const [lowerIsBetter, setLowerIsBetter] = useState(candidate.lower_is_better ?? false);
  const [goldenId, setGoldenId] = useState(candidate.golden_case_id ?? "");
  const [goldenQ, setGoldenQ] = useState(candidate.question);
  const [goldenTags, setGoldenTags] = useState("");
  const [goldenShape, setGoldenShape] = useState(
    cube && measureName ? `{"cube": "${cube}", "measures": ["${measureName}"]}` : "{}",
  );
  const [formError, setFormError] = useState<string | null>(null);
  // Faz 4.2/H2 — ONAY DIFF GÖRÜLMEDEN AÇILMAZ. Yanlış bir ölçünün blast-radius'u
  // kategorik olarak büyüktür (yeni SQL/join/agregasyon → çift sayım, grain uyuşmazlığı)
  // ve inceleme ancak GÖRÜLEN bir değişiklik üzerinde yapılabilir. Backend'de bu uç
  // Faz 4.2'de yazılmıştı ama HİÇ bağlanmamıştı — onaylayan kişi MDL değişikliğini
  // yalnız OLDU BİTTİ olarak görebiliyordu.
  const [preview, setPreview] = useState<MeasurePreview | null>(null);
  // Diff, formun O ANKİ haline aittir. Form değişince damga bayatlar → yeniden bakılmalı.
  const previewImzasi = JSON.stringify([cube, measureName, expression, type, label, synonyms,
                                        lowerIsBetter]);
  const [previewIcin, setPreviewIcin] = useState<string | null>(null);
  const previewGuncel = preview !== null && previewIcin === previewImzasi;

  const onizle = useMutation({
    mutationFn: () =>
      previewMeasureCandidate(candidate.id, {
        cube,
        measure_name: measureName,
        expression,
        type,
        label: label || null,
        synonyms: synonyms.split(",").map((x) => x.trim()).filter(Boolean),
        lower_is_better: lowerIsBetter,
      }),
    onSuccess: (d) => {
      setPreview(d);
      setPreviewIcin(previewImzasi);
      setFormError(null);
    },
    onError: (e) => {
      setPreview(null);
      setFormError(apiErrorMessage(e));
    },
  });

  const approve = useMutation({
    mutationFn: async () => {
      setFormError(null);
      let shape: Record<string, unknown>;
      try {
        shape = JSON.parse(goldenShape || "{}");
      } catch {
        throw new Error("Altın-vaka 'shape' alanı geçerli JSON değil");
      }
      return approveMeasureCandidate(candidate.id, {
        cube,
        measure_name: measureName,
        expression,
        type,
        label: label || null,
        synonyms: synonyms
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        lower_is_better: lowerIsBetter,
        golden_case: {
          id: goldenId,
          q: goldenQ,
          tags: goldenTags
            .split(",")
            .map((s) => s.trim())
            .filter(Boolean),
          expect: "answer",
          shape,
        },
      });
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["measure-candidates"] });
      qc.invalidateQueries({ queryKey: ["measure-candidate", candidate.id] });
    },
    onError: (e) => setFormError(apiErrorMessage(e)),
  });

  const reject = useMutation({
    mutationFn: () => rejectMeasureCandidate(candidate.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["measure-candidates"] });
      qc.invalidateQueries({ queryKey: ["measure-candidate", candidate.id] });
    },
  });

  const field = "w-full border border-hairline bg-transparent px-2 py-1 font-mono text-[12px]";
  const label_ = "mb-1 block font-mono text-[10px] uppercase text-neutral-400";

  return (
    <div className="space-y-3 border border-hairline p-3">
      <div className="font-mono text-[11px] uppercase text-neutral-400">Onay formu</div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={label_}>cube</label>
          <input className={field} value={cube} onChange={(e) => setCube(e.target.value)} />
        </div>
        <div>
          <label className={label_}>ölçü adı</label>
          <input
            className={field}
            value={measureName}
            onChange={(e) => setMeasureName(e.target.value)}
          />
        </div>
      </div>
      <div>
        <label className={label_}>expression (SQL agregatı)</label>
        <input
          className={field}
          value={expression}
          onChange={(e) => setExpression(e.target.value)}
        />
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className={label_}>tip</label>
          <input className={field} value={type} onChange={(e) => setType(e.target.value)} />
        </div>
        <div>
          <label className={label_}>etiket (opsiyonel)</label>
          <input className={field} value={label} onChange={(e) => setLabel(e.target.value)} />
        </div>
      </div>
      <div>
        <label className={label_}>sinonimler (virgülle ayrılmış)</label>
        <input
          className={field}
          value={synonyms}
          onChange={(e) => setSynonyms(e.target.value)}
        />
      </div>
      <label className="flex items-center gap-2 font-mono text-[12px] text-foreground">
        <input
          type="checkbox"
          checked={lowerIsBetter}
          onChange={(e) => setLowerIsBetter(e.target.checked)}
        />
        yüksek = kötü (lower_is_better)
      </label>

      <div className="border-t border-hairline pt-3">
        <div className="mb-2 font-mono text-[11px] uppercase text-neutral-400">
          Altın-vaka (zorunlu — eval/cases.yaml&apos;a eklenir)
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className={label_}>vaka id</label>
            <input className={field} value={goldenId} onChange={(e) => setGoldenId(e.target.value)} />
          </div>
          <div>
            <label className={label_}>etiketler (virgülle)</label>
            <input
              className={field}
              value={goldenTags}
              onChange={(e) => setGoldenTags(e.target.value)}
            />
          </div>
        </div>
        <div className="mt-2">
          <label className={label_}>soru metni</label>
          <input className={field} value={goldenQ} onChange={(e) => setGoldenQ(e.target.value)} />
        </div>
        <div className="mt-2">
          <label className={label_}>beklenen şekil (shape, JSON)</label>
          <textarea
            className={`${field} font-mono`}
            rows={2}
            value={goldenShape}
            onChange={(e) => setGoldenShape(e.target.value)}
          />
        </div>
      </div>

      {formError && (
        <p className="border border-red-500/40 bg-red-500/5 p-2 font-mono text-[11px] text-red-500">
          {formError}
        </p>
      )}
      {candidate.name_conflict && (
        <p className="border border-amber-500/40 bg-amber-500/5 p-2 font-mono text-[11px] text-amber-600">
          Uyarı: &quot;{measureName}&quot; adı hedef cube&apos;da ZATEN var — onay 409 ile
          reddedilecek, farklı bir ad seçin.
        </p>
      )}

      {/* KURU KOŞUM — onayın ön koşulu. Diff'i üretimdeki yazıcının KENDİSİ geçici bir
          kopya üzerinde üretir (taklit değil), böylece incelenen şey gerçekten yazılacak
          olandır. */}
      <div className="border border-hairline p-2">
        <div className="flex items-center justify-between">
          <span className="font-mono text-[10px] uppercase text-neutral-400">
            ne değişecek (kuru koşum)
          </span>
          <button
            onClick={() => onizle.mutate()}
            disabled={onizle.isPending || !cube || !measureName || !expression}
            className="border border-hairline px-2 py-1 font-mono text-[11px] text-neutral-500 transition-colors hover:border-foreground/30 hover:text-foreground disabled:opacity-40"
          >
            {onizle.isPending ? "hesaplanıyor…" : previewGuncel ? "yenile" : "diff'i göster"}
          </button>
        </div>
        {!previewGuncel && (
          <p className="mt-2 font-mono text-[11px] text-neutral-400">
            {preview === null
              ? "Onay için önce değişikliği görmelisin."
              : "Form değişti — diff bayat. Yeniden bak."}
          </p>
        )}
        {previewGuncel && preview && (
          <div className="mt-2 space-y-2">
            <div className="font-mono text-[10px] text-neutral-400">{preview.yaml_path}</div>
            {preview.changed ? (
              <pre className="max-h-64 overflow-auto border border-hairline bg-black/20 p-2 font-mono text-[11px] leading-relaxed">
                {preview.diff.split("\n").map((satir, i) => (
                  <div
                    key={i}
                    className={
                      satir.startsWith("+") && !satir.startsWith("+++")
                        ? "text-emerald-500"
                        : satir.startsWith("-") && !satir.startsWith("---")
                          ? "text-red-500"
                          : satir.startsWith("@@")
                            ? "text-sky-500"
                            : "text-neutral-400"
                    }
                  >
                    {satir || " "}
                  </div>
                ))}
              </pre>
            ) : (
              <p className="font-mono text-[11px] text-amber-600">
                Diff BOŞ — bu onay YAML&apos;da hiçbir şey değiştirmiyor.
              </p>
            )}
            {preview.creates_company_override && (
              <p className="border border-sky-500/40 bg-sky-500/5 p-2 font-mono text-[11px] text-sky-600">
                Diff&apos;te GÖRÜNMEYEN sonuç: bu onay, pack&apos;ten gelen cube&apos;u bu
                şirketin katmanına <strong>taşır</strong> (paylaşılan pack dosyasına
                dokunulmaz). Bundan sonra pack güncellemeleri bu cube&apos;a otomatik
                yansımaz.
              </p>
            )}
          </div>
        )}
      </div>

      <div className="flex gap-2 pt-1">
        <button
          onClick={() => approve.mutate()}
          disabled={
            approve.isPending || !cube || !measureName || !expression || !goldenId ||
            !previewGuncel
          }
          title={previewGuncel ? undefined : "Önce diff'i göster — görülmeden onay yok"}
          className="border border-emerald-600/50 px-3 py-1.5 font-mono text-[12px] text-emerald-600 transition-colors hover:bg-emerald-600/10 disabled:opacity-40"
        >
          {approve.isPending ? "onaylanıyor…" : "✓ onayla"}
        </button>
        <button
          onClick={() => reject.mutate()}
          disabled={reject.isPending}
          className="border border-hairline px-3 py-1.5 font-mono text-[12px] text-neutral-400 transition-colors hover:text-red-500 disabled:opacity-40"
        >
          ✗ reddet
        </button>
      </div>
    </div>
  );
}

function DeprecateBlock({ candidate }: { candidate: MeasureCandidate }) {
  const qc = useQueryClient();
  const [reason, setReason] = useState("");
  const { data: blast } = useQuery({
    queryKey: ["measure-blast-radius", candidate.id],
    queryFn: () => getMeasureBlastRadius(candidate.id, candidate.cube!, candidate.measure_name!),
    enabled: !!candidate.cube && !!candidate.measure_name,
  });
  const deprecate = useMutation({
    mutationFn: () => deprecateMeasureCandidate(candidate.id, reason || undefined),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["measure-candidates"] });
      qc.invalidateQueries({ queryKey: ["measure-candidate", candidate.id] });
    },
  });

  const totalHits = blast
    ? blast.verified_query + blast.dashboard_widget + blast.contract_log_structured +
      blast.contract_log_raw_sql_text_match
    : 0;

  return (
    <div className="space-y-2 border border-hairline p-3">
      <div className="font-mono text-[11px] uppercase text-neutral-400">Geri al (deprecate)</div>
      <p className="font-mono text-[11px] leading-relaxed text-neutral-400">
        Ölçü YAML&apos;dan SİLİNMEZ — yalnız doğal-dil aramadan gizlenir. Eski pano/doğrulanmış-
        sorgu kayıtları kırılmaz.
      </p>
      {blast && (
        <p className="font-mono text-[11px] text-amber-600">
          Yaklaşık {totalHits} potansiyel kullanım bulundu (VQR {blast.verified_query} · pano{" "}
          {blast.dashboard_widget} · kanıt {blast.contract_log_structured}+
          {blast.contract_log_raw_sql_text_match}).
        </p>
      )}
      <input
        className="w-full border border-hairline bg-transparent px-2 py-1 font-mono text-[12px]"
        placeholder="neden (opsiyonel)"
        value={reason}
        onChange={(e) => setReason(e.target.value)}
      />
      <button
        onClick={() => deprecate.mutate()}
        disabled={deprecate.isPending}
        className="border border-red-500/40 px-3 py-1.5 font-mono text-[12px] text-red-500 transition-colors hover:bg-red-500/10 disabled:opacity-40"
      >
        {deprecate.isPending ? "gizleniyor…" : "gizle (deprecate)"}
      </button>
    </div>
  );
}

function CandidateDetail({ id }: { id: string }) {
  const canApprove = usePermission("measure:approve");
  const { data: candidate, isLoading } = useQuery({
    queryKey: ["measure-candidate", id],
    queryFn: () => getMeasureCandidate(id),
  });

  if (isLoading || !candidate) {
    return <p className="p-4 font-mono text-[12px] text-neutral-400">yükleniyor…</p>;
  }

  return (
    <div className="space-y-4 overflow-y-auto p-4">
      <div className="flex items-center gap-2">
        <StatusBadge status={candidate.status} />
        <span className="font-mono text-[10px] text-neutral-400">
          {candidate.company} · {new Date(candidate.created_at).toLocaleString("tr-TR")}
        </span>
      </div>
      <div>
        <div className="mb-1 font-mono text-[10px] uppercase text-neutral-400">Soru</div>
        <p className="font-mono text-[13px] text-foreground">{candidate.question}</p>
      </div>
      <div>
        <div className="mb-1 font-mono text-[10px] uppercase text-neutral-400">
          Discovery&apos;in ürettiği SQL
        </div>
        <pre className="overflow-x-auto border border-hairline p-2 font-mono text-[11px] text-foreground">
          {candidate.sql}
        </pre>
      </div>
      {candidate.sample_rows && (
        <div>
          <div className="mb-1 font-mono text-[10px] uppercase text-neutral-400">
            Örnek satırlar (ilk {candidate.sample_rows.rows.length})
          </div>
          <SampleRowsTable sample={candidate.sample_rows} />
        </div>
      )}
      {candidate.review_note && (
        <p className="border border-hairline p-2 font-mono text-[11px] text-neutral-400">
          not: {candidate.review_note}
        </p>
      )}

      {!canApprove ? (
        <p className="border border-hairline p-2 font-mono text-[11px] text-neutral-400">
          Görüntüleme izniniz var — onaylamak/reddetmek için admin rolü gerekir.
        </p>
      ) : candidate.status === "draft" || candidate.status === "pending_review" ? (
        <ApproveForm candidate={candidate} />
      ) : candidate.status === "approved" ? (
        <DeprecateBlock candidate={candidate} />
      ) : null}
    </div>
  );
}

/** FAZ 3.3 — TERFİ KUYRUĞU KAPANIŞ ORANI.
 *
 * 🔴 *"Her Discovery cevabı bir kapsam boşluğunun belgesidir"* (MIMARI §9) — ama kaçının
 * **kapandığını** kimse ölçmüyordu. *Ölçülmeyen bir kuyruk, kuyruk değil bir çöp kutusudur.*
 *
 * ⚠ **REDDEDİLEN DE KAPANIŞTIR** ve etiket bunu söyler: yalnız onayları saymak, **doğru
 * reddi bir başarısızlık gibi** gösterir ve incelemeciyi onaylamaya iterdi.
 */
function KapanisOrani() {
  const { data } = useQuery({ queryKey: ["terfi-kapanis"], queryFn: getTerfiKapanis });
  if (!data) return null;
  // 🔴 `null` = hiç aday yok (⊘). "%0" göstermek, çalışmayan bir kuyruğu BAŞARISIZ gibi
  // gösterirdi — yokluk bir başarısızlık değildir.
  const oran = data.kapanis_orani;
  return (
    <div className="border-b border-hairline px-3 py-2 font-mono text-[10px] text-neutral-400">
      {oran === null ? (
        <span>⊘ henüz aday yok — kapanış oranı ölçülemez</span>
      ) : (
        <>
          kapanış <span className="text-foreground">%{(oran * 100).toFixed(0)}</span>
          {" · "}açık <span className="text-foreground">{data.acik}</span>
          {" · "}kapalı <span className="text-foreground">{data.kapali}</span>
          <span className="ml-1" title="Reddedilen de KAPANIŞTIR: 'bu bir metrik değil' kararı boşluğun kapandığı anlamına gelir.">
            ⓘ
          </span>
        </>
      )}
    </div>
  );
}

export function ReviewPanel() {
  const [status, setStatus] = useState("draft");
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <div className="grid h-full grid-cols-[minmax(280px,1fr)_2fr] grid-rows-[auto_1fr]">
      <div className="col-span-2">
        <KapanisOrani />
      </div>
      <CandidateList status={status} setStatus={setStatus} selected={selected} onSelect={setSelected} />
      {selected ? (
        <CandidateDetail id={selected} />
      ) : (
        <p className="p-4 font-mono text-[12px] text-neutral-400">
          İncelemek için soldan bir aday seçin.
        </p>
      )}
    </div>
  );
}
