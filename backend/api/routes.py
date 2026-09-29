import os
from collections import Counter
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from models.database import (
    add_memory, create_exception, get_all_exceptions, get_all_memories,
    get_exception_by_id, search_memories, update_exception,
)

router = APIRouter()


class ExceptionCreate(BaseModel):
    vendor: str = Field(min_length=2, max_length=120)
    invoice_number: Optional[str] = ""
    po_number: Optional[str] = ""
    invoice_amount: float = Field(ge=0)
    po_amount: float = Field(ge=0)
    exception_type: str = Field(min_length=2, max_length=120)
    description: Optional[str] = ""


class InvestigateRequest(BaseModel):
    vendor: str
    invoice_number: Optional[str] = ""
    po_amount: float = 0
    invoice_amount: Optional[float] = None
    difference: Optional[float] = None
    exception_type: str
    description: Optional[str] = ""


class MemoryRecord(BaseModel):
    vendor: str
    problem_type: str
    amount_difference: float = 0
    root_cause: str
    solution: str
    outcome: str


class ResolveRequest(BaseModel):
    status: str = "resolved"
    root_cause: str
    solution: str
    outcome: str = "successful"


@router.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "ExceptionIQ",
        "ai_provider": "openai" if os.getenv("OPENAI_API_KEY") else "grounded-local-fallback",
        "memory_provider": "local-hindsight-compatible-store",
    }


@router.get("/exceptions")
def list_exceptions():
    return {"data": get_all_exceptions()}


@router.get("/exceptions/{exception_id}")
def get_exception(exception_id: int):
    exception = get_exception_by_id(exception_id)
    if not exception:
        raise HTTPException(status_code=404, detail="Exception not found")
    return {"data": exception}


@router.post("/exceptions", status_code=201)
def create_new_exception(data: ExceptionCreate):
    calc_difference = data.invoice_amount - data.po_amount
    return {"data": create_exception({**data.model_dump(), "difference": calc_difference})}


@router.patch("/exceptions/{exception_id}")
def patch_exception(exception_id: int, updates: dict):
    if not get_exception_by_id(exception_id):
        raise HTTPException(status_code=404, detail="Exception not found")
    return {"data": update_exception(exception_id, updates)}


@router.post("/exceptions/{exception_id}/resolve")
def resolve_exception(exception_id: int, data: ResolveRequest):
    exception = get_exception_by_id(exception_id)
    if not exception:
        raise HTTPException(status_code=404, detail="Exception not found")
    if data.status not in {"resolved", "rejected", "open"}:
        raise HTTPException(status_code=400, detail="Unsupported status")
    updated = update_exception(exception_id, {"status": data.status, "resolution": data.solution})
    memory = None
    if data.status == "resolved":
        memory = add_memory({
            "vendor": exception["vendor"],
            "problem_type": exception["exception_type"],
            "amount_difference": exception["difference"],
            "root_cause": data.root_cause,
            "solution": data.solution,
            "outcome": data.outcome,
        })
    return {"data": updated, "memory": memory}


@router.post("/investigate")
def investigate_exception(request: InvestigateRequest):
    difference = request.difference
    if difference is None and request.invoice_amount is not None:
        difference = request.invoice_amount - request.po_amount
    difference = float(difference or 0)
    memories = search_memories(request.vendor, request.exception_type, difference, limit=5)
    recommendation = build_grounded_recommendation(request, memories)
    confidence = recommendation["confidence"]
    return {
        "current_exception": {
            "vendor": request.vendor,
            "invoice_number": request.invoice_number,
            "po_amount": request.po_amount,
            "exception_type": request.exception_type,
            "difference": difference,
            "similarity_score": confidence,
        },
        "similar_memories": memories,
        "recommendation": recommendation,
        "pattern_detected": bool(memories and memories[0]["similarity_score"] >= 45),
        "grounding": "Recommendations are generated only from stored historical cases; human approval is required.",
    }


@router.get("/memories")
def list_memories():
    return {"data": get_all_memories()}


@router.post("/memories", status_code=201)
def save_memory(data: MemoryRecord):
    return {"data": add_memory(data.model_dump())}


@router.get("/analytics")
def analytics():
    exceptions = get_all_exceptions()
    memories = get_all_memories()
    total = len(exceptions)
    resolved = sum(1 for item in exceptions if item.get("status") == "resolved")
    open_count = sum(1 for item in exceptions if item.get("status") == "open")
    vendor_counts = Counter(item["vendor"] for item in exceptions)
    type_counts = Counter(item["exception_type"] for item in exceptions)
    successful_memories = sum(1 for item in memories if item.get("outcome") == "successful")
    return {
        "totals": {"exceptions": total, "open": open_count, "resolved": resolved, "memories": len(memories)},
        "resolution_rate": round((resolved / total) * 100, 1) if total else 0,
        "memory_success_rate": round((successful_memories / len(memories)) * 100, 1) if memories else 0,
        "top_vendors": vendor_counts.most_common(5),
        "top_exception_types": type_counts.most_common(5),
    }


def build_grounded_recommendation(exception: InvestigateRequest, memories: list[dict]) -> dict:
    if not memories:
        return {
            "pattern": "No sufficiently similar historical case was found.",
            "root_cause": "Unknown — requires manual verification.",
            "recommendation": "Verify the invoice, PO, contract terms and vendor documentation before taking action.",
            "explanation": "ExceptionIQ has no stored evidence for this pattern yet, so it will not invent a historical precedent.",
            "confidence": 18,
            "evidence_count": 0,
        }

    strong = [m for m in memories if m["similarity_score"] >= 40]
    evidence = strong or memories[:2]
    causes = [m["root_cause"] for m in evidence if m.get("root_cause")]
    common_cause = Counter(causes).most_common(1)[0][0] if causes else "Historical exception pattern"
    successful = [m for m in evidence if m.get("outcome") == "successful" and m.get("solution")]
    solution = successful[0]["solution"] if successful else evidence[0].get("solution", "Review supporting documents")
    confidence = round(sum(m["similarity_score"] for m in evidence) / len(evidence))
    confidence = max(20, min(confidence, 95))
    return {
        "pattern": f"{len(evidence)} related historical case(s) point to: {common_cause}",
        "root_cause": common_cause,
        "recommendation": solution,
        "explanation": f"The recommendation is grounded in {len(evidence)} stored case(s), led by a {evidence[0]['similarity_score']}% similarity match. Review the evidence before approval.",
        "confidence": confidence,
        "evidence_count": len(evidence),
    }
