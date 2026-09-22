// Titles for automatic insights. The engine names them in English
// ("Makineler by Kapasite Kg"); this phrases them like the rest of the app.
// Pure, unit-tested.

export function insightTitle(name: string, table: string): string {
  const by = /^(.*?) (?:by|per) (.+)$/i.exec(name);
  if (by) return `${by[2]} kırılımı`;
  if (/^total /i.test(name)) return `Toplam ${table}`;
  if (/^count of /i.test(name)) return `${table} adedi`;
  return name;
}
