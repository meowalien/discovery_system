import json
import requests
import jwt
import config

# These are intended to be private module-level variables
_OIDC_SERVER = f"{config.KEYCLOAK_OIDC_URL}/realms/{config.KEYCLOAK_REALM}"
_url = f"{_OIDC_SERVER}/.well-known/openid-configuration"

_response = requests.get(_url)
_response.raise_for_status()
try:
    _oidc_config = _response.json()
except json.decoder.JSONDecodeError:
    print("Unable to parse JSON. Response content:")
    print(_response.text)
    raise

_jwks_uri = _oidc_config.get("jwks_uri")
_signing_algs = _oidc_config.get("id_token_signing_alg_values_supported")
_jwks_client = jwt.PyJWKClient(_jwks_uri)

def parse_jwt_token(token: str):
    signing_key = _jwks_client.get_signing_key_from_jwt(token).key

    data = jwt.decode_complete(
        token,
        key=signing_key,
        algorithms=_signing_algs,
        issuer=_OIDC_SERVER,
        leeway=60,
        audience=config.KEYCLOAK_DEMO_CLIENT_AUDIENCE
    )
    payload = data.get("payload")
    header = data.get("header")
    signature = data.get("signature")

    return payload, header, signature