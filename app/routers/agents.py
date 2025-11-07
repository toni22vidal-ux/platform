from fastapi import APIRouter, HTTPException
from typing import Dict
from multinicho_agents.lead_qualifier import LeadQualifier

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/run")
def run_agent(payload: Dict):
    agent = payload.get("agent")
    data = payload.get("input", {})
    if not agent:
        raise HTTPException(400, "Missing 'agent'")
    if agent == "lead_qualifier":
        out = LeadQualifier().run(data)
        return {"ok": True, "agent": agent, "output": out}
    return {"ok": True, "agent": agent, "input": data, "note": "fallback"}
