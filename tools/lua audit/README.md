# Tools/Lua Audit

`tools/lua audit/` is the **block-level inherited-Lua understanding layer** of
the EFT2 iterative resolution loop.

It reads the read-only `lua/` reference and produces stable, agent-readable
behavior blocks, system clusters, and a Lua → s&box bridge. It is **not** a
direct Lua → C# translator. Its job is to give future agents reviewable
handles into the original behavior so that gameplay meaning can be recovered
*before* C# code is rewritten.

## Resolution chain it serves

```
README contract
  -> inherited Lua behavior          <-- this tool
  -> tacit played meaning
  -> FGD/map grammar
  -> map analysis / virtual perception
  -> s&box engine surface
  -> current C# implementation
  -> telemetry / scenarios / simulation validation
  -> feedback back into earlier layers
```

## Scope

- Audits every `.lua` under `lua/` except recorded match data under
  `lua/game logs/`.
- Read-only. The tool never edits `lua/` files.
- Repo-relative paths only. Personal filesystem paths are never written into
  outputs.

## Run

```powershell
python "tools/lua audit/audit_lua.py" --help
python "tools/lua audit/audit_lua.py" --root .
```

Optional flags:

- `--lua-dir lua` — override Lua scan root.
- `--out "tools/lua audit/output"` — override output directory.

## Outputs

```
tools/lua audit/output/
  LUA_AUDIT.json
  LUA_AUDIT.md
  LUA_SYSTEM_CLUSTERS.json
  LUA_SYSTEM_CLUSTERS.md
  LUA_TO_SBOX_BRIDGE.json
  LUA_TO_SBOX_BRIDGE.md
  id_registry.json     # identity-key -> stable block ID
```

Each JSON file uses the standard envelope:

```json
{
  "generated_by": "tools/lua audit",
  "schema_version": 1,
  "generated_at": "...",
  "warnings": []
}
```

## Honesty rules

- **First pass is a draft, not final canon.** It creates handles future
  passes can refine, merge, split, or correct.
- `audit_quality` is one of `mechanical`, `inferred`, `human_confirmed`. The
  first pass emits `inferred` for interpretive fields.
- `tacit_meaning` is **conservative**. If the heuristic cannot infer why a
  block mattered in play, it is left empty, `needs_human_review = true`, and
  `missing_evidence` records what is missing.
- `csharp_owner.status` is one of `candidate_present`, `partial`, `planned`,
  `missing`, `needs_inspection`. `candidate_present` only means a plausible
  owner file exists in `game/eft2/Code/`. **Parity is not verified by this
  tool.** `parity_verified` is always `false` until a human review pass
  confirms behavioral parity.
- Stable IDs do **not** depend primarily on line numbers. Identity key:
  `relpath :: block_kind :: symbol :: normalized_signature` (or short body
  hash if the symbol is anonymous). `line_range` is metadata only.
- Inherited MANIFEST LINKS (`/// MANIFEST LINKS:` headers) and embedded
  contract IDs (`P-…`, `M-…`, `C-…`, `S-…`, `E-…`) are extracted verbatim and
  preserved on every block in the file.

## Connection to the rest of the loop

- `tools/simulation/` should consume `LUA_AUDIT.json`,
  `LUA_SYSTEM_CLUSTERS.json`, and `LUA_TO_SBOX_BRIDGE.json` to ground rules
  before attempting map/gameplay prediction. Without Lua Audit grounding,
  simulation readiness is preliminary.
- `tools/telemetry/` and `tools/scenario harness/` should be joined into the
  bridge in a later pass so each cluster names the telemetry events and
  scenario IDs that validate it.
- `tools/contract validator/` and `tools/indexer/` are unaffected by this
  tool's outputs; running them after this tool should produce the same
  baseline they produced before.

See `lua_audit_schema.md` for the per-block record schema.
