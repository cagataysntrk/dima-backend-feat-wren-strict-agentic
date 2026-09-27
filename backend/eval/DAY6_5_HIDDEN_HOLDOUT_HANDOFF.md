# Day 6.5 Hidden Holdout Freeze Handoff

Bu dizin hidden prompt metnini tutmaz.

Bağımsız evaluator/arkadaş kendi ortamında 50-case corpus'u hazırlar ve şu komutu çalıştırır:

```bash
python lab/v2_day6_5_freeze_holdout.py /secure/path/day65_hidden.jsonl \
  --expected-count 50 \
  --attestation /secure/path/day65_hidden_attestation.json \
  --metadata-out /secure/path/day65_hidden_metadata.json
```

Evaluator önce aşağıdaki gibi ayrı bir attestation dosyası oluşturur:

```json
{
  "status": "ATTESTED_EXTERNAL",
  "independent_evaluator": true,
  "development_model_generated": false,
  "prompt_text_committed": false,
  "prompt_text_shared_with_implementation": false,
  "development_corpus_seen": false,
  "development_failure_outputs_seen": false,
  "frozen_before_architecture_seal_run": true
}
```

Bu alanlar freeze utility tarafından artık otomatik uydurulmaz; external evaluator'ın
açık beyanından okunur ve attestation dosyasının SHA-256 değeri metadata'ya bağlanır.

Development tarafına **yalnız** `day65_hidden_metadata.json` içeriği aktarılır.

Beklenen güvenli metadata:

```json
{
  "status": "FROZEN_EXTERNAL",
  "case_count": 50,
  "corpus_sha256": "<sha256>",
  "taxonomy_sha256": "<sha256>",
  "attestation_sha256": "<sha256>",
  "taxonomy_manifest": {
    "case_count": 50,
    "taxonomy_counts": {},
    "language_counts": {},
    "adaptive_case_count": 0,
    "adversarial_case_count": 0
  },
  "independent_evaluator": true,
  "prompt_text_committed": false,
  "prompt_text_shared_with_implementation": false,
  "development_model_generated": false,
  "development_corpus_seen": false,
  "development_failure_outputs_seen": false,
  "frozen_before_architecture_seal_run": true
}
```

Yasak:
- hidden corpus'u repoya commit etmek,
- prompt text'i issue/PR/log/chat'e yapıştırmak,
- implementation yapan modele hidden promptları göstermek,
- hash sonrası corpus'u değiştirmek,
- development modelin ürettiği corpus için external attestation vermek,
- DEV/VALIDATION prompt corpusunu veya failure çıktısını hidden üretiminde kullanmak.

## Architecture seal günü — hidden result receipt

Hidden promptlar seal gününde de development context'e girmez. Independent evaluator,
frozen corpus'u exact target commit üzerinde çalıştırır ve yalnız şu receipt'i döndürür:

```text
status = PASS | FAIL
corpus_sha256
taxonomy_sha256
attestation_sha256
tested_git_sha
eval_harness_sha
model_role
provider
model
contract_schema_version
case_count
aggregate_gate_metrics
```

`tested_git_sha` ve `eval_harness_sha` zorunludur; corpus sabitken test edilen kodun
ve oracle/harness'ın hangisi olduğu denetlenebilir kalmalıdır. Prompt text, per-case prompt
ve hidden expected-answer içeriği receipt'e girmez.

Metadata geldikten sonra `eval/v2_day6_5_eval_manifest.yaml` içindeki corpus/taxonomy/attestation REQUIRED placeholder'ları gerçek değerlerle değiştirilir ve Day 6.5 architecture-seal gate açılır. Manager implementation bundan bağımsız ilerleyebilir. Hidden corpus implementation
başladıktan sonra da hazırlanabilir; geçerlilik şartı development prompt/failure
çıktılarından bağımsız kalması ve architecture-seal run'dan önce freeze edilmesidir.
