# EFT2 Map Analyzer

`Tools/Map Analyzer/` is the first EFT2 map intelligence pipeline.

It exists to help agents understand maps as played spaces, not merely as entity lists. Raw VMF data is preserved, then reconciled into confidence-scored gameplay structures, Virtual Perception artifacts, and map summaries for later porting/design work.

## Commands

Dry-run map organization:

```powershell
python "Tools/Map Analyzer/organize_maps.py" --dry-run
```

Organize loose VMFs:

```powershell
python "Tools/Map Analyzer/organize_maps.py"
```

Analyze one map:

```powershell
python "Tools/Map Analyzer/analyze_map.py" "Maps/Slam Dunk"
```

Analyze all organized maps:

```powershell
python "Tools/Map Analyzer/analyze_all.py"
```

## Output

Each map domain has:

- `<Canonical Name>.vmf`: read-only original Source 1 reference.
- `README.md`: source policy and analysis status.
- `Analysis/`: generated structured analysis.
- `Virtual Perception/`: LLM-facing spatial/gameplay perception artifacts.
- `Simulation/`: placeholder only; simulation is not implemented in this patch.

Generated analysis includes raw entities, brush entities, trigger volumes, EFT entity classifications, semantic groups, Recast-pending nav files, gameplay profile, confidence report, and `summary.md`.

`Simulation/abstract_gameflow.json` and `.md` contain coarse gameplay telemetry. They use README movement constants and extracted map landmarks to model route pressure, carrier timing, defender timing, scoring likelihood, and scrum/intercept outcomes. They are not physics replays.

## Recast Status

Recast/Detour is the intended traversal brain. This version records the mined Recast integration shape, inspects for a Recast binary/binding, and exports approximate Recast-friendly triangle geometry from VMF AABBs. It does not fake route metrics.

Blender/Recast source trees were temporary mining inputs only. Useful backend lessons now live in project-owned analyzer code and `backend_research.md`; no separate Blender/Recast tool domain is created.

s&box itself implements Recast Navigation. Future in-game bots should use `Scene.NavMesh`, `NavMeshAgent`, `NavMeshLink`, and `NavMeshArea` where they fit EFT movement. Analyzer route evidence should become validation and authoring input for those runtime systems, not a separate competing bot stack.

## Validation Targets

Slam Dunk is first because it stresses verticality, powerups, push/jump routes, hoop/scoring interpretation, and high-energy scoring flow.

Bloodbowl is second because it validates open-field swarm, spawn-to-ball convergence, hazards/resets, and raw goal trigger count versus inferred scoring complexes.

## Known Limits

- Brush bounds are approximate AABBs from VMF side plane points.
- Semantic grouping is first-pass and confidence-scored.
- Route graph, preventability, and timing metrics are pending Recast integration.
- Line-of-sight output currently probes reconstructed VMF brush triangles, but still needs final validation against s&box physics/navmesh after porting.
- Abstract simulation uses sport constants and map landmarks only; it should be treated as gameplay pressure telemetry until runtime bot/nav validation exists.
- Analyzer output should inform domain-expert review, not replace it.
