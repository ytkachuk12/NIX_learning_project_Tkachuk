"""Methods of interacting with the DB:
insert, ....."""
from datetime import date
from typing import Optional, List

import bcrypt

from .models import *


def hashing_pass(password: str):
    # password = user input
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def checking_nickname(nickname: str) -> bool:
    """check the presence of user's nickname in DB
    :return bool"""
    if Users.query.filter_by(nickname=nickname).first():
        return True
    return False


def checking_email(email: str) -> bool:
    """check the presence of user's email in DB
    :return bool"""
    if Users.query.filter_by(email=email).first():
        return True
    else:
        return False


def checking_pass(nickname: str, password: str) -> bool:
    """check the presence of user's password in DB
    :return bool"""
    check_user = Users.query.filter_by(nickname=nickname).first()
    if check_user.hash_and_salt == hashing_pass(password):
        return True
    else:
        return False


def register_user(nickname: str, password: str, email: str, first_name: str,
                  surname: str, age: Optional[int] = None):
    # create and add user to base
    if checking_nickname(nickname):
        raise ValueError("User with the same nickname already exist")
    elif checking_email(email):
        raise ValueError("User with the same email already exist")
    else:
        # create hash_pass
        hash_and_salt = hashing_pass(password)
        user = Users(nickname=nickname, hash_and_salt=hash_and_salt, email=email,
                     first_name=first_name, surname=surname, age=age)
        try:
            db.session.add(user)
        except Exception as e:
            print(e)
            db.session.rollback()
        else:
            db.session.commit()
    return Users.query.filter_by(nickname=nickname).first().user_id


# def login(nickname: str, password: str):
#     if not checking_nickname(nickname):
#         raise ValueError("Incorrect nickname")
#     elif not checking_pass(nickname, password):
#         raise ValueError("Incorrect password")
#     else:
#         return "Successfully logged in"


def rate_film(film_id: int, user_rate: int):
    film = Films.query.filter_by(film_id=film_id).first_or_404(description="No film with this id")
    # count the sum of all scores
    temp = film.rating * film.number_of_rated_users
    # not shure
    # count the new average score
    # update film data
    film.rating = (temp + user_rate) / (film.number_of_rated_users + 1)
    film.number_of_rated_users += 1

    db.session.commit()


def insert_genre(genre_name: str):
    """ Add film's genre in Genres db table
    """
    genre = Genres(genre_name=genre_name)
    try:
        db.session.add(genre)
    except Exception as e:
        print(e)
        db.session.rollback()
    else:
        db.session.commit()


def insert_director(director_name: str):
    """ Add film's director in Directors db table
    """
    director = Directors(genre_name=director_name)
    try:
        db.session.add(director)
    except Exception as e:
        print(e)
        db.session.rollback()
    else:
        db.session.commit()


def insert_film_genre(new_film: Films, genre_names: List[str]):
    """Add links to the film_genre table.
    """
    for genre_name in genre_names:
        # looking for genre in genres table
        new_genre = Genres.query.filter_by(genre_name=genre_name).first()
        if not new_genre:
            insert_genre(genre_name)
        new_genre = Genres.query.filter_by(genre_name=genre_name).first()
        # add genre_id to associated table
        new_film.film_genre.append(new_genre)

    db.session.commit()


def insert_film_director(new_film: Films, director_names: List[str]):
    """Add links to the film_director table.
    """
    for director_name in director_names:
        # looking for director in genres table
        new_director = Directors.query.filter_by(director_name=director_name).first()
        if not new_director:
            insert_director(director_name)
        new_director = Directors.query.filter_by(director_name=director_name).first()
        # add genre_id to associated table
        new_film.film_director.append(new_director)

    db.session.commit()


def insert_film(user_id, film_name: str, description: str, release_date: date, poster_link: str,
                genre_names: List[str], director_names: List[str]):
    if Films.query.filter_by(film_name=film_name, release_date=release_date).first():
        return 'Film with the same name and year already exist'
    else:
        new_film = Films(user_id_added_film=user_id, film_name=film_name,
                         description=description, release_date=release_date,
                         poster_link=poster_link)
        try:
            db.session.add(new_film)
        except Exception as e:
            print(e)
            db.session.rollback()
        else:
            db.session.commit()

    insert_film_genre(new_film, genre_names)
    insert_film_director(new_film, director_names)


