"use client";

import { useMemo } from "react";
import { Boxes, Database, FileCheck2, Layers, RotateCw, Sigma } from "lucide-react";
import type { AskResponse, CubeQuery } from "@dima/contracts";
import { SourceBadge } from "@/components/report/SourceBadge";
import { SqlBlock } from "@/components/report/SqlBlock";
import { AiShare } from "@/components/report/AiShare";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

/**
 * KAYNAKLAR — "bu sohbetteki cevaplar veriyi nereden aldı?"
 *
 * Sağ panelin işi AÇIK SOHBET; bu da onun en sohbete özgü sorusu. Hesap
 * genelindeki veri kataloğu sol taraftaki Veri kaynakları sayfasının işi —
 * burada yalnız BU konuşmanın gerçekten dokunduğu şey var.
 *
 * Üç katman, gitgide detaylanan: hangi küpler → hangi ölçü/kırılımlar → hangi
 * cevap hangi yolla (◆ CUBE deterministik / ▚ LLM) ve mühürlü sözleşmesi.
 * Kaynak listesi cevapların `cube_query`'sinden TÜRETİLİR; ayrı bir uç yok.
 */

/** Bir cube_query'den okunabilir alanlar — backend `dict[str, Any]` bırakıyor. */
function readCq(cq: CubeQuery | null) {
  if (!cq) return null;
  const s = (k: string) => (typeof cq[k] === "string" ? (cq[k] as string) : null);
  const arr = (k: string) => (Array.isArray(cq[k]) ? (cq[k] as unknown[]).map(String) : []);
  return {
    cube: s("cube"),
    measures: arr("measures"),
    dimensions: arr("dimensions"),
  };
}

export function SourcesPanel({
  items,
  onRerun,
}: {
  items: AskResponse[];
  /** D21/D40 — kanıtı yeniden koştur: aynı cube_query, şimdi. */
  onRerun?: (edit: { cq: CubeQuery; label: string }) => void;
}) {
  const summary = useMemo(() => {
    const cubes = new Map<string, { measures: Set<string>; dims: Set<string>; uses: number }>();
    let llm = 0;
    let deterministic = 0;
    const contracts: { id: string; question: string }[] = [];

    for (const item of items) {
      const cq = readCq(item.cube_query);
      if (cq?.cube) {
        const e = cubes.get(cq.cube) ?? { measures: new Set(), dims: new Set(), uses: 0 };
        cq.measures.forEach((m) => e.measures.add(m));
        cq.dimensions.forEach((d) => e.dims.add(d));
        e.uses += 1;
        cubes.set(cq.cube, e);
      }
      if (item.source?.startsWith("llm")) llm += 1;
      else if (item.source) deterministic += 1;
      if (item.contract_id) {
        contracts.push({ id: item.contract_id, question: item.question });
      }
    }
    return { cubes: [...cubes.entries()], llm, deterministic, contracts };
  }, [items]);

  // Sorgusu olan cevaplar — kaynak izinin taşıyıcıları.
  const answered = items.filter((i) => i.source && (i.sql || i.cube_query));

  if (answered.length === 0) {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-2 text-center">
        <Database className="size-5 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">Bu sohbette henüz kaynak yok.</p>
        <p className="max-w-xs text-xs text-muted-foreground/80">
          Bir soru sor — cevabın hangi küpten, hangi ölçü ve kırılımlarla geldiği
          burada görünecek.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* D60 — yol dağılımı (altın/gümüş/bronz). Eski "N deterministik / N model"
          rozetlerinin yerini aldı: aynı bilgiyi oran olarak ve iddiayla veriyor. */}
      <AiShare items={items} />

      {summary.contracts.length > 0 && (
        <div className="flex items-center gap-1.5">
          <Badge variant="outline" className="rounded-md text-[10px]">
            {summary.contracts.length} mühürlü kayıt
          </Badge>
          <span className="text-[11px] text-muted-foreground">
            her biri yeniden oynatılıp doğrulanabilir
          </span>
        </div>
      )}

      {/* Küpler — bu sohbetin dokunduğu veri modeli parçaları. */}
      {summary.cubes.length > 0 && (
        <section className="space-y-2">
          <h3 className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground">
            <Boxes className="size-3.5" />
            Kullanılan küpler
          </h3>
          <div className="space-y-2">
            {summary.cubes.map(([cube, e]) => (
              <Card key={cube} className="gap-2 p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate font-mono text-xs font-medium text-foreground">
                    {cube}
                  </span>
                  <span className="shrink-0 font-mono text-[10px] text-muted-foreground">
                    {e.uses} sorgu
                  </span>
                </div>
                {e.measures.size > 0 && (
                  <div className="flex flex-wrap items-center gap-1">
                    <Sigma className="size-3 text-muted-foreground" aria-hidden />
                    {[...e.measures].map((m) => (
                      <Badge key={m} variant="outline" className="font-mono text-[10px] font-normal">
                        {m}
                      </Badge>
                    ))}
                  </div>
                )}
                {e.dims.size > 0 && (
                  <div className="flex flex-wrap items-center gap-1">
                    <Layers className="size-3 text-muted-foreground" aria-hidden />
                    {[...e.dims].map((d) => (
                      <Badge key={d} variant="outline" className="font-mono text-[10px] font-normal">
                        {d}
                      </Badge>
                    ))}
                  </div>
                )}
              </Card>
            ))}
          </div>
        </section>
      )}

      <Separator />

      {/* Cevap cevap iz: hangi soru, hangi yolla, hangi sorguyla. */}
      <section className="space-y-2">
        <h3 className="text-xs font-medium text-muted-foreground">Cevapların izi</h3>
        <div className="space-y-2">
          {answered.map((item, i) => (
            <Card key={`${item.question}-${i}`} className="gap-2 p-3">
              <div className="flex items-start justify-between gap-2">
                <p className="min-w-0 flex-1 truncate text-xs text-foreground" title={item.question}>
                  {item.question}
                </p>
                <SourceBadge source={item.source} />
              </div>

              {item.contract_id && (
                <div
                  className="flex items-center gap-1.5"
                  title="Query Contract — soru + sorgu + sonuç özeti mühürlendi; yeniden oynatılıp doğrulanabilir"
                >
                  <FileCheck2 className="size-3 shrink-0 text-muted-foreground" aria-hidden />
                  <span className="truncate font-mono text-[10px] text-muted-foreground">
                    {item.contract_id}
                  </span>
                </div>
              )}

              {item.sql && <SqlBlock sql={item.sql} />}

              {/* D21/D40 — "bu sayı neye dayanıyor?" sorusunun son halkası:
                  denetçi aynı sorguyu ŞİMDİ koşturup sayıyı yeniden üretebilir. */}
              {onRerun && item.cube_query && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onRerun({ cq: item.cube_query!, label: item.question })}
                  className="h-7 w-fit gap-1.5 text-xs"
                >
                  <RotateCw className="size-3.5" />
                  yeniden koştur
                </Button>
              )}
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}
