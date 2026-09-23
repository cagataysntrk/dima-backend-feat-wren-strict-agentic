#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_REPO="${UPSTREAM_REPO:-metabase/metabase}"
TARGET_ORG="${TARGET_ORG:-UpcyTech}"
TARGET_NAME="${TARGET_NAME:-dima-metabase-engine}"
TARGET_REPO="${TARGET_ORG}/${TARGET_NAME}"
BASE_TAG="${BASE_TAG:-v0.63.18}"
BASE_SHA="${BASE_SHA:-2ba2485c78d7e00a9a25f82c00fc201da71590c4}"
BASE_BRANCH="${BASE_BRANCH:-upstream/base-v0.63.18}"
INTEGRATION_BRANCH="${INTEGRATION_BRANCH:-main}"

for bin in gh git jq; do
  command -v "$bin" >/dev/null || { echo "missing required tool: $bin" >&2; exit 2; }
done

gh auth status >/dev/null

if ! gh api "repos/$TARGET_REPO" >/dev/null 2>&1; then
  echo "Creating real GitHub fork $TARGET_REPO from $UPSTREAM_REPO ..."
  gh api --method POST "repos/$UPSTREAM_REPO/forks"     -f organization="$TARGET_ORG"     -f name="$TARGET_NAME" >/dev/null
fi

echo "Waiting for fork metadata ..."
for _ in $(seq 1 90); do
  if meta="$(gh api "repos/$TARGET_REPO" 2>/dev/null)"; then
    fork="$(jq -r '.fork' <<<"$meta")"
    parent="$(jq -r '.parent.full_name // empty' <<<"$meta")"
    if [[ "$fork" == "true" && "$parent" == "$UPSTREAM_REPO" ]]; then
      break
    fi
  fi
  sleep 2
done

meta="$(gh api "repos/$TARGET_REPO")"
[[ "$(jq -r '.fork' <<<"$meta")" == "true" ]] || { echo "target is not a GitHub fork" >&2; exit 3; }
[[ "$(jq -r '.parent.full_name' <<<"$meta")" == "$UPSTREAM_REPO" ]] || {
  echo "wrong fork parent: $(jq -r '.parent.full_name' <<<"$meta")" >&2
  exit 3
}

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

git clone --filter=blob:none "https://github.com/$TARGET_REPO.git" "$work/repo"
cd "$work/repo"

if git remote get-url upstream >/dev/null 2>&1; then
  git remote set-url upstream "https://github.com/$UPSTREAM_REPO.git"
else
  git remote add upstream "https://github.com/$UPSTREAM_REPO.git"
fi

git fetch --tags --force upstream
resolved="$(git rev-parse "$BASE_TAG^{commit}")"
[[ "$resolved" == "$BASE_SHA" ]] || {
  echo "base mismatch: $BASE_TAG -> $resolved expected $BASE_SHA" >&2
  exit 4
}

# Immutable upstream base reference: create once, never move.
if git ls-remote --exit-code --heads origin "$BASE_BRANCH" >/dev/null 2>&1; then
  remote_base="$(git ls-remote --heads origin "$BASE_BRANCH" | awk '{print $1}')"
  [[ "$remote_base" == "$BASE_SHA" ]] || {
    echo "$BASE_BRANCH already exists at $remote_base, refusing to move immutable base" >&2
    exit 5
  }
else
  git push origin "$BASE_SHA:refs/heads/$BASE_BRANCH"
fi

# Main may only be initialized at the exact base. Never rewrite a published Dima main.
if git ls-remote --exit-code --heads origin "$INTEGRATION_BRANCH" >/dev/null 2>&1; then
  remote_main="$(git ls-remote --heads origin "$INTEGRATION_BRANCH" | awk '{print $1}')"
  [[ "$remote_main" == "$BASE_SHA" ]] || {
    echo "$INTEGRATION_BRANCH already exists at $remote_main; bootstrap refuses to rewrite it" >&2
    exit 6
  }
else
  git push origin "$BASE_SHA:refs/heads/$INTEGRATION_BRANCH"
fi

gh api --method PATCH "repos/$TARGET_REPO" -f default_branch="$INTEGRATION_BRANCH" >/dev/null

cat <<EOF
BOOTSTRAP_GREEN
target=$TARGET_REPO
parent=$UPSTREAM_REPO
base_tag=$BASE_TAG
base_sha=$BASE_SHA
base_branch=$BASE_BRANCH
main=$INTEGRATION_BRANCH
main_sha=$BASE_SHA
EOF
