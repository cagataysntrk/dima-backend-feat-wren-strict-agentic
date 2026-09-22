import { describe, expect, it } from "vitest";
import { fromQueryFailure, fromUpstream, scrub } from "./errors";

describe("public errors", () => {
  it("hides other tenants' ids: upstream 403 and 404 both become 404", () => {
    expect(fromUpstream(403, "x").status).toBe(404);
    expect(fromUpstream(404, "x").status).toBe(404);
  });

  it("never exposes the engine's name", () => {
    const messages = [
      fromUpstream(500, "Metabase exploded").publicMessage,
      fromUpstream(401, "bad key").publicMessage,
      fromQueryFailure('ERROR: relation "foo" does not exist — metabase.driver').publicMessage,
      fromQueryFailure("Metabase: timeout").publicMessage,
    ];
    for (const m of messages) expect(m).not.toMatch(/metabase/i);
  });

  it("scrub replaces every engine mention", () => {
    expect(scrub("Metabase and METABASE")).not.toMatch(/metabase/i);
  });
});
