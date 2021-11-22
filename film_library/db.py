# """Methods of interacting with the DB:
# insert, ....."""
# from datetime import date, datetime
# from typing import Optional, List
#
# from flask import abort
# import bcrypt
#
# from film_library.models import *
#
#
# def hashing_pass(password: str) -> str:
#     """Hash password with bcrypt module
#     :return hash"""
#     # password = user input, and generate salt
#     return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
#
#
# def checking_nickname(nickname: str) -> bool:
#     """Check the presence of user's nickname in DB
#     :return bool"""
#     if Users.query.filter_by(nickname=nickname).first():
#         return True
#     return False
#
#
# def checking_email(email: str) -> bool:
#     """check the presence of user's email in DB
#     :return bool"""
#     if Users.query.filter_by(email=email).first():
#         return True
#     else:
#         return False
#
#
# def checking_pass(nickname: str, password: str) -> Optional[int]:
#     """check the presence of user's password in DB
#     :return user: Users or None"""
#     check_user = Users.query.filter_by(nickname=nickname).first()
#     if bcrypt.checkpw(password.encode(), check_user.hash_and_salt):
#         return check_user
#     else:
#         return None
#
#
# def convert_str_to_date(input_date):
#     # convert date
#     try:
#         return datetime.strptime(input_date, '%Y-%m-%d').date()
#     except ValueError:
#         return abort(400, "Wrong date format")
#
#
# def get_user_creator(film_id: int) -> Optional[int]:
#     return Films.query.filter_by(film_id=film_id).first_or_404(
#         description="No film with this id").user_id_added_film
#
#
# def register_user(nickname: str, password: str, email: str, first_name: Optional[str] = None,
#                   surname: Optional[str] = None, age: Optional[int] = None):
#     # create and add user to base
#     if checking_nickname(nickname):
#         return abort(400, f"User {nickname} is already registered.")
#     elif checking_email(email):
#         return abort(400, f"User {email} is already registered.")
#     else:
#         # create hash_pass
#         hash_and_salt = hashing_pass(password)
#         user = Users(nickname=nickname, hash_and_salt=hash_and_salt, email=email,
#                      first_name=first_name, surname=surname, age=age)
#         try:
#             db.session.add(user)
#         except Exception as e:
#             db.session.rollback()
#             return abort(500, e)
#         else:
#             db.session.commit()
#     return user.id
#
#
# def rate_film(film_id: int, user_rate: int):
#     film = Films.query.filter_by(film_id=film_id).first_or_404(description="No film with this id")
#     # count the sum of all scores
#     temp = film.rating * film.number_of_rated_users
#     # count the new average score
#     # update film data
#     film.rating = (temp + user_rate) / (film.number_of_rated_users + 1)
#     film.number_of_rated_users += 1
#
#     db.session.commit()
#
#     return convert_to_dict(film)
#
#
# def get_film(film_id):
#     film = Films.query.select_from(Films) \
#         .join(film_genre) \
#         .join(film_director) \
#         .join(Genres) \
#         .join(Directors) \
#         .filter(
#         (Films.film_id == film_id)
#     ).add_columns(
#         Films.film_id,
#         Films.user_id_added_film,
#         Films.film_name,
#         Films.description,
#         Films.rating,
#         Films.number_of_rated_users,
#         Films.release_date,
#         Films.poster_link,
#         Directors.director_name,
#         Genres.genre_name,
#     ).first()
#     return film
#
#
# def get_genres(film_id):
#     all_genres = Films.query.select_from(Films).join(film_genre).join(Genres).filter(
#         (Films.film_id == film_id) &
#         (Films.film_id == film_genre.c.films_film_id) &
#         (film_genre.c.genres_genre_id == Genres.genre_id)
#     ).add_columns(Genres.genre_name).all()
#
#     return all_genres
#
#
# def get_directors(film_id):
#     all_directors = Films.query.select_from(Films).join(film_director).join(Directors).filter(
#         (Films.film_id == film_id) &
#         (Films.film_id == film_director.c.films_film_id) &
#         (film_director.c.directors_director_id == Directors.director_id)
#     ).add_columns(Directors.director_name).all()
#
#     return all_directors
#
#
# def insert_genre(genre_name: str):
#     """ Add film's genre in Genres db table
#     """
#     genre = Genres(genre_name=genre_name)
#     try:
#         db.session.add(genre)
#     except Exception as e:
#         print(e)
#         db.session.rollback()
#     else:
#         db.session.commit()
#
#
# def insert_director(director_name: str):
#     """ Add film's director in Directors db table
#     """
#     director = Directors(director_name=director_name)
#     try:
#         db.session.add(director)
#     except Exception as e:
#         print(e)
#         db.session.rollback()
#     else:
#         db.session.commit()
#
#
# def insert_film_genre(new_film: Films, genre_names: list[str]):
#     """Add links to the film_genre table.
#     """
#     for genre_name in genre_names:
#         # looking for genre in genres table
#         new_genre = Genres.query.filter_by(genre_name=genre_name).first()
#         if not new_genre:
#             insert_genre(genre_name)
#         new_genre = Genres.query.filter_by(genre_name=genre_name).first()
#         # add genre_id to associated table
#         new_film.add_film_genre.append(new_genre)
#
#     db.session.commit()
#
#
# def insert_film_director(new_film: Films, director_names: list[str]):
#     """Add links to the film_director table."""
#     for director_name in director_names:
#         # looking for director in genres table
#         new_director = Directors.query.filter_by(director_name=director_name).first()
#
#         if not new_director:
#             insert_director(director_name)
#         new_director = Directors.query.filter_by(director_name=director_name).first()
#         # add genre_id to associated table
#         new_film.add_film_director.append(new_director)
#
#     db.session.commit()
#
#
# def check_directors(director_names: Optional[List[str]]):
#     # check directors
#     if not director_names:
#         director_names = []
#         directors = Directors.query.add_columns(Directors.director_name).all()
#         for director in directors:
#             director_names.append(director[1])
#     return director_names
#
#
# def check_genres(genre_names: Optional[List[str]]):
#     # check genres
#     if not genre_names:
#         genre_names = []
#         genres = Genres.query.add_columns(Genres.genre_name).all()
#         for genre in genres:
#             genre_names.append(genre[1])
#     return genre_names
#
#
# def check_sorting(sorting):
#     if sorting == 'rating':
#         return Films.rating.desc()
#     elif sorting == 'release_date':
#         return Films.release_date.desc()
#     return None
#
#
# def convert_release_range(release_range):
#     if not release_range:
#         release_range = [convert_str_to_date("1900-01-01"), date.today()]
#     else:
#         release_range = [convert_str_to_date(release_range[0]),
#                          convert_str_to_date(release_range[1])]
#     return release_range
#
#
# def search_directors():
#     pass
#
#
# def search_films(film_mask: str, release_range: Optional[List[str]],
#                  director_names: Optional[List[str]], genre_names: Optional[List[str]],
#                  pagination: int, page_number: int, sorting: str):
#     # check and set sorting
#     sorting = check_sorting(sorting)
#
#     # check and set release range
#     release_range = convert_release_range(release_range)
#
#     # check and set directors
#     director_names = check_directors(director_names)
#
#     # check and set genres
#     genre_names = check_genres(genre_names)
#
#     all_films = Films.query.select_from(Films) \
#         .join(film_genre) \
#         .join(film_director) \
#         .join(Genres) \
#         .join(Directors) \
#         .filter(
#         (Films.film_name.ilike("%" + film_mask + "%")) &
#         (Films.film_id == film_genre.c.films_film_id) &
#         (film_genre.c.genres_genre_id == Genres.genre_id) &
#         (Genres.genre_name.in_(genre_names)) &
#         (film_director.c.directors_director_id == Directors.director_id) &
#         (Directors.director_name.in_(director_names)) &
#         (Films.release_date.between(release_range[0], release_range[1]))) \
#         .add_columns(
#         Films.film_id,
#         Films.user_id_added_film,
#         Films.film_name,
#         Films.description,
#         Films.rating,
#         Films.number_of_rated_users,
#         Films.release_date,
#         Films.poster_link
#     ).order_by(sorting).paginate(per_page=pagination, page=page_number)
#
#     list_of_films = []
#     for i in all_films.items:
#         directors = get_directors(i.film_id)
#         genres = get_genres(i.film_id)
#         list_of_films.append(convert_to_dict(i, directors, genres))
#
#     return list_of_films
#
#
# def insert_film(user_id, film_name: str, description: Optional[str], release_date: date,
#                 poster_link: Optional[str], genre_names: Optional[list[str]],
#                 director_names: Optional[List[str]]):
#     film = Films.query.filter_by(film_name=film_name, release_date=release_date).first()
#     if film:
#         return abort(400, f'Film with {film_name} name and same release year already exist')
#     else:
#         new_film = Films(user_id_added_film=user_id, film_name=film_name,
#                          description=description, release_date=release_date,
#                          poster_link=poster_link)
#         try:
#             db.session.add(new_film)
#         except Exception as e:
#             print(e)
#             db.session.rollback()
#             return False
#         else:
#             db.session.commit()
#     if genre_names:
#         insert_film_genre(new_film, genre_names)
#     if director_names:
#         insert_film_director(new_film, director_names)
#
#     film = get_film(new_film.film_id)
#     directors = get_directors(new_film.film_id)
#     genres = get_genres(new_film.film_id)
#
#     return convert_to_dict(film, directors, genres)
#
#
# def edit_film(film_id: int, film_name: Optional[str], description: Optional[str],
#               release_date: Optional[str], poster_link: Optional[str],
#               director_names: Optional[list], genre_names: Optional[list]):
#
#     film = Films.query.filter_by(film_id=film_id).first_or_404(description="No film with this id")
#
#     if film_name:
#         film.film_name = film_name
#     if description:
#         film.description = description
#     if release_date:
#         film.release_date = release_date
#     if poster_link:
#         film.poster_link = poster_link
#     if director_names:
#         insert_film_director(film, director_names)
#     if genre_names:
#         insert_film_genre(film, genre_names)
#
#     db.session.commit()
#
#     edited_film = Films.query.filter_by(film_id=film_id).first()
#     directors = get_directors(edited_film.film_id)
#     genres = get_genres(edited_film.film_id)
#
#     return convert_to_dict(edited_film, directors, genres)
#
#
# def delete_film(film_id: int):
#     """Delete the film
#     need add delete from film-director"""
#     if Films.query.filter_by(film_id=film_id).first():
#         try:
#             # film = db.session.query(Films).filter(Films.film_id == film_id)
#             # db.session.delete(film)
#             Films.query.filter_by(film_id=film_id).delete()
#         except Exception as e:
#             db.session.rollback()
#             print(e)
#             return abort(500)
#         else:
#             db.session.commit()
#         return film_id
#     return abort(400, f'No film with id {film_id}')
#
#
# def convert_to_dict(film, directors, genres):
#     """ Create dict from attributes to adopt it for json. """
#     release_date = datetime.strftime(film.release_date, "%Y.%m.%d")
#     film = {"film_id": film.film_id, "user_id": film.user_id_added_film,
#             "film_name": film.film_name, "description": film.description,
#             "rating": film.rating, "number_of_rated_users": film.number_of_rated_users,
#             "release_date": release_date, "poster_link": film.poster_link,
#             "director_names": [], "genre_names": []}
#
#     if directors:
#         for i in directors:
#             film["director_names"].append(i.director_name)
#     if genres:
#         for i in genres:
#             film["genre_names"].append(i.genre_name)
#
#     return film
#
#
# if __name__ == '__main__':
#     print(get_directors(1))
