import { describe, expect, it } from "vitest";
import { createParser } from "@openuidev/lang-core";

import spec from "@/generated/spec.json";
import { resolveKind } from "@/components/tiles/chart";

/**
 * VOKABÜLER TESTİ — LLM ÇAĞRISI YOK.
 *
 * OpenUI Lang'i modelin üreteceği biçimde elle yazıp kütüphane şemasına karşı
 * ayrıştırıyoruz. Böylece "model makul pano kurabilir mi" sorusunun yarısı
 * (dilin kompozisyonu ifade edebilmesi ve hataları reddetmesi) sağlayıcıya
 * hiç para ödemeden, ağ olmadan, deterministik biçimde yanıtlanıyor.
 *
 * Asıl değeri REDDETME testlerinde: vokabülerin modeli gerçekten kısıtladığını
 * kanıtlarlar. Kısıtlamayan bir şema, güvenlik değil dekordur.
 */

const parse = (source: string) => {
  const result = createParser(spec, "Dashboard").parse(source);
  return result.meta?.errors ?? [];
};

describe("dima pano vokabüleri", () => {
  it("KPI satırı + grafik + yorum + tablodan oluşan tam bir panoyu kabul eder", () => {
    expect(
      parse(`root = Dashboard("Çeyrek Özeti", [ust, egilim, detay])
ust = Grid([k1, k2, k3], "3")
k1 = KpiTile("q1")
k2 = KpiTile("q2")
k3 = KpiTile("q3")
egilim = Section("Eğilim", [c1, yorum])
c1 = ChartTile("q4")
yorum = InsightNote("q4")
detay = Section("Detay", [t1])
t1 = TableTile("q5", 20)`),
    ).toEqual([]);
  });

  it("iç içe yerleşimi destekler — panonun ağaç olması şart", () => {
    // AI SDK'nın tool-çağrısı deseninin ifade EDEMEDİĞİ şey tam olarak bu:
    // Grid içinde Section, Section içinde Grid.
    expect(
      parse(`root = Dashboard("Üretim", [bolum])
bolum = Section("Vardiya", [ic])
ic = Grid([c1, t1], "2")
c1 = ChartTile("q1", "bar")
t1 = TableTile("q2")`),
    ).toEqual([]);
  });

  it("opsiyonel argümanlar sondan atlanabilir", () => {
    expect(parse(`root = Dashboard("Boş", [c])\nc = ChartTile("q1")`)).toEqual([]);
  });

  // --- Reddetmesi gerekenler ------------------------------------------------

  it("kütüphanede olmayan bileşeni reddeder", () => {
    // Model kendi kafasından "LineChart" uyduramamalı.
    expect(parse(`root = Dashboard("X", [c])\nc = LineChart("q1")`).length).toBeGreaterThan(0);
  });

  it("zorunlu argüman eksikse reddeder", () => {
    expect(parse(`root = Dashboard("X", [k])\nk = KpiTile()`).length).toBeGreaterThan(0);
  });

  it("fazla argümanı reddeder", () => {
    expect(
      parse(`root = Dashboard("X", [k])\nk = KpiTile("q1", "fazladan", 3)`).length,
    ).toBeGreaterThan(0);
  });

  /**
   * BULGU: parser enum ÜYELİĞİNİ denetlemiyor.
   *
   * Üretilen spec yapısal tip değil, imza METNİ taşıyor
   * ("kind?: \"bar\" | \"line\" | …"), bu yüzden ayrıştırıcı yalnız bileşen
   * adını ve argüman SAYISINI doğrulayabiliyor. Enum modele yalnız tavsiye.
   *
   * Bu testi "reddetmeli" diye yazmıştım ve geçmedi — varsayımım yanlıştı.
   * Doğru tepki testi zorlamak değil, ZORLAMAYI RENDERER'A TAŞIMAK oldu
   * (resolveKind). Test şimdi gerçek davranışı belgeliyor ki bir gün parser
   * bunu denetlemeye başlarsa haberimiz olsun.
   */
  it("BELGE: parser geçersiz enum değerini yakalamaz — zorlama renderer'da", () => {
    expect(parse(`root = Dashboard("X", [c])\nc = ChartTile("q1", "sankey")`)).toEqual([]);
  });

  it("renderer tanınmayan grafik türünü deterministik seçime düşürür", () => {
    // Modelin hatası doğru davranışa düşmeli: sessizce sütun çizmek değil,
    // analyze()'ın veri şeklinden seçtiği türe dönmek.
    expect(resolveKind("sankey", "line")).toBe("line");
    expect(resolveKind(undefined, "bar")).toBe("bar");
    expect(resolveKind("pie", "bar")).toBe("pie");
  });

  /**
   * BULGU: `root =` yazılmazsa parser SON ifadeyi kök kabul ediyor ve kökün
   * kütüphanedeki root bileşeni (Dashboard) olmasını ZORLAMIYOR.
   *
   * "root tanımlanmazsa hiçbir şey render edilmez" diye yazdığım test geçmedi;
   * varsayımım yanlıştı. dima için bu tolere edilebilir — sarmalayıcısız tek
   * karo yine doğru çizilir, çünkü her karo verisini katalogdan kendi çeker.
   * Ama bilerek tolere ediyoruz; sessizce bilmemek başka şey.
   */
  it("BELGE: root yoksa son ifade kök olur — Dashboard sarmalayıcısı zorunlu değil", () => {
    const result = createParser(spec, "Dashboard").parse(`k = KpiTile("q1")`);
    expect(result.root?.typeName).toBe("KpiTile");
  });

  it("root'tan erişilemeyen ifadeleri öksüz olarak işaretler", () => {
    // Modelin tanımlayıp bağlamayı unuttuğu karo sessizce kaybolmamalı —
    // `orphaned` bunu modele geri besleyeceğimiz düzeltme sinyali yapar.
    const result = createParser(spec, "Dashboard").parse(
      `root = Dashboard("X", [a])\na = KpiTile("q1")\nunutulan = TableTile("q2")`,
    );
    expect(result.meta.orphaned).toContain("unutulan");
  });

  it("tanımsız referansı çözülmemiş olarak bildirir", () => {
    const result = createParser(spec, "Dashboard").parse(`root = Dashboard("X", [yok])`);
    expect(result.meta.unresolved).toContain("yok");
  });
});
