"""Public regulatory and clinical source catalogue and read-only probes."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from typing import Any


SOURCE_CATALOG = [
    {
        "id": "fda-guidance",
        "name": "FDA Guidance Documents",
        "category": "Regulatory",
        "jurisdiction": "United States",
        "url": "https://www.fda.gov/regulatory-information/search-fda-guidance-documents",
        "mode": "HTML search page",
    },
    {
        "id": "ema-rss",
        "name": "EMA Regulatory and Scientific Guidelines",
        "category": "Regulatory",
        "jurisdiction": "European Union",
        "url": "https://www.ema.europa.eu/en/news-events/rss-feeds",
        "mode": "RSS catalogue",
    },
    {
        "id": "ich-ctd",
        "name": "ICH CTD / eCTD",
        "category": "Dossier standard",
        "jurisdiction": "International",
        "url": "https://admin.ich.org/page/ctd",
        "mode": "HTML / linked documents",
    },
    {
        "id": "clinicaltrials-api",
        "name": "ClinicalTrials.gov API",
        "category": "Clinical",
        "jurisdiction": "United States / global public registry",
        "url": "https://clinicaltrials.gov/api/v2/version",
        "mode": "JSON API",
    },
    {
        "id": "ctis-public",
        "name": "CTIS Public Portal",
        "category": "Clinical / regulatory",
        "jurisdiction": "European Union / EEA",
        "url": "https://euclinicaltrials.eu/",
        "mode": "Public portal",
    },
]


def _probe(source: dict[str, str], timeout: float = 8.0) -> dict[str, Any]:
    started = time.perf_counter()
    request = urllib.request.Request(source["url"], headers={"User-Agent": "regulatory-migration-workbench/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read(4096)
            content_type = response.headers.get("Content-Type", "")
            parsed_json = None
            if "json" in content_type:
                try:
                    parsed_json = json.loads(payload.decode("utf-8", errors="replace"))
                except json.JSONDecodeError:
                    parsed_json = None
            return {
                **source,
                "status": "reachable",
                "http_status": response.status,
                "content_type": content_type,
                "response_bytes_sampled": len(payload),
                "api_payload": parsed_json,
                "latency_ms": round((time.perf_counter() - started) * 1000, 1),
                "error": "",
            }
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return {
            **source,
            "status": "unreachable",
            "http_status": None,
            "content_type": "",
            "response_bytes_sampled": 0,
            "api_payload": None,
            "latency_ms": round((time.perf_counter() - started) * 1000, 1),
            "error": str(exc),
        }


def check_sources(source_ids: list[str] | None = None) -> list[dict[str, Any]]:
    selected = [source for source in SOURCE_CATALOG if not source_ids or source["id"] in source_ids]
    return [_probe(source) for source in selected]

