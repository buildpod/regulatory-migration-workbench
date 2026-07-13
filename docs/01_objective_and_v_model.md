# Regulatory Migration Workbench

## Objective, gap assessment and V-model baseline

**Status:** Baseline for requirements discovery

**Purpose:** Define what the product is, what it is not, and how each requirement will be verified before we add more capability.

## 1. Defined objective

Build a local-first, deployable regulatory migration workbench that helps a migration team:

1. preserve and profile source data and dossier structures;
2. identify data-quality issues and duplicate candidates with evidence;
3. assess FAIR readiness and explain the reasoning in plain language;
4. map source data and regulatory evidence to canonical target concepts;
5. propose or apply controlled, reversible transformations;
6. record accepted risk, exceptions, owners, approvals, and review dates; and
7. produce an auditable validation and migration package for human-approved loading into a target system.

The workbench supports decisions. It must not silently change source data, automatically merge records, accept GxP/regulatory risk, or write to Veeva/CARA/eMAS without an explicitly approved downstream control.

## 2. What we are building

This is a product with two faces and one processing core:

| Product face | Purpose | Initial delivery shape |
|---|---|---|
| Utility | Repeatable analysis for a file, folder, API response, or batch | CLI/library-compatible processing engine |
| UI | Guided review, learning, mapping, exception, and approval workflow | Local browser UI; later team deployment |
| Processing core | Deterministic profiling, duplicate detection, FAIR evidence, mapping, transformation, reconciliation, and export | Python modules with versioned rules and evidence objects |

The first release is an **evidence-first decision workbench**, not a validated migration executor. Its output is a reviewable package containing findings, proposed actions, mappings, references, approvals, and verification results.

## 3. Experience we are carrying forward

The design reflects the patterns that matter in life-sciences migration work:

- **Understand the source before prescribing the solution.** A folder or field that looks wrong may be an allowed lifecycle, regional, or business exception.
- **Separate detection from judgement.** The rule records evidence; a data owner or process owner decides what it means.
- **Preserve the original.** The source extract, source path, retrieval time, and hash remain immutable.
- **Use controlled references.** Regulatory and clinical guidance must be source-identified, versioned, jurisdiction-aware, and reviewable.
- **Do not confuse RAG, FAIR, data quality, and risk acceptance.** They are related signals, but they answer different questions.
- **Keep regulatory boundaries explicit.** A folder-structure rule can identify a likely eCTD root; it cannot prove that a submission is content-complete or validated.
- **Make the result defensible.** Every proposed cleanup, duplicate disposition, mapping, and transformation needs evidence, rationale, owner, and verification.
- **Design for more than a UI.** The same rules must be runnable as a utility, service, batch job, or future connector.

## 4. Current gap assessment

The current MVP proves the direction, but not the full operating model.

| Capability | What exists now | Gap | Consequence | Target increment |
|---|---|---|---|---|
| Source ingestion | CSV upload and sample dataset | No XLSX, XML, ZIP/dossier, JSON, API, or folder-tree ingestion | Real migration sources cannot yet be analysed consistently | Source adapters with a common immutable `SourceAsset` model |
| Source preservation | SHA-256 of uploaded CSV in memory | No durable source package, retrieval metadata, or evidence store | Findings cannot yet be reconstructed as a controlled project record | Immutable source manifest and evidence package |
| Data profiling | Missing values, inferred types, date checks, uniqueness counts | No business-key rules, code-list checks, referential integrity, temporal rules, or structural dossier checks | Technical anomalies may be detected without business meaning | Profile rules configurable by object, field, jurisdiction, and project |
| Duplicate detection | Exact and normalized duplicate candidates | No fuzzy matching, survivorship rules, relationship checks, or review history | Candidates cannot be safely resolved or merged | Explainable match scoring and human disposition workflow |
| FAIR assessment | Guided four-principle scaffolding | No metadata model, FAIR evidence register, or reusable FAIR scorecard | FAIR remains educational rather than operational | FAIR evidence objects linked to fields, datasets, and decisions |
| Reference library | Public source catalogue and reachability probes | No versioned documents, content extraction, section/page citations, source precedence, or approval workflow | A reachable URL is not controlled regulatory evidence | Staged reference ingestion, versioning, citation, review, and publication |
| Mapping | Workbook pattern understood; no product mapping engine | No source-to-canonical-to-target mapping model or reference link at rule level | Transformation cannot be repeated or audited | Mapping registry with rule, evidence, reference, and approval fields |
| Transformation | No controlled transformation pipeline | No dry-run, reversibility, rejected-record handling, or before/after evidence | Cleanup cannot be safely promoted to migration output | Versioned transformations with preview, rollback, and reconciliation |
| Risk and exception | UI captures a simple review-required decision | No risk taxonomy, acceptance criteria, segregation of duties, signatures, or status history | A note is not a defensible risk acceptance | Risk register with owner, approver, rationale, expiry, and evidence |
| Validation | Unit tests for the current quality module | No requirements traceability, test protocols, test data, or release evidence | Product behavior is not yet demonstrably fit for intended use | V-model verification package and release evidence |
| Output | JSON export and source-health results | No review workbook, mapping package, reconciliation report, or target load package | Teams must manually rework outputs | Standard evidence, mapping, exception, and load-ready exports |
| Security and deployment | Local-only, dependency-free server | No authentication, authorization, project isolation, persistence, audit log, encryption, or deployment controls | Not ready for shared or regulated operational use | Deployment profiles: local utility, controlled team service, enterprise integration |

