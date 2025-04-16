from pydantic import BaseModel, UUID4

from typing import Optional
class CreateClientRequest(BaseModel):
    api_id: int
    api_hash: str

class CreateClientResponse(BaseModel):
    session_id: UUID4

class SignInClientRequest(BaseModel):
    phone: str


class SignInClientResponse(BaseModel):
    status: str
    phone_code_hash: Optional[str] = None


class InitSignInStatus:
    NEED_CODE = "need_code"
    SUCCESS = "success"


class CompleteSignInRequest(BaseModel):
    phone: str
    password: Optional[str] = None
    code: str
    phone_code_hash: str