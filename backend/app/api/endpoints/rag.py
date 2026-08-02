from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.rag.retriever import rag_retriever
from app.sandbox.dry_run import sandbox_engine, SandboxDiff
from app.persona.engine import persona_engine, OperatorRole, PersonaProfile

router = APIRouter()

class RAGQueryRequest(BaseModel):
    command: str

class SimulateRequest(BaseModel):
    command: str
    targets: List[str]

@router.post("/rag/query", summary="Query RAG Knowledge Base (Man pages, CIS Benchmarks)")
async def query_rag(request: RAGQueryRequest):
    guidelines = rag_retriever.retrieve_guidelines(request.command)
    return {"command": request.command, "guidelines": guidelines}

@router.post("/sandbox/simulate", response_model=SandboxDiff, summary="Virtual Dry-Run Sandbox Simulation")
async def simulate_sandbox(request: SimulateRequest):
    diff = sandbox_engine.simulate_execution(request.command, request.targets)
    return diff

@router.get("/persona/profile", response_model=PersonaProfile, summary="Get Operator Persona Profile")
async def get_persona(role: OperatorRole = OperatorRole.DEVELOPER):
    return persona_engine.get_profile(role)
