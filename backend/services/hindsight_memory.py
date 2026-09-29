"""Small Hindsight HTTP adapter for ExceptionIQ.

Uses the real Hindsight retain/recall APIs. No localStorage or hand-written
similarity algorithm is used here. Configure either Hindsight Cloud or a
self-hosted server with the environment variables in .env.example.
"""
import json
import os
from typing import Any

import httpx

BASE_URL = os.getenv("HINDSIGHT_BASE_URL", "http://localhost:8888").rstrip("/")
BANK_ID = os.getenv("HINDSIGHT_BANK_ID", "exceptioniq")
API_KEY = os.getenv("HINDSIGHT_API_KEY", "").strip()
TIMEOUT = float(os.getenv("HINDSIGHT_TIMEOUT", "8"))


def _headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers


def _url(path: str) -> str:
    return f"{BASE_URL}/v1/default/banks/{BANK_ID}{path}"


def provider_name() -> str:
    return "hindsight-cloud" if "api.hindsight.vectorize.io" in BASE_URL else "hindsight-self-hosted"


def retain_case(case: dict[str, Any]) -> dict[str, Any]:
    """Persist one resolved ExceptionIQ case as a Hindsight experience."""
    exception_id = str(case.get("exception_id") or case.get("id") or "unknown")
    content = (
        f"ExceptionIQ resolved case {exception_id}. "
        f"Vendor: {case.get('vendor', '')}. "
        f"Exception type: {case.get('problem_type', '')}. "
        f"Amount difference: {case.get('amount_difference', 0)}. "
        f"Root cause: {case.get('root_cause', '')}. "
        f"Human decision: {case.get('human_decision', 'approved')}. "
        f"Resolution: {case.get('solution', '')}. "
        f"Outcome: {case.get('outcome', '')}."
    )
    metadata = {
        "exception_id": exception_id,
        "vendor": str(case.get("vendor", "")),
        "problem_type": str(case.get("problem_type", "")),
        "root_cause": str(case.get("root_cause", "")),
        "solution": str(case.get("solution", "")),
        "outcome": str(case.get("outcome", "")),
        "human_decision": str(case.get("human_decision", "approved")),
        "amount_difference": str(case.get("amount_difference", 0)),
    }
    payload = {"items": [{
        "content": content,
        "context": "ExceptionIQ accounts-payable resolution",
        "document_id": f"exceptioniq-case-{exception_id}",
        "metadata": metadata,
    }]}
    with httpx.Client(timeout=TIMEOUT) as client:
        response = client.post(_url("/memories"), headers=_headers(), json=payload)
        response.raise_for_status()
        return response.json()


def recall_cases(vendor: str, problem_type: str, amount_difference: float, max_tokens: int = 1200) -> list[dict[str, Any]]:
    """Retrieve ranked cases using Hindsight's semantic/keyword/graph/temporal recall."""
    query = (
        "Find previous successful ExceptionIQ accounts-payable cases relevant to "
        f"vendor {vendor}, exception type {problem_type}, amount difference {amount_difference}. "
        "Prioritize same-vendor and same-problem experiences and their human-approved resolutions."
    )
    payload = {"query": query, "types": ["experience", "world", "observation"], "prefer_observations": True, "max_tokens": max_tokens}
    with httpx.Client(timeout=TIMEOUT) as client:
        response = client.post(_url("/memories/recall"), headers=_headers(), json=payload)
        response.raise_for_status()
        raw = response.json().get("results", [])

    cases = []
    for rank, item in enumerate(raw[:8], start=1):
        metadata = item.get("metadata") or {}
        scores = item.get("scores") or {}
        # Hindsight scores are ranking signals, not calibrated probabilities.
        cases.append({
            "id": item.get("id"),
            "text": item.get("text", ""),
            "vendor": metadata.get("vendor", vendor),
            "problem_type": metadata.get("problem_type", problem_type),
            "root_cause": metadata.get("root_cause", ""),
            "solution": metadata.get("solution", ""),
            "outcome": metadata.get("outcome", ""),
            "human_decision": metadata.get("human_decision", ""),
            "created_at": item.get("mentioned_at") or item.get("occurred_start"),
            "document_id": item.get("document_id"),
            "rank": rank,
            "relevance_score": scores.get("final"),
            "similarity_score": round(float(scores.get("semantic") or 0) * 100, 1) if scores.get("semantic") is not None else None,
        })
    return cases


def list_memories() -> list[dict[str, Any]]:
    """List Hindsight memory units for the Memory Explorer."""
    with httpx.Client(timeout=TIMEOUT) as client:
        response = client.get(_url("/memories/list"), headers=_headers())
        response.raise_for_status()
        body = response.json()
    raw = body.get("items") or body.get("memories") or body.get("results") or []
    result = []
    for item in raw:
        metadata = item.get("metadata") or {}
        result.append({
            "id": item.get("id"), "text": item.get("text", ""),
            "vendor": metadata.get("vendor", ""), "problem_type": metadata.get("problem_type", ""),
            "root_cause": metadata.get("root_cause", ""), "solution": metadata.get("solution", ""),
            "outcome": metadata.get("outcome", ""), "human_decision": metadata.get("human_decision", ""),
            "created_at": item.get("mentioned_at") or item.get("occurred_start"),
        })
    return result


def is_available() -> bool:
    try:
        with httpx.Client(timeout=min(TIMEOUT, 2.0)) as client:
            response = client.get(f"{BASE_URL}/health/ready", headers=_headers())
            return response.status_code < 500
    except httpx.HTTPError:
        return False
