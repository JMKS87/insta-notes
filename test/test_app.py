import shutil
import tempfile
import time
from unittest.mock import patch

from bs4 import BeautifulSoup

from app.main import app
import pytest


@pytest.fixture
def temp_data():
    with tempfile.TemporaryDirectory() as tmpdirname:
        with patch("app.main.DATA_DIR", tmpdirname):
            yield


@pytest.fixture
def client(temp_data):
    with app.test_client() as client:
        yield client


def test_main_page(client):
    # given

    # when
    rv = client.get("/")

    # then
    assert rv.status_code == 200
    soup = BeautifulSoup(rv.data)
    form_element = soup.find("form")
    assert not form_element


def test_empty_note(client):
    # given

    # when
    rv = client.get("/my_note")

    # then
    assert rv.status_code == 200
    soup = BeautifulSoup(rv.data)
    form_element = soup.find("form")
    assert form_element
    assert form_element.find("textarea").text == ""


def test_post_simple_note(client):
    # given

    # when
    rv = client.post("/my_note", data={"content": "abc"})

    # then
    assert rv.status_code == 200
    soup = BeautifulSoup(rv.data)
    form_element = soup.find("form")
    assert form_element.find("textarea").text == "abc"


def test_retrieve_note(client):
    # given
    rv = client.post("/my_note", data={"content": "abc"})

    # when
    rv = client.get("/my_note")

    # then
    assert rv.status_code == 200
    soup = BeautifulSoup(rv.data)
    form_element = soup.find("form")
    assert form_element.find("textarea").text == "abc"


def test_post_note_with_password(client):
    # given

    # when
    rv = client.post("/my_note", data={"content": "abc", "password": "def"})

    # then
    assert rv.status_code == 200
    soup = BeautifulSoup(rv.data)
    form_element = soup.find("form")
    assert form_element.find("textarea").text == "abc"
    assert form_element.find("input", {"name": "password"}).text == ""


def test_post_note_with_changes(client):
    # given
    rv = client.post("/my_note", data={"content": "abc", "password": ""})

    # when
    rv = client.post("/my_note", data={"content": "ghi", "password": ""})

    # then
    assert rv.status_code == 200
    soup = BeautifulSoup(rv.data)
    form_element = soup.find("form")
    assert form_element.find("textarea").text == "ghi"


def test_get_note_with_password_asks_for_password(client):
    # given
    rv = client.post("/my_note", data={"content": "abc", "password": "def"})

    # when
    rv = client.get("/my_note")

    # then
    assert rv.status_code == 200
    soup = BeautifulSoup(rv.data)
    form_element = soup.find("form")
    assert not form_element.find("textarea")
    assert soup.find("div", {"id": "message"}).text == "Note is password-protected"


def test_retrieve_note_with_password(client):
    # given
    rv = client.post("/my_note", data={"content": "abc", "password": "def"})

    # when
    rv = client.post("/my_note", data={"password": "def"})

    # then
    assert rv.status_code == 200
    soup = BeautifulSoup(rv.data)
    form_element = soup.find("form")
    assert form_element.find("textarea").text == "abc"


def test_wrong_password(client):
    # given
    rv = client.post("/my_note", data={"content": "abc", "password": "def"})

    # when
    rv = client.post("/my_note", data={"password": "abc"})

    # then
    assert rv.status_code == 403


def test_with_ttl(client):
    # given
    rv = client.post("/my_note", data={"content": "abc", "ttl": "500"})

    # when
    rv = client.get("/my_note")

    # then
    assert rv.status_code == 200
    soup = BeautifulSoup(rv.data)
    form_element = soup.find("form")
    retrieved_ttl = int(form_element.find("input", {"name": "ttl"}).get("value"))
    assert 500 > retrieved_ttl > 490


def test_ttl_reached(client):
    # given
    rv = client.post("/my_note", data={"content": "abc", "ttl": "1"})

    # when
    rv1 = client.get("/my_note")
    time.sleep(1)
    rv2 = client.get("/my_note")

    # then
    assert rv1.status_code == 200
    assert rv2.status_code == 200
    assert b"abc" in rv1.data
    assert not b"abc" in rv2.data


def test_ttl_minus(client):
    # given
    rv = client.post("/my_note", data={"content": "abc", "ttl": "-1"})

    # when
    rv = client.get("/my_note")

    # then
    soup = BeautifulSoup(rv.data)
    form_element = soup.find("form")
    assert form_element
    assert form_element.find("textarea").text == ""


def test_404(client):
    # given

    # when
    rv = client.get("/my_note/sth")

    # then
    assert rv.status_code == 404
