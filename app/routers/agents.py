from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/run")
def run_agent(payload: dict):
    agent = payload.get("agent")
    data = payload.get("input", {})
    if not agent:
        raise HTTPException(400, "Missing 'agent'")
    return {"ok": True, "agent": agent, "input": data}
