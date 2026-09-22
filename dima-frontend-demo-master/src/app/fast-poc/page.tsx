import type { QueryResult } from "@/lib/types";
import fixture from "@/features/fast-poc/metabase-result-fixture.json";
import { FastAnalystPoc } from "@/features/fast-poc/FastAnalystPoc";

export default function FastPocPage() {
  return (
    <FastAnalystPoc
      result={fixture.result as QueryResult}
      provenance={fixture.provenance}
    />
  );
}
