import requests

# BASE_URL = "http://localhost:80/telegram_reader"
BASE_URL = "http://localhost:8002"
access_token = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJPXzlmY09DUVEzYlpkdVlYeGNzVk5iOTJtNUd4dW1DdVBjRzNTUThySXBrIn0.eyJleHAiOjE3NDQyMDU4NTQsImlhdCI6MTc0NDIwNTU1NCwiYXV0aF90aW1lIjoxNzQ0MjA0Njk1LCJqdGkiOiI2MzRiMDZlOC1kYjIxLTRlZDctODdlYy02ZGJjOTQzYzI1ZTEiLCJpc3MiOiJodHRwOi8vbG9jYWxob3N0OjgwODIvcmVhbG1zL2Rpc2NvdmVyeV9zeXN0ZW0iLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiYzYyZjU2OTQtMmExOS00NGNmLTgyY2ItMmE5Njg3OThkNmRiIiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiZGVtbyIsInNpZCI6Ijk2ODhkZDZjLWYyZDctNGI1Yi1hODlkLTcyOTcwMzRjZTNhOSIsImFjciI6IjAiLCJhbGxvd2VkLW9yaWdpbnMiOlsiaHR0cDovL2xvY2FsaG9zdDozMDAwIl0sInJlYWxtX2FjY2VzcyI6eyJyb2xlcyI6WyJvZmZsaW5lX2FjY2VzcyIsImRlZmF1bHQtcm9sZXMtZGlzY292ZXJ5X3N5c3RlbSIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiZGVtbyI6eyJyb2xlcyI6WyJhZG1pbiJdfSwiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJvcGVuaWQgcHJvZmlsZSBlbWFpbCIsImVtYWlsX3ZlcmlmaWVkIjp0cnVlLCJuYW1lIjoic2F5IGtlbiIsInByZWZlcnJlZF91c2VybmFtZSI6InNheWtlbiIsImdpdmVuX25hbWUiOiJzYXkiLCJmYW1pbHlfbmFtZSI6ImtlbiIsImVtYWlsIjoiYS5tZW93YWxpZW5AZ21haWwuY29tIn0.C2kMQZvc7Xpa6Q1jEZdTvA9vIQe4HeoQT-lVpawv_4T6gDpO8Sw0HIhmqrCsXvmZr6WbN1-D8W0-5m0kGKm14Bc6L5uN1fR9CxwJpPMHfZCyOR7DII118dPQtBGo45XKzk15U9ue3x-ROLjL0-KbpWHcvkb3WCWnZNxpK3cnzFNeih_nONOgNxI-YfNi7f_ceOtTIJpoGYTvrQzsyQbx-6PF_ZjZ9P-6GshXfkQzmeIzUVVpba-A1tesf3qcqW_ZMEb0vviRXxo0JYNO-TIKPJnP8Phy0JnObFDl8Ff2zrhkBPaX1ICvLM7KM_b4xK38ec2lZooEk-mWDO-QeBgAeg"

def sign_in_init(api_id, api_hash, phone, password):
    """
    呼叫 /signin/init API，回傳的資料包含 phone_code（若需要 code）
    """
    url = f"{BASE_URL}/signin/init"
    payload = {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone": phone,
        "password": password
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": access_token,
    }
    response = requests.post(url, json=payload,headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error during sign-in initialization: {response.text}")
    return response.json()

def sign_in_code(api_id, api_hash, phone, password, phone_code_hash, code):
    """
    呼叫 /signin/code API，傳入所有必要參數以完成登入
    """
    url = f"{BASE_URL}/signin/code"
    payload = {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone": phone,
        "password": password,
        "phone_code_hash": phone_code_hash,
        "code": code
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": access_token,
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error during sign-in with code: {response.text}")
    return response.json()

def main():
    # 輸入所需參數
    api_id = 24529225
    api_hash = '0abc06cc13bab8c228b59bcca4284800'
    phone = '+886968893589'
    password = 'kingkingjin'

    # 第一步：初始化登入，獲取 phone_code_hash 或直接登入成功
    data = sign_in_init(api_id, api_hash, phone, password)
    print("Init response:", data)

    status = data.get("status")
    if status == "success":
        print("Already signed in:", data.get("user"))
        return
    elif status == "need_code":
        phone_code_hash = data.get("phone_code")
    else:
        raise Exception("Unexpected status in init response")

    print("Sign-in initiated. Received phone_code_hash:", phone_code_hash)

    # 第二步：從前端輸入 code，完成登入
    code = input("Enter code: ")
    result = sign_in_code(api_id, api_hash, phone, password, phone_code_hash, code)
    if result:
        print("Sign in successful. Response:")
        print(result)
    else:
        print("Sign in with code failed.")

if __name__ == '__main__':
    main()