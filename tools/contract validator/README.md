# Tools/Contract Validator

Checks docs, code, and tooling outputs against the EFT2 game contract.

## Purpose

The Contract Validator scans the repo for contract compliance: contract ID coverage, mechanic anchor presence, known bad states, and required outputs. It never modifies source files. It emits a structured report and exits nonzero when hard violations are found.

The validator is the machine-readable companion to `README.md`. Where `README.md` is the human game contract, this tool checks that the agent-generated work actually respects it.

## What it checks

### 1. Contract ID coverage

`README.md` defines contract IDs of the form `C-NNN`, `P-NNN`, `M-NNN`, `S-NNN`, `E-NNN`. The validator:

- Extracts all IDs defined in `README.md`
- Scans configured target files/folders for references to each ID
- Reports which IDs are referenced nowhere outside the contract itself (coverage gap)
- Reports which IDs are referenced in places that look like violations (e.g. "removes C-001")

### 2. Mechanic anchors

A set of mechanic keyword anchors drawn from the EFT2 soul list must appear in key implementation files once those files exist. The validator checks presence only — it does not check correctness. Missing anchors in scaffold stubs are reported as warnings, not failures.

### 3. Known bad states

`README.md` section P-900 defines states that break EFT2 (sticky possession, no voluntary drop, no automatic pickup, etc.). The validator scans code for patterns that suggest these states are being hard-coded or optimized away.

### 4. Required outputs

Once Scenario Harness and Telemetry exist, the validator checks that their required output files are present and schema-valid.

## CLI

```
python "tools/contract validator/validate_contract.py" --help
python "tools/contract validator/validate_contract.py" --root .
python "tools/contract validator/validate_contract.py" --root . --strict
```

`--strict` makes coverage gaps exit nonzero (default: warnings only).

## Output

- `tools/contract validator/Output/CONTRACT_REPORT.json` — machine-readable findings
- `tools/contract validator/Output/CONTRACT_REPORT.md` — human-readable summary

## Integration

Run after any significant change to `README.md`, `AGENTS.md`, or `Game/` code. The Indexer does not run the validator — they are separate passes.

## Build order context

Contract Validator is step 3 of the infrastructure rails, after Observer skeleton and AGENTS.md patch. Scenario Harness follows.
