import requests

# BASE_URL = "http://localhost:80/telegram_reader"
BASE_URL = "http://localhost:8002"

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
    response = requests.post(url, json=payload)
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
    response = requests.post(url, json=payload)
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