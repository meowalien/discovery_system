# app/models.py
from pydantic import BaseModel

class InitSignInRequest(BaseModel):
    api_id: int
    api_hash: str
    phone: str
    password: str

class CodeSignInRequest(BaseModel):
    session_id: str
    code: str