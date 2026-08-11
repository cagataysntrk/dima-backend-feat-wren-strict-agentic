"""§C1 — `FIIL_ANLAMI` ↔ `tools.py` örtüşmesi, ve şema gerçekten okunuyor mu."""
import inspect

from app.plan_semasi import FIIL_ANLAMI, plan_json_schema
from app import tools

fiiller = sorted(FIIL_ANLAMI)
print(f"FIIL_ANLAMI: {len(fiiller)} fiil")
print("  ", ", ".join(fiiller))
print()

kayit = getattr(tools, "KAYIT", None) or getattr(tools, "ARACLAR", None)
if kayit is None:
    adlar = [n for n in dir(tools) if n.isupper()]
    print("tools.py büyük harfli semboller:", adlar)
else:
    ad_listesi = sorted(kayit) if isinstance(kayit, dict) else sorted(
        getattr(a, "ad", str(a)) for a in kayit)
    print(f"tools kaydı: {len(ad_listesi)} araç")
    print("  ", ", ".join(ad_listesi))
    print()
    # Örtüşme: fiil adı bir aracın adında (ya da tersi) geçiyor mu — kaba ama ölçülebilir
    ortusen = [f for f in fiiller
               if any(f.lower() in a.lower() or a.lower().startswith(f.lower()[:4])
                      for a in ad_listesi)]
    print(f"ÖRTÜŞME (kaba): {len(ortusen)}/{len(fiiller)} = %{100*len(ortusen)//len(fiiller)}")
    print("  örtüşen:", ", ".join(ortusen))
    print("  örtüşmeyen:", ", ".join(f for f in fiiller if f not in ortusen))
