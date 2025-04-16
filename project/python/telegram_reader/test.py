import requests

BASE_URL = "http://localhost:8002"

common_headers = {
    "Content-Type": "application/json",
    # "Authorization": f"Bearer {access_token}"
}


def create_client(api_id, api_hash):
    url = f"{BASE_URL}/clients"
    payload = {
        "api_id": api_id,
        "api_hash": api_hash
    }
    response = requests.post(url, json=payload, headers=common_headers)
    if response.status_code != 200:
        raise Exception(f"Error creating client: {response.text}")
    return response.json()  # {"session_id": "..."}


def sign_in_client(session_id, phone):
    url = f"{BASE_URL}/clients/{session_id}/sign_in"
    payload = {
        "phone": phone,
    }
    response = requests.post(url, json=payload, headers=common_headers)
    if response.status_code != 200:
        raise Exception(f"Error during sign in: {response.text}")
    return response.json()


def complete_sign_in_client(session_id, phone, code, phone_code_hash, password=None):
    url = f"{BASE_URL}/clients/{session_id}/complete_sign_in"
    payload = {
        "phone": phone,
        "code": code,
        "phone_code_hash": phone_code_hash
    }
    if password:
        payload["password"] = password
    response = requests.post(url, json=payload, headers=common_headers)
    if response.status_code != 200:
        raise Exception(f"Error completing sign in: {response.text}")
    return response.text


def list_clients():
    url = f"{BASE_URL}/clients"
    response = requests.get(url, headers=common_headers)
    if response.status_code != 200:
        raise Exception(f"Error listing clients: {response.text}")
    return response.json()


def main():
    api_id = 24529225
    api_hash = '0abc06cc13bab8c228b59bcca4284800'
    phone = '+886968893589'
    password = 'kingkingjin'

    # Step 1: Create client
    create_response = create_client(api_id, api_hash)
    session_id = create_response.get("session_id")
    print("Created client with session_id:", session_id)

    # Step 2: Sign in
    sign_in_response = sign_in_client(session_id, phone)
    print("Sign in response:", sign_in_response)
    status = sign_in_response.get("status")

    if status == "success":
        print("Signed in successfully.")
        return
    elif status == "need_code":
        phone_code_hash = sign_in_response.get("phone_code_hash")
    else:
        raise Exception("Unexpected status returned during sign in")

    print("Sign in requires verification code. Received phone_code_hash:", phone_code_hash)

    # Step 3: Complete sign in
    code = input("Enter the verification code you received: ")
    complete_response = complete_sign_in_client(session_id, phone, code, phone_code_hash, password)
    print("Complete sign in response:", complete_response)

    # Step 4: List all clients
    clients = list_clients()
    print("Clients under manager:", clients)



def load_client(session_id:str)->bool:
    """
    Load all clients from the database
    """
    url = f"{BASE_URL}/clients/{session_id}/load"
    response = requests.post(url, headers=common_headers)
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        raise Exception(f"Error loading client: {response.text}")

def get_dialogs(session_id:str)->list:
    """
    Get all dialogs for a client
    """
    url = f"{BASE_URL}/clients/{session_id}/dialogs"
    response = requests.get(url, headers=common_headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        return []
    else:
        raise Exception(f"Error getting dialogs: {response.text}")

def start_read_message(session_id:str):
    """
    Start to read message for a client
    """
    url = f"{BASE_URL}/clients/{session_id}/read_message/start"
    response = requests.post(url, headers=common_headers)
    if response.status_code != 200:
        raise Exception(f"Error starting to read message: {response.text}")
    return response.json()

def main2():
    api_id = 24529225
    api_hash = '0abc06cc13bab8c228b59bcca4284800'
    phone = '+886968893589'
    password = 'kingkingjin'
    session_id = "63f99658-6f35-4eac-b076-8ee2575a2133"
    loaded = load_client(session_id)
    if not loaded:
        raise Exception(f"session_id {session_id} not found")
    # Step 2: Sign in
    sign_in_response = sign_in_client(session_id, phone)
    print("Sign in response:", sign_in_response)
    status = sign_in_response.get("status")

    if status == "need_code":
        phone_code_hash = sign_in_response.get("phone_code_hash")
        print("Sign in requires verification code. Received phone_code_hash:", phone_code_hash)

        # Step 3: Complete sign in
        code = input("Enter the verification code you received: ")
        complete_response = complete_sign_in_client(session_id, phone, code, phone_code_hash, password)
        print("Complete sign in response:", complete_response)

    print("Signed in successfully.")
    # Step 4: List all clients
    clients = list_clients()
    print("Clients under manager:", clients)

    dialogs = get_dialogs(session_id)
    print("Dialogs under manager:", dialogs)

    # Step 4: List all clients
    clients = list_clients()
    print("Clients under manager:", clients)

    start_read_message(session_id)

if __name__ == '__main__':
    main2()