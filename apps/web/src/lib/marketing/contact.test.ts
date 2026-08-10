import { describe, expect, it } from "vitest";
import { isLikelyBot, validateContactForm } from "./contact";

function validForm() {
  const data = new FormData();
  data.set("fullName", "Ada Lovelace");
  data.set("email", "ada@example.com");
  data.set("company", "Analytical Engines");
  data.set("role", "Founder");
  data.set("need", "Weekly operational exceptions");
  data.set("privacyConsent", "on");
  return data;
}

describe("contact validation", () => {
  it("accepts a complete request", () => {
    expect(validateContactForm(validForm(), "en").valid).toBe(true);
  });
  it("rejects malformed email and missing fields", () => {
    const data = validForm();
    data.set("email", "not-an-email");
    data.delete("company");
    const result = validateContactForm(data, "en");
    expect(result.valid).toBe(false);
    expect(result.errors.email).toBeDefined();
    expect(result.errors.company).toBeDefined();
  });
  it("detects honeypot and implausibly fast submission", () => {
    const data = validForm();
    data.set("startedAt", String(Date.now()));
    expect(isLikelyBot(data)).toBe(true);
    data.set("website", "https://spam.invalid");
    expect(isLikelyBot(data, Date.now() + 3000)).toBe(true);
  });
  it("normalizes single-line fields before email delivery", () => {
    const data = validForm();
    data.set("company", "Example\r\nInjected");
    expect(validateContactForm(data, "en").payload.company).toBe("Example Injected");
  });
  it("requires an explicit privacy acknowledgement", () => {
    const data = validForm();
    data.delete("privacyConsent");
    const result = validateContactForm(data, "en");
    expect(result.valid).toBe(false);
    expect(result.errors.privacyConsent).toBeDefined();
  });
});
