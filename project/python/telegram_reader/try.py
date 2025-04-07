import base64

import jwt
import requests


access_token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJPXzlmY09DUVEzYlpkdVlYeGNzVk5iOTJtNUd4dW1DdVBjRzNTUThySXBrIn0.eyJleHAiOjE3NDQwMjYxNDYsImlhdCI6MTc0NDAyNTg0NiwiYXV0aF90aW1lIjoxNzQ0MDI1NTc4LCJqdGkiOiIyMjczNzQ3Yy1iMjAyLTQ5YjQtODE2ZS02MTdjYTkyMTg3MDAiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODIvcmVhbG1zL2Rpc2NvdmVyeV9zeXN0ZW0iLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiYzYyZjU2OTQtMmExOS00NGNmLTgyY2ItMmE5Njg3OThkNmRiIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiZGVtbyIsInNpZCI6IjViZDQ0OTRlLWIyNzEtNGNlOS1iNzYwLTc0OTFiNWY3MDNlYiIsImFjciI6IjEiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cDovL2xvY2FsaG9zdDozMDAwIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsImRlZmF1bHQtcm9sZXMtZGlzY292ZXJ5X3N5c3RlbSIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgb2ZmbGluZV9hY2Nlc3MgcHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwibmFtZSI6InNheSBrZW4iLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzYXlrZW4iLCJnaXZlbl9uYW1lIjoic2F5IiwiZmFtaWx5X25hbWUiOiJrZW4iLCJlbWFpbCI6ImEubWVvd2FsaWVuQGdtYWlsLmNvbSJ9.drclcu9XJFxm0WN_0EBmDEtRbshEjqIgu7RYcCayFLxZujF0RxQ2r1pauuBIuGlxEdZK6QgMexazFuJpwBIWpXBTfS-w2sGiwvbl0wuqdh6rGZ1bqNZh7GXDRdTpHkXuicZaEecFQTsXwnQuw0LEbgiHgvXCBmZ3zMJw6yZ74g_tMGmEQWmi4V3xzYdNl8-lTF2PAt10sjYZBWE4Ivm_K5sDYRIHMgqA5l21hHSXZ_ZRR0kDzZJsmeV9y6-f-k2cHUkuCZ7JmDmeJ-uMhASZPbKm7-zSwjaqrbSuFZ_AQ1w9Kff11BnKiFQBaKaxr7WwS6T9jgn7JvquZm00WDu83Q"



# in OIDC, you must know your client_id (this is the OAuth 2.0 client_id)
audience = "account"

# example of fetching data from your OIDC server
# see: https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderConfig
oidc_server = "http://localhost:8082/realms/discovery_system"
oidc_config = requests.get(
    f"{oidc_server}/.well-known/openid-configuration"
).json()
signing_algos = oidc_config["id_token_signing_alg_values_supported"]

print("signing_algos: ",signing_algos)

# setup a PyJWKClient to get the appropriate signing key
jwks_client = jwt.PyJWKClient(oidc_config["jwks_uri"])

print("jwks_client: ",jwks_client)

# get signing_key from access_token
signing_key = jwks_client.get_signing_key_from_jwt(access_token)
print("signing_key: ",signing_key)


# now, decode_complete to get payload + header
data = jwt.decode_complete(
    access_token,
    key=signing_key,
    algorithms=signing_algos,
    audience=audience,
    issuer=oidc_server,
    leeway=60,  # 允许 60 秒钟的时间偏差
)


payload, header, signature = data["payload"], data["header"], data["signature"]

print("data: ",payload)