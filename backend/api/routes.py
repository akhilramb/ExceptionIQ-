import os
from collections import Counter
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from models.database import create_exception, get_all_exceptions, get_exception_by_id, update_exception
from services.hindsight_memory import is_available, list_memories, provider_name, recall_cases, retain_case

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

class ResolveRequest(BaseModel):
    status: str = "resolved"
    root_cause: str
    solution: str
    outcome: str = "successful"

@router.get("/health")
def health():
    return {"status":"healthy","service":"ExceptionIQ","memory_provider":provider_name(),"hindsight_available":is_available()}

@router.get("/exceptions")
def list_exceptions(): return {"data":get_all_exceptions()}

@router.get("/exceptions/{exception_id}")
def get_exception(exception_id:int):
    item=get_exception_by_id(exception_id)
    if not item: raise HTTPException(404,"Exception not found")
    return {"data":item}

@router.post("/exceptions",status_code=201)
def create_new_exception(data:ExceptionCreate):
    return {"data":create_exception({**data.model_dump(),"difference":data.invoice_amount-data.po_amount})}

@router.patch("/exceptions/{exception_id}")
def patch_exception(exception_id:int,updates:dict):
    if not get_exception_by_id(exception_id): raise HTTPException(404,"Exception not found")
    return {"data":update_exception(exception_id,updates)}

@router.post("/exceptions/{exception_id}/resolve")
def resolve_exception(exception_id:int,data:ResolveRequest):
    item=get_exception_by_id(exception_id)
    if not item: raise HTTPException(404,"Exception not found")
    if data.status not in {"resolved","rejected","open"}: raise HTTPException(400,"Unsupported status")
    updated=update_exception(exception_id,{"status":data.status,"resolution":data.solution})
    memory=None; warning=None
    if data.status=="resolved":
        try:
            memory=retain_case({"exception_id":exception_id,"vendor":item["vendor"],"problem_type":item["exception_type"],"amount_difference":item["difference"],"root_cause":data.root_cause,"solution":data.solution,"outcome":data.outcome,"human_decision":"approved"})
        except (httpx.HTTPError,ValueError) as exc:
            warning="Resolution was saved, but Hindsight memory could not be reached."
    return {"data":updated,"memory":memory,"memory_warning":warning}

@router.post("/investigate")
def investigate_exception(request:InvestigateRequest):
    difference=request.difference if request.difference is not None else ((request.invoice_amount or 0)-request.po_amount)
    try:
        memories=recall_cases(request.vendor,request.exception_type,float(difference or 0))
    except (httpx.HTTPError,ValueError):
        memories=[]
    recommendation=build_grounded_recommendation(request,memories)
    return {"current_exception":{"vendor":request.vendor,"invoice_number":request.invoice_number,"po_amount":request.po_amount,"exception_type":request.exception_type,"difference":difference},"similar_memories":memories,"recommendation":recommendation,"pattern_detected":len(memories)>0,"grounding":"Previous cases come from Hindsight recall. Human approval is required."}

@router.get("/memories")
def memories():
    try: return {"data":list_memories(),"provider":provider_name()}
    except (httpx.HTTPError,ValueError): return {"data":[],"provider":provider_name(),"warning":"Hindsight is not currently reachable."}

@router.get("/analytics")
def analytics():
    exceptions=get_all_exceptions(); total=len(exceptions); resolved=sum(x.get("status")=="resolved" for x in exceptions); opened=sum(x.get("status")=="open" for x in exceptions)
    try: memory_count=len(list_memories())
    except (httpx.HTTPError,ValueError): memory_count=0
    vendors=Counter(x["vendor"] for x in exceptions); types=Counter(x["exception_type"] for x in exceptions)
    return {"totals":{"exceptions":total,"open":opened,"resolved":resolved,"memories":memory_count},"resolution_rate":round(resolved/total*100,1) if total else 0,"memory_success_rate":0,"top_vendors":vendors.most_common(5),"top_exception_types":types.most_common(5)}

def build_grounded_recommendation(exception:InvestigateRequest,memories:list[dict])->dict:
    if not memories:
        return {"pattern":"No Hindsight precedent was retrieved.","root_cause":"Unknown — requires manual verification.","recommendation":"Verify the invoice, PO, contract terms and vendor documentation before taking action.","explanation":"No stored evidence was available, so ExceptionIQ did not invent a precedent.","confidence":18,"evidence_count":0,"missing_information":["Supporting invoice/PO evidence may be required"]}
    evidence=memories[:5]; causes=[m.get("root_cause") for m in evidence if m.get("root_cause")]; cause=Counter(causes).most_common(1)[0][0] if causes else "Historical exception pattern"; successful=[m for m in evidence if m.get("outcome")=="successful" and m.get("solution")]; solution=successful[0]["solution"] if successful else next((m.get("solution") for m in evidence if m.get("solution")),"Review supporting documents")
    semantic=[m.get("similarity_score") for m in evidence if m.get("similarity_score") is not None]; confidence=round(sum(semantic)/len(semantic)) if semantic else min(85,45+len(evidence)*8)
    return {"pattern":f"Hindsight retrieved {len(evidence)} relevant historical memory item(s).","root_cause":cause,"recommendation":solution,"explanation":"The recommendation uses the ranked Hindsight memories shown below; Hindsight relevance scores are retrieval signals, not certainty probabilities.","confidence":max(20,min(confidence,95)),"evidence_count":len(evidence),"missing_information":[]}
