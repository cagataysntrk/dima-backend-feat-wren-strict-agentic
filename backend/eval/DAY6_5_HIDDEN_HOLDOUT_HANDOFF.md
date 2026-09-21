# Day 6.5 Hidden Holdout Freeze Handoff

Bu dizin hidden prompt metnini tutmaz.

Bağımsız evaluator/arkadaş kendi ortamında 50-case corpus'u hazırlar ve şu komutu çalıştırır:

```bash
python lab/v2_day6_5_freeze_holdout.py /secure/path/day65_hidden.jsonl \
  --expected-count 50 \
  --metadata-out /secure/path/day65_hidden_metadata.json
```

Development tarafına **yalnız** `day65_hidden_metadata.json` içeriği aktarılır.

Beklenen güvenli metadata:

```json
{
  "status": "FROZEN_EXTERNAL",
  "case_count": 50,
  "corpus_sha256": "<sha256>",
  "taxonomy_sha256": "<sha256>",
  "taxonomy_manifest": {
    "case_count": 50,
    "taxonomy_counts": {},
    "language_counts": {},
    "adaptive_case_count": 0,
    "adversarial_case_count": 0
  },
  "prompt_text_committed": false,
  "development_model_generated": false
}
```

Yasak:
- hidden corpus'u repoya commit etmek,
- prompt text'i issue/PR/log/chat'e yapıştırmak,
- implementation yapan modele hidden promptları göstermek,
- hash sonrası corpus'u değiştirmek.

Metadata geldikten sonra `eval/v2_day6_5_eval_manifest.yaml` içindeki iki REQUIRED placeholder
gerçek hash'lerle değiştirilir ve Day 6.5 production implementation gate açılır.
