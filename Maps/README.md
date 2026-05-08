# EFT2 Maps

`Maps/` is organized by canonical map domains, not old Source 1 filenames.

Each map folder uses the map's display name, and the root VMF inside the folder is renamed to the same canonical name. Original filenames and Source 1 suffixes are preserved in `source_manifest.json`.

The root VMF in each map domain is a read-only original source reference. Do not edit, reformat, normalize, or regenerate it.

- `Analysis/` contains generated structured map analysis.
- `Virtual Perception/` contains generated LLM-facing spatial/gameplay perception artifacts.
- `Simulation/` is reserved for future optional simulation work and is not implemented in this patch.

Slam Dunk is the first map intelligence validation target. Bloodbowl is the second validation target and the flat/open-field swarm reference.
