"""Dependency-free data-quality analysis for the first workbench slice."""

from __future__ import annotations

import csv
import hashlib
import io
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any


NULL_MARKERS = {"", "null", "none", "n/a", "na", "unknown"}
DATE_RE = re.compile(r"^\d{4}[-/]\d{1,2}[-/]\d{1,2}$")
ID_HINTS = ("id", "identifier", "number", "code", "key")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _normalise(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().casefold().split())


def _is_null(value: Any) -> bool:
    return _normalise(value) in NULL_MARKERS


def _infer_type(values: list[str]) -> str:
    values = [v.strip() for v in values if not _is_null(v)]
    if not values:
        return "empty"
    if all(v.casefold() in {"true", "false", "yes", "no"} for v in values):
        return "boolean"
    if all(re.fullmatch(r"[-+]?\d+", v) for v in values):
        return "integer"
    if all(re.fullmatch(r"[-+]?(?:\d+\.\d+|\d+)", v) for v in values):
        return "number"
    if all(DATE_RE.fullmatch(v) for v in values):
        return "date"
    return "text"


def parse_csv(text: str, delimiter: str | None = None) -> tuple[list[str], list[dict[str, str]]]:
    if not text or not text.strip():
        raise ValueError("The uploaded file is empty")
    sample = text[:4096]
    if delimiter is None:
        try:
            delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter
        except csv.Error:
            delimiter = ","
    reader = csv.DictReader(io.StringIO(text.lstrip("\ufeff")), delimiter=delimiter)
    if not reader.fieldnames:
        raise ValueError("The file does not contain a header row")
    headers = [str(h).strip() for h in reader.fieldnames]
    if any(not h for h in headers):
        raise ValueError("The header row contains a blank column name")
    rows: list[dict[str, str]] = []
    for row in reader:
        clean = {header: (row.get(original) or "").strip() for header, original in zip(headers, reader.fieldnames)}
        if any(value for value in clean.values()):
            rows.append(clean)
    return headers, rows


def _duplicate_groups(rows: list[dict[str, str]], headers: list[str]) -> list[dict[str, Any]]:
    raw_groups: defaultdict[tuple[str, ...], list[int]] = defaultdict(list)
    normal_groups: defaultdict[tuple[str, ...], list[int]] = defaultdict(list)
    for index, row in enumerate(rows, start=1):
        raw_groups[tuple(row.get(h, "") for h in headers)].append(index)
        normal_groups[tuple(_normalise(row.get(h, "")) for h in headers)].append(index)

    groups: list[dict[str, Any]] = []
    for signature, indices in raw_groups.items():
        if len(indices) > 1:
            groups.append({"kind": "exact", "row_numbers": indices, "match_reason": "All field values match exactly."})
    for signature, indices in normal_groups.items():
        raw_signatures = {tuple(rows[index - 1].get(h, "") for h in headers) for index in indices}
        if len(indices) > 1 and len(raw_signatures) > 1:
            groups.append({"kind": "likely", "row_numbers": indices, "match_reason": "Values match after trimming whitespace and ignoring case."})
    return groups


def _fair_assessment(headers: list[str], rows: list[dict[str, str]], source_name: str) -> list[dict[str, Any]]:
    lower_headers = [h.casefold() for h in headers]
    id_fields = [h for h in headers if any(h.casefold().endswith(hint) for hint in ID_HINTS)]
    unique_id = False
    if id_fields and rows:
        first_id = id_fields[0]
        values = [_normalise(row.get(first_id, "")) for row in rows if not _is_null(row.get(first_id, ""))]
        unique_id = bool(values) and len(values) == len(set(values))
    return [
        {
            "dimension": "Findable",
            "status": "evidence-supported" if unique_id else "needs-evidence",
            "evidence": f"{id_fields[0]} is unique." if unique_id else "No verified unique identifier was detected.",
        },
        {
            "dimension": "Accessible",
            "status": "needs-evidence",
            "evidence": f"{source_name} was supplied to the local workbench; authorization and retrieval controls need confirmation.",
        },
        {
            "dimension": "Interoperable",
            "status": "needs-evidence" if any(_infer_type([r.get(h, "") for r in rows]) == "text" for h in headers) else "evidence-supported",
            "evidence": "Structured types were inferred, but code-list and reference-data alignment still requires review.",
        },
        {
            "dimension": "Reusable",
            "status": "needs-evidence",
            "evidence": "Business definition, provenance, permitted use, and quality disposition require human confirmation.",
        },
    ]


def analyse_csv(text: str, source_name: str = "uploaded dataset", delimiter: str | None = None) -> dict[str, Any]:
    headers, rows = parse_csv(text, delimiter)
    profile_columns: list[dict[str, Any]] = []
    issues: list[dict[str, Any]] = []
    for header in headers:
        values = [row.get(header, "") for row in rows]
        non_null = [value for value in values if not _is_null(value)]
        inferred = _infer_type(values)
        blank_count = len(values) - len(non_null)
        unique_count = len({_normalise(value) for value in non_null})
        profile_columns.append(
            {
                "name": header,
                "inferred_type": inferred,
                "row_count": len(values),
                "blank_count": blank_count,
                "blank_rate": round(blank_count / len(values), 4) if values else 0,
                "unique_count": unique_count,
                "examples": non_null[:3],
            }
        )
        if blank_count:
            issues.append(
                {
                    "issue_type": "missing-values",
                    "severity": "medium" if header.casefold().endswith(ID_HINTS) else "low",
                    "field": header,
                    "count": blank_count,
                    "message": f"{blank_count} row(s) have no value for {header}.",
                    "learning": "This is a completeness signal. First confirm whether the field is required for this object and business process; do not fill blanks automatically.",
                    "fair_link": "Findable / Reusable",
                }
            )
        if "date" in header.casefold() or header.casefold().endswith("_dt"):
            invalid = [i for i, value in enumerate(values, start=1) if not _is_null(value) and not DATE_RE.fullmatch(value)]
            if invalid:
                issues.append(
                    {
                        "issue_type": "invalid-date",
                        "severity": "medium",
                        "field": header,
                        "count": len(invalid),
                        "rows": invalid[:20],
                        "message": f"{len(invalid)} row(s) do not match YYYY-MM-DD or YYYY/MM/DD.",
                        "learning": "This is a validity and interoperability signal. Confirm the allowed date format, timezone, and whether the value is a real date or an estimate.",
                        "fair_link": "Interoperable / Reusable",
                    }
                )

    duplicates = _duplicate_groups(rows, headers)
    for group in duplicates:
        issues.append(
            {
                "issue_type": "duplicate-candidate",
                "severity": "high" if group["kind"] == "exact" else "medium",
                "field": "(record)",
                "count": len(group["row_numbers"]),
                "rows": group["row_numbers"],
                "message": group["match_reason"],
                "learning": "This is a uniqueness signal. A candidate is not automatically a duplicate: compare identifiers, business meaning, lifecycle, and provenance before merging.",
                "fair_link": "Findable / Reusable",
            }
        )

    return {
        "analysis_version": "0.1.0",
        "analysed_at": _utc_now(),
        "source_name": source_name,
        "source_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "row_count": len(rows),
        "column_count": len(headers),
        "headers": headers,
        "columns": profile_columns,
        "duplicates": duplicates,
        "issues": issues,
        "fair_assessment": _fair_assessment(headers, rows, source_name),
        "risk_decision": {
            "decision": "review-required",
            "rationale": "No risk has been accepted automatically. Review data-quality evidence before transformation or migration.",
            "approver": "",
            "review_date": "",
        },
    }
