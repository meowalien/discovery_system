import json

import requests
import jwt
import config

# 建構 OIDC 服務 URL
OIDC_SERVER = f"{config.KEYCLOAK_OIDC_URL}/realms/{config.KEYCLOAK_REALM}"
url = f"{OIDC_SERVER}/.well-known/openid-configuration"
print("url: ",url)
# 取得 .well-known 的 OIDC 配置
response = requests.get(url)
response.raise_for_status()  # 當請求失敗時會丟出 HTTPError
try:
    oidc_config = response.json()
except json.decoder.JSONDecodeError:
    print("无法解析 JSON，响应内容为:")
    print(response.text)
    raise  # 或者进一步处理错误
jwks_uri = oidc_config.get("jwks_uri")
print("jwks_uri: ",jwks_uri)
signing_algs = oidc_config.get("id_token_signing_alg_values_supported")

# 利用 PyJWKClient 建立 jwks_client 實例
jwks_client = jwt.PyJWKClient(jwks_uri)