## 5. Product boundaries

### In scope

- Regulatory, clinical, dossier, and migration source assessment.
- Data-quality profiling and explainable duplicate candidate detection.
- FAIR evidence capture and learning guidance.
- Reference-backed mapping and transformation design.
- Human review, exception, risk, and approval records.
- Reconciliation and export of a controlled migration package.
- UI plus reusable utility/service processing core.

### Out of scope for the initial validated boundary

- Automatic acceptance of regulatory or GxP risk.
- Automatic duplicate merging or deletion of source records.
- Direct write-back to Veeva, CARA, eMAS, or another production system.
- Claiming dossier or submission completeness from folder structure alone.
- Replacing regulatory, medical, clinical, quality, or data-owner judgement.
- Treating a live URL as an approved reference without version and review controls.

## 6. V-model development and verification path

The left side defines intent and controls. The right side proves that the implemented behavior meets that intent.

| V-model level | Requirement output | Example for this workbench | Verification evidence |
|---|---|---|---|
| User need | UN-001 | Migration teams need evidence-backed cleanup decisions before loading a target system | User acceptance scenarios and stakeholder sign-off |
| User requirements | URS-001 to URS-008 | Preserve source, detect issues, review duplicates, map, transform, accept risk, export evidence | Approved URS and traceability review |
| System requirements | SRS-001 to SRS-012 | Source manifest, rule version, reference ID, audit event, role, status, export contract | Requirements inspection and interface tests |
| System architecture | SAD-001 to SAD-005 | Processing core separated from UI, adapters, evidence store, reference service, export service | Architecture review and threat/data-flow review |
| Functional/module design | FRS/DES-001 onward | Duplicate rule, mapping rule, FAIR evidence record, transformation rule, reconciliation rule | Detailed design review and unit-test specification |
| Implementation | Code and configuration | Python engine, UI, adapters, persistence, connectors | Code review, static checks, unit tests |
| Unit verification | TEST-U | Each rule produces deterministic results for known inputs | Automated unit tests and test evidence |
| Integration verification | TEST-I | UI, API, processing core, reference catalogue, and exports agree on identifiers and statuses | API/UI integration tests and contract tests |
| System verification | TEST-S | A project can be ingested, assessed, reviewed, transformed in a copy, reconciled, and exported | End-to-end test protocol and evidence package |
| User acceptance / operational qualification | TEST-UAT/OQ | A migration analyst and approver can complete the controlled workflow using realistic scenarios | UAT script, signed outcomes, known limitations |
| Release / intended-use decision | REL-001 | Release is suitable for the declared utility or deployment boundary | Traceability matrix, risk review, release decision, training/operating instructions |

## 7. Core controlled workflow

```text
Acquire source
  -> preserve original + hash + manifest
  -> profile structure and data
  -> record evidence-based findings
  -> assess quality and FAIR dimensions
  -> review duplicate candidates and exceptions
  -> select canonical meaning and source of truth
  -> map source -> canonical -> target
  -> preview reversible transformations
  -> verify counts, keys, rules, and exceptions
  -> record risk decision and approval
  -> export controlled migration package
  -> optional downstream load under separate authorization
```

## 8. Minimum evidence object

Every important finding, mapping, or transformation should be representable with:

| Field | Meaning |
|---|---|
| `evidence_id` | Stable identifier for the observation or decision |
| `project_id` | Migration/project context |
| `source_asset_id` | Immutable input and source hash |
| `rule_id` / `rule_version` | Logic that produced the finding |
| `location` | File, sheet, row, field, path, XML element, or API object |
| `observed_value` | Original evidence; never overwritten |
| `interpretation` | Human or approved rule interpretation |
| `proposed_action` | Keep, correct, map, transform, exclude, or review |
| `reference_id` | Controlled regulatory/clinical/business reference when applicable |
| `risk_status` | Open, accepted, rejected, mitigated, expired, or not applicable |
| `owner` / `approver` | Accountable roles and approval evidence |
| `verification_result` | Test, reconciliation, or sampling result after action |
| `created_at` / `updated_at` | Traceable lifecycle timestamps |

## 9. Definition of done for the requirements baseline

This baseline is complete when:

- the product objective and boundaries are approved;
- each in-scope capability has a requirement ID and a verification method;
- the sample workbook's RAG/reference pattern is represented as a reusable mapping model;
- risk acceptance is separate from automated detection and RAG display;
- source preservation, human review, and audit evidence are mandatory design controls;
- the next implementation increment is limited to a traceable vertical slice.

## 10. Recommended next vertical slice

Implement one complete, testable path before adding broad connectors:

**CSV/XLSX source → immutable manifest → profile → duplicate review → reference-backed mapping → reversible transform preview → reconciliation report → approved JSON/CSV export.**

This slice will prove the V-model traceability and operating workflow while leaving the architecture ready for XML/eCTD, dossier folder, API, and live reference connectors.
