"""
FastAPI REST API Server for USP-825 Sentinel: Nuclear Medicine Radiopharmaceutical Quality Agent.
"""
from typing import Dict, Any
from .models import FrontierPayload
from .agents import USP825Coordinator

coordinator = USP825Coordinator()


def create_app():
    try:
        from fastapi import FastAPI, HTTPException
        from pydantic import BaseModel, Field
        from agents.base import PHIGuard, SecurityException

        app = FastAPI(
            title="USP-825 Sentinel: Nuclear Medicine Radiopharmaceutical Quality Agent",
            description="Demonstration-only metric screening; does not calculate Mo-99 breakthrough, ITLC purity, decay, or USP <825> compliance.",
            version="2.0.0-FRONTIER",
        )

        class TaskRequest(BaseModel):
            task_id: str = Field(default="TASK-2026-001", min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._-]+$")
            target_identifier: str = Field(default="TARGET-BIO-KEY", min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._-]+$")
            primary_metric: float = Field(default=28.5, ge=-1e6, le=1e6, allow_inf_nan=False)
            secondary_metric: float = Field(default=14.2, ge=-1e6, le=1e6, allow_inf_nan=False)
            status_descriptor: str = Field(default="DISCORDANT_ANOMALY", max_length=128)
            is_critical_flag: bool = True
            attributes: Dict[str, Any] = Field(default_factory=dict)

        class ChatRequest(BaseModel):
            query: str

        @app.get("/health")
        def health():
            return {"status": "HEALTHY", "system": "radiopharmaceutical-usp-825-agent", "domain": "Nuclear Pharmacy", "version": "2.0.0-FRONTIER"}

        @app.post("/api/audit")
        def api_audit(req: TaskRequest):
            try:
                PHIGuard.assert_no_phi(req.model_dump_json())
            except SecurityException:
                raise HTTPException(status_code=422, detail="Sensitive identifiers are not permitted")
            payload = FrontierPayload(
                task_id=req.task_id,
                target_identifier=req.target_identifier,
                primary_metric=req.primary_metric,
                secondary_metric=req.secondary_metric,
                status_descriptor=req.status_descriptor,
                is_critical_flag=req.is_critical_flag,
                attributes=req.attributes,
            )
            return coordinator.process(payload)

        @app.post("/api/chat")
        def api_chat(req: ChatRequest):
            return {"response": coordinator.query_supervisory_chat(req.query)}

        return app
    except ImportError:
        return None
