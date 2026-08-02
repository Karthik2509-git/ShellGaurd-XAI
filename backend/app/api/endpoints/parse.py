from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.parser.ast_parser import command_parser
from app.parser.metadata_extractor import CommandMetadata

router = APIRouter()

class ParseRequest(BaseModel):
    command: str

@router.post("/parse", response_model=CommandMetadata, summary="Parse Linux Command & Extract AST Metadata")
async def parse_command(request: ParseRequest):
    """
    Parses a raw Linux shell command into AST structure, flags, targets, 
    and checks for anti-evasion obfuscation attempts.
    """
    if not request.command or not request.command.strip():
        raise HTTPException(status_code=400, detail="Command string cannot be empty")
        
    metadata = command_parser.parse(request.command)
    return metadata
