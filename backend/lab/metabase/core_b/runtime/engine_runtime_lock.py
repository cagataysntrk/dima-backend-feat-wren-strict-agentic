#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path
SHA40=re.compile(r"^[0-9a-f]{40}$"); DIGEST=re.compile(r"^sha256:[0-9a-f]{64}$")
def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--lock",type=Path,required=True); ap.add_argument("--gitlink-sha",required=True); ap.add_argument("--github-env",type=Path,required=True); args=ap.parse_args()
 b=json.loads(args.lock.read_text())
 if b["engine_sha"]!=args.gitlink_sha: raise RuntimeError("engine gitlink/runtime lock mismatch")
 if not SHA40.fullmatch(b["engine_sha"]) or not DIGEST.fullmatch(b["registry_digest"]): raise RuntimeError("invalid engine lock")
 expected="ghcr.io/upcytech/dima-metabase-engine@"+b["registry_digest"]
 if b["immutable_image_ref"]!=expected: raise RuntimeError("image ref/digest mismatch")
 expected_build=f"github-actions:{b['certification_run_id']}:{b['engine_sha']}"
 if b["build_identity"]!=expected_build: raise RuntimeError("build identity mismatch")
 exports={"ENGINE_SHA":b["engine_sha"],"UPSTREAM_BASE_SHA":b["upstream_sha"],"RUNTIME_TAG":b["runtime_tag"],"CERTIFICATION_RUN_ID":b["certification_run_id"],"IMMUTABLE_IMAGE_REF":b["immutable_image_ref"],"REGISTRY_DIGEST":b["registry_digest"],"BUILD_IDENTITY":b["build_identity"]}
 with args.github_env.open("a",encoding="utf-8") as f:
  for k,v in exports.items(): f.write(f"{k}={v}\n")
 print(json.dumps(b,sort_keys=True))
if __name__=="__main__":main()
