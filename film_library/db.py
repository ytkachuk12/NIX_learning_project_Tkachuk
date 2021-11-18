"""Methods of interacting with the DB:
insert, ....."""
from datetime import date, datetime
from typing import Optional, List

from flask import abort
import bcrypt

from film_library.models import *


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


def checking_pass(nickname: str, password: str) -> Optional[int]:
    """check the presence of user's password in DB
    :return user: Users or None"""
    check_user = Users.query.filter_by(nickname=nickname).first()
    if bcrypt.checkpw(password.encode(), check_user.hash_and_salt):
        return check_user
    else:
        return None


def register_user(nickname: str, password: str, email: str, first_name: Optional[str] = None,
                  surname: Optional[str] = None, age: Optional[int] = None):
    # create and add user to base
    if checking_nickname(nickname):
        return abort(400, f"User {nickname} is already registered.")
    elif checking_email(email):
        return abort(400, f"User {email} is already registered.")
    else:
        # create hash_pass
        hash_and_salt = hashing_pass(password)
        user = Users(nickname=nickname, hash_and_salt=hash_and_salt, email=email,
                     first_name=first_name, surname=surname, age=age)
        try:
            db.session.add(user)
        except Exception as e:
            db.session.rollback()
            return abort(500, e)
        else:
            db.session.commit()
    return {"user_id": Users.query.filter_by(nickname=nickname).first().id}


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
    director = Directors(director_name=director_name)
    try:
        db.session.add(director)
    except Exception as e:
        print(e)
        db.session.rollback()
    else:
        db.session.commit()


def insert_film_genre(new_film: Films, genre_names: list[str]):
    """Add links to the film_genre table.
    """
    for genre_name in genre_names:
        # looking for genre in genres table
        new_genre = Genres.query.filter_by(genre_name=genre_name).first()
        if not new_genre:
            insert_genre(genre_name)
        new_genre = Genres.query.filter_by(genre_name=genre_name).first()
        # add genre_id to associated table
        new_film.add_film_genre.append(new_genre)

    db.session.commit()


def insert_film_director(new_film: Films, director_names: list[str]):
    """Add links to the film_director table."""
    for director_name in director_names:
        # looking for director in genres table
        new_director = Directors.query.filter_by(director_name=director_name).first()

        if not new_director:
            insert_director(director_name)
        new_director = Directors.query.filter_by(director_name=director_name).first()
        # add genre_id to associated table
        new_film.add_film_director.append(new_director)

    db.session.commit()


def insert_film(user_id, film_name: str, description: Optional[str], release_date: date,
                poster_link: Optional[str], genre_names: Optional[list[str]],
                director_names: Optional[List[str]]):

    film = Films.query.filter_by(film_name=film_name, release_date=release_date).first()
    if film:
        return abort(400, f'Film with {film_name} name and same release year already exist')
    else:
        new_film = Films(user_id_added_film=user_id, film_name=film_name,
                         description=description, release_date=release_date,
                         poster_link=poster_link)
        try:
            db.session.add(new_film)
        except Exception as e:
            print(e)
            db.session.rollback()
            return False
        else:
            db.session.commit()
    if genre_names:
        insert_film_genre(new_film, genre_names)
    if director_names:
        insert_film_director(new_film, director_names)
    return new_film


def edit_film(film_id: int, film_name: Optional[str], description: Optional[str], release_date: Optional[str],
              poster_link: Optional[str], director_names: Optional[list], genre_names: Optional[list]):
    film = Films.query.filter_by(film_id=film_id).first()
    if film:
        if film_name:
            film.film_name = film_name
        if description:
            film.description = description
        if release_date:
            film.release_date = release_date
        if poster_link:
            film.poster_link = poster_link
        if director_names:
            insert_film_director(film, director_names)
        if genre_names:
            insert_film_genre(film, genre_names)

    db.session.commit()
    return Films.query.filter_by(film_id=film_id).first()


def delete_film(film_id: int):
    """Delete the film
    need add delete from film-director"""
    if Films.query.filter_by(film_id=film_id).first():
        try:
            Films.query.filter_by(film_id=film_id).delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return abort(500)
        else:
            db.session.commit()
        return film_id
    return abort(400, f'No film with id {film_id}')


if __name__ == '__main__':
    edit_film(1, "lost")