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

The project is intentionally public-safe: it contains no customer data, credentials, licensed medical dictionaries, or private reference documents.

## Run locally

```bash
cd regulatory-migration-workbench
python3 -m app.server
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
