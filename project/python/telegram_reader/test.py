import requests

BASE_URL = "http://localhost:8000"

def sign_in_init(api_id, api_hash, phone, password):
    url = f"{BASE_URL}/signin/init"
    payload = {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone": phone,
        "password": password
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print("Error during init sign in:", response.text)
        return None
    data = response.json()
    status = data.get("status")

    match status:
        case "need_code":
            return data.get("session_id")

        case "success":
            return None




def sign_in_code(session_id, code):
    url = f"{BASE_URL}/signin/code"
    payload = {
        "session_id": session_id,
        "code": code
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        print("Error during code sign in:", response.text)
        return None
    return response.json()

def main():
    # 輸入所需參數
    api_id = 24529225 #int(input("Enter api_id: "))
    api_hash ='0abc06cc13bab8c228b59bcca4284800' #input("Enter api_hash: ")
    phone ='+886968893589' #input("Enter phone: ")
    password ='kingkingjin' #input("Enter password: ")

    # 第一步：初始化登入並獲取 session_id
    session_id = sign_in_init(api_id, api_hash, phone, password)
    if session_id is None:
        print("Login successful. No code needed.")
        return

    print("Session initiated. Session ID:", session_id)

    # 第二步：輸入 code，完成登入
    code = input("Enter code: ")
    result = sign_in_code(session_id, code)
    if result:
        print("Sign in successful. Response:")
        print(result)
    else:
        print("Sign in with code failed.")

if __name__ == '__main__':
    main()