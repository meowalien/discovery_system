import jwt
from fastapi import HTTPException
from starlette.requests import Request

import config
from jwks_client import jwks_client, signing_algs, OIDC_SERVER


def get_user_from_token(request: Request):
    request_id = getattr(request.state, "request_id", "unknown")
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail=f"[{request_id}] Missing or invalid Authorization header")
    token = auth.removeprefix("Bearer ").strip()
    print("OIDC_SERVER: ",OIDC_SERVER)
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            key=signing_key,
            algorithms=signing_algs,
            issuer=OIDC_SERVER,
            leeway=60,
            audience=config.KEYCLOAK_DEMO_CLIENT_AUDIENCE
        )
        print("payload: ",payload)
        request.state.user = payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"[{request_id}] Token validation error: {e}")
    return payload
