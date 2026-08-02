from fastapi import APIRouter
from pydantic import BaseModel
from app.interceptor.voice_nl_shell import voice_nl_engine, NLToCommandResult

router = APIRouter()

class NLTranslateRequest(BaseModel):
    prompt: str

@router.post("/nl_translate", response_model=NLToCommandResult, summary="Translate Natural Language / Voice to Linux Shell Command")
async def translate_nl(request: NLTranslateRequest):
    """
    Converts natural language ("Safely delete old build files") into valid shell commands.
    """
    result = await voice_nl_engine.translate_nl_to_command(request.prompt)
    return result
