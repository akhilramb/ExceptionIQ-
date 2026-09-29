"""Hindsight HTTP adapter for ExceptionIQ.

Uses the real Hindsight retain/recall APIs. No localStorage or hand-written
similarity algorithm is used here. Configure Hindsight Cloud or a self-hosted
server with environment variables.
"""
import os
import re
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


def _text(item: dict[str, Any]) -> str:
    return str(item.get("text") or item.get("content") or "")


def _from_text(text: str, label: str) -> str:
    match = re.search(rf"{re.escape(label)}:\s*(.*?)(?=\.\s+[A-Z][A-Za-z ]+:|\.$|$)", text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _normalise(item: dict[str, Any], fallback_vendor: str = "", fallback_problem: str = "") -> dict[str, Any]:
    metadata = item.get("metadata") or {}
    text = _text(item)
    return {
        "id": item.get("id") or item.get("memory_id") or item.get("document_id") or text[:80],
        "text": text,
        "vendor": metadata.get("vendor") or _from_text(text, "Vendor") or fallback_vendor,
        "problem_type": metadata.get("problem_type") or _from_text(text, "Exception type") or fallback_problem,
        "root_cause": metadata.get("root_cause") or _from_text(text, "Root cause"),
        "solution": metadata.get("solution") or _from_text(text, "Resolution"),
        "outcome": metadata.get("outcome") or _from_text(text, "Outcome"),
        "human_decision": metadata.get("human_decision") or _from_text(text, "Human decision"),
        "created_at": item.get("mentioned_at") or item.get("occurred_start") or item.get("created_at"),
        "document_id": item.get("document_id") or metadata.get("document_id"),
    }


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


def _recall(query: str, max_tokens: int) -> list[dict[str, Any]]:
    """Call Hindsight recall without imposing a local similarity algorithm."""
    payload = {
        "query": query,
        "types": ["experience", "world", "observation"],
        "prefer_observations": False,
        "max_tokens": max_tokens,
    }
    with httpx.Client(timeout=TIMEOUT) as client:
        response = client.post(_url("/memories/recall"), headers=_headers(), json=payload)
        response.raise_for_status()
        return response.json().get("results", [])


def recall_cases(vendor: str, problem_type: str, amount_difference: float, max_tokens: int = 1200) -> list[dict[str, Any]]:
    """Retrieve previous cases using Hindsight recall, with a persistent-bank fallback.

    The fallback does not invent similarity. It only selects exact vendor/problem
    precedents already stored in Hindsight when Cloud recall has not yet surfaced
    a newly retained fact (for example while indexing/consolidation is catching up).
    """
    query = f"{vendor} {problem_type}"
    raw = _recall(query, max_tokens)

    cases = []
    for rank, item in enumerate(raw[:8], start=1):
        case = _normalise(item, vendor, problem_type)
        scores = item.get("scores") or {}
        semantic = scores.get("semantic")
        case.update({
            "rank": rank,
            "relevance_score": scores.get("final"),
            "similarity_score": round(float(semantic) * 100, 1) if semantic is not None else None,
            "retrieval_method": "hindsight-recall",
        })
        if case["vendor"] and case["problem_type"] and (case["solution"] or case["root_cause"]):
            cases.append(case)

    if cases:
        return cases

    # Hindsight's list endpoint is still the same persistent memory layer. This
    # exact metadata match is a safe fallback and intentionally has no fabricated
    # similarity score.
    vendor_key = vendor.strip().casefold()
    problem_key = problem_type.strip().casefold()
    exact = [
        memory for memory in list_memories()
        if memory.get("vendor", "").strip().casefold() == vendor_key
        and memory.get("problem_type", "").strip().casefold() == problem_key
    ]
    for rank, case in enumerate(exact[:8], start=1):
        case.update({
            "rank": rank,
            "relevance_score": None,
            "similarity_score": None,
            "retrieval_method": "hindsight-exact-memory-fallback",
        })
    return exact[:8]


def list_memories() -> list[dict[str, Any]]:
    """List usable ExceptionIQ memory units for the Memory Explorer."""
    with httpx.Client(timeout=TIMEOUT) as client:
        response = client.get(_url("/memories/list"), headers=_headers())
        response.raise_for_status()
        body = response.json()
    raw = body.get("items") or body.get("memories") or body.get("results") or []
    result = []
    seen = set()
    for item in raw:
        memory = _normalise(item)
        if not memory["vendor"] or not memory["problem_type"] or not (memory["solution"] or memory["root_cause"]):
            continue
        key = (memory["vendor"].lower(), memory["problem_type"].lower(), memory["root_cause"].lower(), memory["solution"].lower(), memory["outcome"].lower())
        if key in seen:
            continue
        seen.add(key)
        result.append(memory)
    return result


def is_available() -> bool:
    try:
        with httpx.Client(timeout=min(TIMEOUT, 2.0)) as client:
            response = client.get(f"{BASE_URL}/health/ready", headers=_headers())
            return response.status_code < 500
    except httpx.HTTPError:
        return False
