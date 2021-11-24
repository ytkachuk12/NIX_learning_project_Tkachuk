import pytest

from film_library import app
from tests.data_for_tests import FILMS, USERS, set_test_db
from film_library.models import Films

# set test data
set_test_db()


@pytest.fixture
def client():
    """create testing application """
    with app.test_client() as client:
        yield client


@pytest.fixture
def login_user(client):
    user = client.post("/login", data={"nickname": USERS[0][0], "password": USERS[0][1]})
    return user


@pytest.fixture
def login_user_not_admin(client):
    user = client.post("/login", data={"nickname": USERS[2][0], "password": USERS[2][1]})
    return user


def test_register(client):
    """test '/register' route, method = post"""
    # registration new user
    response = client.post("/register", data={
        "nickname": "petr1", "password": "password", "email": "petemail"})
    assert response.status_code == 200
    # case of not unique username or password
    response = client.post("/register", data={
        "nickname": USERS[0][0], "password": "password", "email": "email1@gmail.com"
    })
    assert response.status_code == 404
    # to small nickname
    response = client.post("/register", data={
        "nickname": "pet", "password": "password", "email": "petemail"
    })
    assert response.status_code == 404


def test_login(client):
    """test '/login' route, method = post"""
    # test successes login
    response = client.post("/login", data={"nickname": USERS[0][0], "password": USERS[0][1]})
    assert response.status_code == 200
    # test nickname not correct
    response = client.post("/login", data={"nickname": "yurii1", "password": "password"})
    assert response.status_code == 404
    # test password not correct
    response = client.post("/login", data={"nickname": "yurii", "password": "password1"})
    assert response.status_code == 404


def test_logout(client, login_user):
    """test '/logout' route, method = post"""
    # test successes logout
    response = client.get("/logout")
    assert response.status_code == 200
    # test no authorization
    response = client.get("/logout")
    assert response.status_code == 401


def test_insert_film(client, login_user):
    """test insert film, '/films' route, method = post"""
    # test successes inserting
    response = client.post("/films", data={
        "film_name": "new_film", "description": "new description", "release_date": "1998-02-01",
        "poster_link": "new_poster", "genre_names": "new_genre", "director_names": "new_dir"
    })
    assert response.status_code == 201
    # test inserting existing films returns code 404
    response = client.post("/films", data={
        "film_name": "new_film", "description": "new description", "release_date": "1998-02-01",
        "poster_link": "new_poster", "genre_names": "new_genre", "director_names": "new_dir"
    })
    assert response.status_code == 404


def test_update_film(client, login_user_not_admin):
    """test update film, '/films' route, method = put"""
    # test successes update
    response = client.put("/films", data={
        "film_id": 3, "film_name": "upd big bang", "description": "apd some description",
        "release_date": "2003-12-11", "poster_link": "upd_link3",
        "genre_names": "upd_new_genre", "director_names": "upd_new_dir"
    })
    assert response.status_code == 201
    # test user did not creat current film or user is not admin
    response = client.put("/films", data={
        "film_id": 1
    })
    assert response.status_code == 404


def test_delete_film(client, login_user_not_admin):
    """test delete film, '/films' route, method = delete"""
    # test successes delete
    response = client.delete("/films", data={
        "id": 3
    })
    assert response.status_code == 200
    # test user did not creat current film or user is not admin
    response = client.delete("/films", data={
        "id": 2
    })
    assert response.status_code == 404
    # test no film in DB
    response = client.delete("/films", data={
        "id": 111
    })
    assert response.status_code == 404


def test_search_film(client):
    """test search film, '/films' route, method = get"""
    # search by film mask
    response = client.get("/films?film_mask=die")
    temp = response.json["films"]
    assert len(temp) == 1
    assert len(temp[0]) == len(FILMS[1]) + 3
    assert temp[0]["film_name"] == FILMS[1][1]

    # search by film mask, release date, genre
    response = client.get("/films?film_mask=&genre_names=thriller&release_range=1990-01-01,2015-01-01")
    temp = response.json["films"]
    assert len(temp) == 2


def test_delete_director(client, login_user):
    """test delete director, '/directors' route, method = delete"""
    # successes delete by admin
    response = client.delete("/directors", data={"director_name": "dir1"})
    assert response.status_code == 200


def test_rate_film(client):
    """test rate film, '/film/rate' route, method = get"""
    # successes rate film
    response = client.get("/film/rate?film_id=1&user_rate=5")
    temp = response.json["films"]
    assert temp["rating"] == Films.query.filter_by(film_id=1).first().rating

    response = client.get("/film/rate?film_id=1&user_rate=4")
    temp = response.json["films"]
    assert temp["rating"] == Films.query.filter_by(film_id=1).first().rating
