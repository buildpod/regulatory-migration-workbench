"""Guided learning content for FAIR and practical data cleanup."""

from __future__ import annotations


LEARNING_CONTENT = {
    "fair_principles": [
        {
            "id": "findable",
            "name": "Findable",
            "question": "Can a person or machine locate the right dataset and record?",
            "plain_language": "Give the dataset a name, persistent identifier, useful metadata, and searchable fields. A record that exists but cannot be reliably located is not operationally findable.",
            "evidence": ["Unique identifier", "Dataset title and description", "Owner and source system", "Searchable catalogue metadata"],
            "cleanup_connection": "Duplicates and missing identifiers weaken findability.",
        },
        {
            "id": "accessible",
            "name": "Accessible",
            "question": "Can an authorised person or machine retrieve it under the right conditions?",
            "plain_language": "Accessible does not mean public. Sensitive clinical or regulatory data can be FAIR when access conditions, authentication, retention, and retrieval instructions are explicit.",
            "evidence": ["Access method", "Permission model", "Retrieval instructions", "Retention and availability rules"],
            "cleanup_connection": "A clean record is not useful if authorised users cannot retrieve it or do not know which version to use.",
        },
        {
            "id": "interoperable",
            "name": "Interoperable",
            "question": "Can another system understand the meaning and format without guessing?",
            "plain_language": "Use shared identifiers, controlled vocabularies, explicit data types, documented relationships, and machine-readable metadata. Interoperability is about meaning as well as file format.",
            "evidence": ["Controlled vocabulary", "Documented data type", "Reference-data crosswalk", "Relationship and key rules"],
            "cleanup_connection": "Invalid dates, free-text codes, inconsistent status values, and broken keys are interoperability problems.",
        },
        {
            "id": "reusable",
            "name": "Reusable",
            "question": "Can someone safely use the data again and understand its limits?",
            "plain_language": "Document provenance, quality, business definitions, permitted use, licence or access conditions, and known limitations. Reuse requires context, not just a downloadable file.",
            "evidence": ["Provenance and lineage", "Data-quality results", "Business definitions", "Usage constraints and limitations"],
            "cleanup_connection": "A transformation without a rule, owner, rationale, or verification result is difficult to reuse or defend.",
        },
    ],
    "cleanup_steps": [
        {"number": 1, "title": "Preserve the original", "action": "Keep the source extract immutable and calculate a hash. Never clean the only copy.", "why": "This protects traceability and lets you prove what was changed."},
        {"number": 2, "title": "Profile before changing", "action": "Measure completeness, uniqueness, types, formats, code values, and relationships.", "why": "You need a baseline before deciding what is wrong."},
        {"number": 3, "title": "Separate evidence from judgement", "action": "Record the detected issue first; then ask a data owner whether it is truly wrong and how important it is.", "why": "A blank field may be an error, an allowed exception, or out of scope."},
        {"number": 4, "title": "Define the canonical meaning", "action": "Choose the source of truth, survivor record, code mapping, or business rule before transforming.", "why": "Cleaning without a meaning decision can make data look consistent but become wrong."},
        {"number": 5, "title": "Transform reversibly", "action": "Apply a versioned rule to a copy and retain rejected or excluded records with reasons.", "why": "A rule must be explainable, repeatable, and reviewable."},
        {"number": 6, "title": "Verify after cleaning", "action": "Compare counts, duplicates, key integrity, exceptions, and samples before approving the result.", "why": "A successful script run does not prove the data is fit for migration."},
    ],
    "quality_vs_fair": {
        "title": "Data quality is not the same as FAIR",
        "text": "Quality asks whether the data is correct, complete, valid, consistent, unique, timely, and fit for its intended use. FAIR asks whether people and machines can find, access, understand, and reuse it under defined conditions. They overlap, but one does not prove the other.",
    },
    "sources": [
        {"label": "GO FAIR overview", "url": "https://www.go-fair.org/how-to-go-fair/"},
        {"label": "Original FAIR Guiding Principles", "url": "https://doi.org/10.1038/sdata.2016.18"},
    ],
}

