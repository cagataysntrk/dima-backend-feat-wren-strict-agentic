/**
 * dima-backend HTTP sözleşmesi.
 *
 * Bu paket React, DOM ve Node tanımaz — mobil (React Native) tarafı da aynı
 * tipleri kullanacak. Kural `@dima/eslint-config/boundaries` ile lint'te zorlanır.
 *
 * Tipler şu an backend'in `app/schemas.py`'si ile ELLE senkron tutuluyor; bu
 * canlı bir kayma riski. Kalıcı çözüm backend'in OpenAPI şemasından üretmek —
 * bkz. STRUCTURE.md.
 */
export type * from "./types";
