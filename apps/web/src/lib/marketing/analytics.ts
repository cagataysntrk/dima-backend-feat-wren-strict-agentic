export type MarketingEvent =
  | "demo_cta_clicked"
  | "product_proof_view_changed"
  | "contact_form_started"
  | "contact_form_submitted";

type SafeProperties = Record<string, string | number | boolean>;

/**
 * Privacy-safe integration seam. Deliberately no-op until an approved analytics
 * provider and consent policy are configured. Never pass email, names or free text.
 */
export function trackMarketingEvent(_event: MarketingEvent, _properties: SafeProperties = {}) {
  void _event;
  void _properties;
}
