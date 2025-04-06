from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel

class InitSignInRequest(BaseModel):
    api_id: int
    api_hash: str
    phone: str
    password: str

class CodeSignInRequest(BaseModel):
    api_id: int
    api_hash: str
    phone: str
    password: str
    code: str
    phone_code_hash: str
