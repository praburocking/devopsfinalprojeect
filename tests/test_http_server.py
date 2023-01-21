import sys
sys.path.insert(0, '../httpserver')

from httpserver import app
from fastapi.testclient import TestClient
import pytest
from six import PY2

@pytest.fixture
def mocker_file_open(mocker):
    # Read a mocked /etc/release file
    mocked_etc_release_data = mocker.mock_open(read_data=" Oracle Solaris 12.0")
    builtin_open = "__builtin__.open" if PY2 else "builtins.open"
    mocker.patch(builtin_open, mocked_etc_release_data)


client = TestClient(app)

def test_read_message(mocker_file_open):
    response = client.get("/message")
    output_res=["2022-10-01T06:35:01.200Z 1 MSG_1 to compse140.i",
                "2022-10-01T06:35:01.373Z 2 MSG_1 to compse140.o"]
    assert response.status_code == 200
    assert response.text=="\n".join(output_res)

def test_update_state():
    response = client.put("/state")
    assert response.status_code == 200
    assert response.text=="updated"

def test_get_state():
    response = client.get("/state")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_get_log():
    response = client.get("/run-log")
    output_res=["2020-11-01T06:35:01.373Z: INIT",
                "2020-11-01T06.35:01.380Z: RUNNING",
                "2020-11-01T06:40:01.373Z: PAUSED"
                "2020-11-01T06:40:01.373Z: RUNNING"]
    assert response.status_code == 200
    assert response.text=="\n".join(output_res)