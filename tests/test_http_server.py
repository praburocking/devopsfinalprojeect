import sys
sys.path.insert(0, '../httpserver')

from httpserver import app
from fastapi.testclient import TestClient
import pytest

# Mocking the file open for /message
@pytest.fixture
def mocker_message_file_open(mocker):
    # Read a mocked file
   pass


# Mocking the file "/usr/data/run_log_file.txt" for /run-log, /state
@pytest.fixture
def mocker_run_log_file_open(mocker):
    
    # Read a mocked file
    output_res=["2020-11-01T06:35:01.373Z: INIT",
                "2020-11-01T06:40:01.373Z: RUNNING"]
    mocked_run_log_file= mocker.mock_open(read_data="\n".join(output_res))
    builtin_open = "builtins.open"
    mocker.patch(builtin_open, mocked_run_log_file)


client = TestClient(app)

def test_read_message(mocker):
    output_res=["2023-01-22 00:18:50.567344 1 MSG_1 to compse140.o",
                "2023-01-22 00:18:50.567431 2 MSG_1 to compse140.i",
                "2023-01-22 00:18:50.567512 3 MSG_2 to compse140.o",
                "2023-01-22 00:18:50.567581 4 MSG_2 to compse140.i",
                "2023-01-22 00:18:51.670902 5 MSG_3 to compse140.o",
                "2023-01-22 00:18:51.671679 6 MSG_3 to compse140.i"]
    mocked_etc_release_data = mocker.mock_open(read_data="\n".join(output_res))
    builtin_open = "builtins.open"
    mocker.patch(builtin_open, mocked_etc_release_data)
    response = client.get("/message")
    assert response.status_code == 200
    assert response.text=="\n".join(output_res)



def test_simple_update_state():
    response = client.put("/state",data=b"PAUSED")
    assert response.status_code == 200
    assert response.text=="state updated"
    
def test_update_same_state():
    response = client.put("/state",data=b"PAUSED")
    response = client.put("/state",data=b"PAUSED")
    assert response.status_code == 200
    assert response.text=="state not updated"

def test_update_undefined_state():
    response = client.put("/state",data=b"random_text")
    assert response.status_code == 400
    assert response.text=="Invalid state. Allowed state ['INIT', 'PAUSED', 'RUNNING', 'SHUTDOWN']"

def test_get_state(mocker_run_log_file_open):
    response = client.get("/state")
    assert response.status_code == 200
    assert response.text == "RUNNING"

def test_get_log(mocker_run_log_file_open):
    response = client.get("/run-log")
    output_res=["2020-11-01T06:35:01.373Z: INIT",
                "2020-11-01T06:40:01.373Z: RUNNING"]
    assert response.status_code == 200
    assert response.text=="\n".join(output_res)