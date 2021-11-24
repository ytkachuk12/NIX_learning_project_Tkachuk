import pytest

from film_library import app


@pytest.fixture
def client():
    """create testing application """
    with app.test_client() as client:
        yield client


@pytest.fixture
def login_user(client):
    user = client.post("/login", data={"nickname": "yurii", "password": "password"})
    return user


@pytest.fixture
def login_user_not_admin(client):
    user = client.post("/login", data={"nickname": "ivan", "password": "passpass"})
    return user


def test_register(client):
    """test '/register' route, method = post"""
    # registration new user
    response = client.post("/register", data={
        "nickname": "petr1", "password": "password", "email": "petemail"})
    assert response.status_code == 200
    # case of not unique username or password
    response = client.post("/register", data={
        "nickname": "yurii", "password": "password", "email": "email1@gmail.com"
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
    response = client.post("/login", data={"nickname": "yurii", "password": "password"})
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
    assert response.json == {"films": [
        {
            "film_id": 2,
            "user_id": 2,
            "film_name": "die hard",
            "description": "description some",
            "rating": 0.0,
            "number_of_rated_users": 0,
            "release_date": "1995.10.10",
            "poster_link": "link2",
            "director_names": "['dir3']",
            "genre_names": "['thriller', 'detective']"
        }]}
    # search by film mask, release date, genre
    response = client.get("/films?film_mask=&genre_names=thriller&release_range=1990-01-01,2015-01-01")
    assert response.json == {"films": [
        {
            "film_id": 1,
            "user_id": 1,
            "film_name": "matrix",
            "description": "some description",
            "rating": 0.0,
            "number_of_rated_users": 0,
            "release_date": "2003.12.12",
            "poster_link": "link1",
            "director_names": "['dir1', 'dir2']",
            "genre_names": "['thriller', 'fantastic']"
        },
        {
            "film_id": 2,
            "user_id": 2,
            "film_name": "die hard",
            "description": "description some",
            "rating": 0.0,
            "number_of_rated_users": 0,
            "release_date": "1995.10.10",
            "poster_link": "link2",
            "director_names": "['dir3']",
            "genre_names": "['thriller', 'detective']"
        }]}


def test_delete_director(client, login_user):
    """test delete director, '/directors' route, method = delete"""
    # successes delete by admin
    response = client.delete("/directors", data={"director_name": "dir1"})
    assert response.status_code == 200


def test_rate_film(client):
    """test rate film, '/film/rate' route, method = get"""
    # successes rate film
    response = client.get("/film/rate?film_id=1&user_rate=5")
    assert response.json == {"films": {
        "film_id": 1,
        "user_id": 1,
        "film_name": "matrix",
        "description": "some description",
        "rating": 5,
        "number_of_rated_users": 1,
        "release_date": "2003.12.12",
        "poster_link": "link1",
        "director_names": "['dir2']",
        "genre_names": "['thriller', 'fantastic']"
    }
    }
    response = client.get("/film/rate?film_id=1&user_rate=4")
    assert response.json == {"films": {
        "film_id": 1,
        "user_id": 1,
        "film_name": "matrix",
        "description": "some description",
        "rating": 4.5,
        "number_of_rated_users": 2,
        "release_date": "2003.12.12",
        "poster_link": "link1",
        "director_names": "['dir2']",
        "genre_names": "['thriller', 'fantastic']"
    }}
