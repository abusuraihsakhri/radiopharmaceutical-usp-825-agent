"""
FastAPI REST API Server for Radiopharmaceutical Usp 825 Agent.
"""
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from .base import AuditLogger, PHIGuard, SecurityException
from .models import SystemTaskPayload, ConsensusDossier
from .supervisor import SystemSupervisor
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles

supervisor = SystemSupervisor(model_provider="mock")

app = FastAPI(
    title="Radiopharmaceutical Usp 825 Agent API",
    description="Enterprise Distributed Component Platform (Nuclear Pharmacy (demonstration))",
    version="3.0.0-ENTERPRISE",
)


class ChatRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    if not os.environ.get("AUDIT_SECRET_KEY"):
        raise HTTPException(status_code=503, detail="Audit signing key is not configured")
    return {"status": "HEALTHY", "service": "radiopharmaceutical-usp-825-agent", "domain": "Nuclear Pharmacy (demonstration)", "standard": "Demonstration rules (not USP <825> compliance)", "version": "3.0.0-ENTERPRISE"}


@app.get("/metrics")
def metrics():
    return {
        "dossiers_processed_total": len(supervisor.dossier_registry),
        "audit_blocks_total": len(AuditLogger.get_trail()),
        "system_status": "NOMINAL_OPTIMAL"
    }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": "Input validation failed; review field types and permitted values."},
    )


@app.post("/api/audit")
def api_audit(payload: SystemTaskPayload):
    try:
        dossier = supervisor.process_task(payload)
        return dossier.to_dict()
    except SecurityException as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/chat")
def api_chat(req: ChatRequest):
    try:
        ans = supervisor.query_supervisory_chat(req.query)
        return {"response": ans}
    except SecurityException as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/api/audit/logs")
def api_audit_logs():
    return {"audit_trail": AuditLogger.get_trail(), "verified": AuditLogger.verify_integrity()}


# Mount last, so API routes remain authoritative while / serves the console.
app.mount("/", StaticFiles(directory=str(Path(__file__).resolve().parent.parent / "web"), html=True), name="web")
