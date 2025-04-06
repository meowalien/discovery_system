from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

class InitSignInRequest(BaseModel):
    api_id: int
    api_hash: str
    phone: str
    password: str

class CodeSignInRequest(BaseModel):
    session_id: str
    code: str



@dataclass
class TelethonLoginSessionData:
    """
    Represents the session data stored in Redis.
    """
    api_id: int
    api_hash: str
    phone: str
    password: str
    phone_code_hash: Optional[str] = None