# Regulatory Migration Workbench

Local-first utility for analysing life-sciences migration datasets and maintaining a governed reference-source catalogue.

This first vertical slice provides:

- CSV import and profiling.
- Null, type, date, and duplicate issue detection.
- Exact and normalized duplicate candidates with row-level evidence.
- FAIR assessment scaffolding with human-review status.
- Guided explanations of FAIR, data quality, duplicate review, and cleanup sequencing.
- Risk-decision capture in the UI and JSON export.
- Read-only health checks for FDA, EMA, ICH, ClinicalTrials.gov, and CTIS source endpoints.
- A browser UI served by a dependency-free Python process.

The requirements baseline is documented in [docs/01_objective_and_v_model.md](docs/01_objective_and_v_model.md). It defines the product objective, current gaps, V-model verification path, evidence model, and next vertical slice.

The project is intentionally public-safe: it contains no customer data, credentials, licensed medical dictionaries, or private reference documents.

## Run locally

### From the downloaded source package

The workbench uses the local system Python and has no third-party runtime dependencies.

```bash
cd regulatory-migration-workbench
python3 -m app.server
```

On macOS or Linux, the included launcher can also be used:

```bash
./run_local.sh
```

On macOS, double-click `run_local.command` after allowing Terminal access if macOS asks for confirmation.

### Install as a local command

```bash
python3 -m pip install .
regulatory-workbench
```

The package keeps the web assets and sample dataset inside the installed distribution, so it does not depend on the original checkout path.

### Start the server

```bash
regulatory-workbench
```

Open <http://127.0.0.1:4174>.

The server is local-only by default. Uploads are processed in memory and are not written to disk by this MVP.

## How to learn with it

Use the sample dataset first. The workbench deliberately shows an issue before showing a recommendation. For each issue, ask:

1. What evidence did the rule detect?
2. Is this genuinely wrong, or an allowed business exception?
3. Which FAIR principle is affected?
4. What owner and evidence are needed before changing it?
5. How will the result be verified after cleanup?

The learning panel explains the four FAIR principles and the practical cleanup loop: preserve, profile, judge, define meaning, transform, and verify.

## Test

```bash
python3 -m unittest discover -s tests -v
```

## Product boundary

This is not a validated migration system and does not automatically accept GxP risk, merge records, or write to Veeva. It produces reviewable evidence for those decisions. Later increments can add DuckDB/Parquet processing, durable project storage, authenticated team deployment, approved reference snapshots, and source-specific connectors.

## Architecture direction

The processing engine is kept separate from the UI and HTTP server so it can become:

- a command-line utility;
- a local desktop package;
- a shared web application; or
- a scheduled source-health and reference-sync worker.
