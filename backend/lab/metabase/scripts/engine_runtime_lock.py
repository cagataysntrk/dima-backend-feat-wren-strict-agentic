#!/usr/bin/env python3
"""Validate and export the single Platform Dima engine runtime dependency lock."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


SHA40 = re.compile(r"^[0-9a-f]{40}$")
DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")
RUN_ID = re.compile(r"^[0-9]+$")


def load_lock(path: Path) -> dict[str, str]:
    body = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "engine_sha",
        "upstream_sha",
        "runtime_tag",
        "certification_run_id",
        "immutable_image_ref",
        "registry_digest",
        "build_identity",
    }
    if set(body) != required:
        raise RuntimeError(
            f"runtime lock keys mismatch: missing={sorted(required-set(body))} "
            f"extra={sorted(set(body)-required)}"
        )
    values = {key: str(value) for key, value in body.items()}
    if values["schema_version"] != "dima_engine_runtime_lock_v1":
        raise RuntimeError("unsupported runtime lock schema")
    if not SHA40.fullmatch(values["engine_sha"]):
        raise RuntimeError("engine_sha is not an exact Git SHA")
    if not SHA40.fullmatch(values["upstream_sha"]):
        raise RuntimeError("upstream_sha is not an exact Git SHA")
    if not values["runtime_tag"].startswith("v0.63.18-dima."):
        raise RuntimeError("runtime_tag is not a Dima engine runtime tag")
    if not RUN_ID.fullmatch(values["certification_run_id"]):
        raise RuntimeError("certification_run_id is not numeric")
    if not DIGEST.fullmatch(values["registry_digest"]):
        raise RuntimeError("registry_digest is not an immutable sha256 digest")
    expected_ref = (
        "ghcr.io/upcytech/dima-metabase-engine@" + values["registry_digest"]
    )
    if values["immutable_image_ref"] != expected_ref:
        raise RuntimeError(
            "immutable_image_ref does not equal the authoritative repository@digest"
        )
    expected_build = (
        f"github-actions:{values['certification_run_id']}:{values['engine_sha']}"
    )
    if values["build_identity"] != expected_build:
        raise RuntimeError(
            "build_identity does not bind certification run id to exact engine SHA"
        )
    return values


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lock", type=Path, required=True)
    ap.add_argument("--gitlink-sha")
    ap.add_argument("--github-env", type=Path)
    ap.add_argument("--print-json", action="store_true")
    args = ap.parse_args()

    values = load_lock(args.lock)
    if args.gitlink_sha is not None and args.gitlink_sha != values["engine_sha"]:
        raise RuntimeError(
            f"engine gitlink/runtime lock mismatch: "
            f"gitlink={args.gitlink_sha} lock={values['engine_sha']}"
        )

    if args.github_env is not None:
        exports = {
            "ENGINE_SHA": values["engine_sha"],
            "UPSTREAM_BASE_SHA": values["upstream_sha"],
            "RUNTIME_TAG": values["runtime_tag"],
            "CERTIFICATION_RUN_ID": values["certification_run_id"],
            "IMMUTABLE_IMAGE_REF": values["immutable_image_ref"],
            "REGISTRY_DIGEST": values["registry_digest"],
            "BUILD_IDENTITY": values["build_identity"],
        }
        with args.github_env.open("a", encoding="utf-8") as handle:
            for key, value in exports.items():
                if "\n" in value or "\r" in value:
                    raise RuntimeError(f"unsafe newline in runtime lock field {key}")
                handle.write(f"{key}={value}\n")

    if args.print_json:
        print(json.dumps(values, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
