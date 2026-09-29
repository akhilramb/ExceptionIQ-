from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from models.database import (
    create_exception,
    get_all_exceptions,
    get_exception_by_id,
    update_exception,
    get_memories_by_vendor,
    add_memory
)

router = APIRouter()

# Request models
class ExceptionCreate(BaseModel):
    vendor: str
    invoice_number: Optional[str] = ""
    po_number: Optional[str] = ""
    invoice_amount: float
    po_amount: float
    exception_type: str
    description: Optional[str] = ""

class InvestigateRequest(BaseModel):
    vendor: str
    invoice_number: Optional[str] = ""
    po_amount: float
    exception_type: str

class MemoryRecord(BaseModel):
    vendor: str
    problem_type: str
    amount_difference: float
    root_cause: str
    solution: str
    outcome: str

@router.get("/exceptions")
def list_exceptions():
    """Get all exceptions"""
    return {"data": get_all_exceptions()}


@router.get("/exceptions/{exception_id}")
def get_exception(exception_id: int):
    """Get a single exception by ID"""
    exception = get_exception_by_id(exception_id)
    if not exception:
        raise HTTPException(status_code=404, detail="Exception not found")
    return {"data": exception}


@router.post("/exceptions")
def create_new_exception(data: ExceptionCreate):
    """Create a new exception"""
    calc_difference = data.invoice_amount - data.po_amount
    exception_data = {**data.model_dump(), 'difference': calc_difference}
    exception = create_exception(exception_data)
    return {"data": exception}


@router.post("/investigate")
def investigate_exception(request: InvestigateRequest):
    """AI investigation: find similar memories and generate recommendation"""
    # Get memories related to this vendor
    memories = get_memories_by_vendor(request.vendor)

    # Calculate similarity score based on vendor match
    similarity_score = min(len(memories) * 15, 100)  # Simple scoring

    # Demo AI recommendation
    recommendation = generate_demo_recommendation(request, memories)

    return {
        "current_exception": {
            "vendor": request.vendor,
            "invoice_number": request.invoice_number,
            "po_amount": request.po_amount,
            "exception_type": request.exception_type,
            "similarity_score": similarity_score
        },
        "similar_memories": memories[:3] if memories else [],
        "recommendation": recommendation,
        "pattern_detected": len(memories) > 0
    }


@router.get("/memories")
def list_memories():
    """Get all memories"""
    from models.database import add_memory
    # Return all memories from mock Hindsight database
    import sqlite3
    from pathlib import Path

    HINDSIGHT_DB_PATH = Path(__file__).parent.parent.parent / "data" / "mock-hindsight.db"

    with sqlite3.connect(HINDSIGHT_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT * FROM memories ORDER BY created_at DESC")
        return [dict(row) for row in cursor.fetchall()]


@router.post("/memories")
def save_memory(data: MemoryRecord):
    """Save a memory to the system"""
    memory = add_memory(data.model_dump())
    return {"data": memory}


def generate_demo_recommendation(exception, memories):
    """Generate demo AI recommendation based on memories"""
    if not memories or len(memories) == 0:
        return {
            "pattern": "No similar memories found",
            "recommendation": "Verify the invoice and contact the vendor directly to clarify the difference.",
            "explanation": "This appears to be a new type of exception. Proceed with manual verification."
        }

    # Group root causes
    root_causes = [m['root_cause'] for m in memories[:5]]
    most_common_cause = max(set(root_causes), key=root_causes.count)

    # Generate pattern
    pattern = f"Previous {exception.vendor} exceptions were often caused by: {most_common_cause}"

    # Generate recommendation
    solution = memories[0]['solution']
    recommendation = {
        "pattern": pattern,
        "recommendation": f"Follow the previous solution: {solution}",
        "explanation": f"This exception matches {len(memories)} similar cases. The pattern shows {most_common_cause}."
    }

    return recommendation