from fastapi import APIRouter
from app.api.endpoints import health, parse, context, intent, risk, explain, pipeline, interceptor, rag

api_router = APIRouter()
api_router.include_router(health.router, prefix="/system", tags=["System & Health"])
api_router.include_router(parse.router, prefix="/parser", tags=["Command Parser Engine"])
api_router.include_router(context.router, prefix="/context", tags=["System Context Engine"])
api_router.include_router(intent.router, prefix="/intent", tags=["AI Intent Engine"])
api_router.include_router(risk.router, prefix="/risk", tags=["Risk Engine"])
api_router.include_router(explain.router, prefix="/explain", tags=["Explainability Engine"])
api_router.include_router(pipeline.router, prefix="/pipeline", tags=["Unified AI Safety Pipeline"])
api_router.include_router(interceptor.router, prefix="/interceptor", tags=["Terminal Interceptor & Voice NL-Shell"])
api_router.include_router(rag.router, prefix="/advanced", tags=["RAG, Sandbox & Persona Engine"])
