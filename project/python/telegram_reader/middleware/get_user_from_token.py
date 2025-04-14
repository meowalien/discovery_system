from fastapi import HTTPException
from starlette.requests import Request
from jwt_token import parse_jwt_token


def get_user_from_token(request: Request):
    request_id = getattr(request.state, "request_id", "unknown")
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail=f"[{request_id}] Missing or invalid Authorization header")
    token = auth.removeprefix("Bearer ").strip()

    try:
        payload, header, signature = parse_jwt_token(token)
        print("payload: ",payload)
        request.state.user = payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"[{request_id}] Token validation error: {e}")
    return payload
