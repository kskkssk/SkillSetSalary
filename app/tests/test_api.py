import logging
from fastapi.testclient import TestClient
import tempfile
import os

logging.basicConfig(level=logging.DEBUG)


def register_user(client: TestClient, password: str, email: str):
    response = client.post('/users/signup',
                           json={"password": password,
                                 "email": email})
    return response


def login_user(client: TestClient, email: str, password: str):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'password',
        'username': email,
        'password': password,
    }
    login_response = client.post('/users/signin', headers=headers, data=data)
    assert login_response.status_code == 200
    return login_response


def test_home_request(client: TestClient):
    response = client.get('/test')
    assert response.status_code == 200
    assert response.json() == {'message': 'success'}


def test_register(client: TestClient):
    response = register_user(client, "0880", "sashakudasheva7@gmail.com")
    assert response.status_code == 200
    assert response.json()['email'] == 'sashakudasheva7@gmail.com'


def test_login(client: TestClient):
    login_response = login_user(client, "sashakudasheva@gmail.com", "0880")
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()


def test_request(client: TestClient):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(b"This is an invalid file.")
        tmp_file_path = tmp_file.name

    try:
        files = {'data': (tmp_file_path, open(tmp_file_path, 'rb'))}
        response = client.post('/users/handle_request', files=files)
    finally:
        os.remove(tmp_file_path)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['message'] == 'Task sent to worker'


def test_interpret(client: TestClient):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(b"This is an invalid file.")
        tmp_file_path = tmp_file.name

    try:
        files = {'data': (tmp_file_path, open(tmp_file_path, 'rb'))}
        response = client.post('/users/interpret', files=files)
    finally:
        os.remove(tmp_file_path)

    assert response.status_code == 200
    response_json = response.json()
    assert response_json['message'] == 'Task sent to worker'


def test_balance(client: TestClient):
    login_user(client, 'sashakudasheva3@gmail.com', '0880')
    response = client.get('/balances/balance')
    assert response.status_code == 200
    assert 'amount' in response.json()


def test_add_balance(client: TestClient):
    login_user(client, 'sashakudasheva5@gmail.com', '0880')
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {'amount': 300.0}
    response = client.post(
        "/balances/add_balance", headers=headers, data=data)
    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    response_json = response.json()
    assert "amount" in response_json, "Response JSON does not contain 'amount'"
    assert response_json["amount"] == 300.0, f"Expected amount 300.0 but got {response_json['amount']}"


def test_invalid_email(client: TestClient):
    response = register_user(client, "0880", "sashakkk")
    assert response.status_code == 422
    logging.debug(response.status_code)
    assert 'detail' in response.json()


def test_invalid_file(client: TestClient):

    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
        tmp_file.write(b"This is an invalid file.")
        tmp_file_path = tmp_file.name

    try:
        files = {'data': (tmp_file_path, open(tmp_file_path, 'rb'))}
        response_interpret = client.post("/users/interpret", files=files)
        response = client.post('/users/handle_request', files=files)
    finally:
        os.remove(tmp_file_path)

    logging.debug(f"Invalid file input response: {response_interpret.json()}")

    assert response_interpret.status_code == 422
    assert 'detail' in response_interpret.json()

    logging.debug(f"Invalid file input response: {response.json()}")

    assert response.status_code == 422
    assert 'detail' in response.json()
