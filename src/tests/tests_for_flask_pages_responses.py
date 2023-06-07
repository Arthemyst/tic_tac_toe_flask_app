import pytest
from app import app
from flask import session
from flask_login import current_user


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        with app.app_context():
            yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_register(client):
    response = client.post("/register", data={"username": "test_user", "password": "test_password"})
    assert response.status_code == 200


def test_login(client):
    response = client.post("/login", data={"username": "test_user", "password": "test_password"})
    assert response.status_code == 302
    assert session["username"] == "test_user"
    assert session["check_if_game_is_on"] == False
    assert session["login_datetime"] is not None


def test_logout(client):
    client.post("/login", data={"username": "test_user", "password": "test_password"})
    response = client.get("/logout")
    with client.session_transaction() as session:
        assert response.status_code == 200 or response.status_code == 302

    assert not current_user.is_authenticated


def test_game_page(client):
    client.post("/login", data={"username": "test_user", "password": "test_password"})
    response = client.get("/game")
    with client.session_transaction() as session:
        assert response.status_code == 200 or response.status_code == 302
        assert b"play move" in response.data
        assert session.get("username") == "test_user"


def test_profile_page(client):
    client.post("/login", data={"username": "test_user", "password": "test_password"})
    response = client.get("/profile")
    with client.session_transaction() as session:
        assert response.status_code == 200 or response.status_code == 302
        assert session.get("username") == "test_user"


def test_player_stats_page(client):
    client.post("/login", data={"username": "test_user", "password": "test_password"})
    response = client.get("/player_stats")
    with client.session_transaction() as session:
        assert response.status_code == 200
        assert b"Statistics for" in response.data
        assert session.get("username") == "test_user"




if __name__ == "__main__":
    pytest.main()
