# Dima Metabase Engine workspace

`engine/metabase` is a Git submodule pointing to the real upstream-derived fork:

```text
UpcyTech/dima-metabase-engine
└── parent: metabase/metabase
```

The Platform repository does **not** vendor or copy Metabase source.

## Development order

```text
1. make engine change in UpcyTech/dima-metabase-engine
2. run engine-owned C0/C1/C2/C3 proof appropriate to the change
3. commit/push the engine change
4. update this Platform submodule pointer to the exact audited engine SHA
5. run Platform integration/governance proof
```

The gitlink is the Platform's immutable engine dependency identity for a given commit.

## Local checkout

Clone recursively:

```bash
git clone --recurse-submodules <platform-repository>
```

For an existing checkout:

```bash
git submodule sync --recursive
git submodule update --init --recursive
```

To inspect the pinned engine:

```bash
git -C engine/metabase rev-parse HEAD
git -C engine/metabase remote -v
```

## Rules

- Do not copy Metabase source into the Platform repository.
- Do not replace the submodule with a subtree.
- Do not point the submodule at `metabase/metabase` directly; it must point at the Dima fork.
- Do not use a moving branch name as product provenance; Platform commits pin an exact gitlink SHA.
- Do not rewrite published engine history.
- Upstream synchronization remains candidate-only in the engine repository.
- Ask-v2 and Fast Track remain read-only controlled-harvest sources and are unrelated to this gitlink.
