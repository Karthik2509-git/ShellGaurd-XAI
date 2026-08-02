from typing import List, Optional
from pydantic import BaseModel, Field

class CommandMetadata(BaseModel):
    raw_command: str = Field(..., description="Original command string entered by user")
    clean_command: str = Field(..., description="De-obfuscated clean command string")
    base_command: str = Field(..., description="Primary executable binary/command (e.g. rm, chmod)")
    flags: List[str] = Field(default_factory=list, description="Extracted command flags (e.g. -r, -f, -777)")
    targets: List[str] = Field(default_factory=list, description="Target directories, files, or wildcards")
    is_recursive: bool = Field(default=False, description="Flag indicating recursive operation")
    is_force: bool = Field(default=False, description="Flag indicating forced operation (-f)")
    is_sudo: bool = Field(default=False, description="Executed with root/sudo privileges")
    is_obfuscated: bool = Field(default=False, description="Flag indicating detected evasion attempt")
    obfuscation_type: Optional[str] = Field(default=None, description="Type of obfuscation detected")
    has_redirection: bool = Field(default=False, description="Contains file redirection operators (>, >>)")
    pipe_commands: List[str] = Field(default_factory=list, description="Chained pipeline commands")
    target_is_wildcard: bool = Field(default=False, description="Targets root / or wildcard * / ~")
    subshell_calls: List[str] = Field(default_factory=list, description="Subshell expressions $(...) or `...`")
