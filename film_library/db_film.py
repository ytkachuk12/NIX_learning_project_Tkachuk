"""Methods of interacting with the DB:
contain interaction with film's side db"""
from datetime import date, datetime
from typing import Optional, List

from flask import abort

from film_library.models import db, Films, film_genre, film_director, Genres, Directors


def get_user_creator(film_id: int) -> Optional[int]:
    """Search user, who create film by film_id in db
        :returns user id if exist, else return None"""
    user_id = Films.query.filter_by(film_id=film_id).first_or_404(
        description="No film with this id")
    if user_id:
        return user_id.user_id_added_film
    return None


def convert_str_to_date(input_date: str):
    """Convert string to Date(class DateTime)
        :return date: Date
        :raise flask abort if not possible to convert, code 404"""
    try:
        return datetime.strptime(input_date, '%Y-%m-%d').date()
    except ValueError:
        return abort(404, "Wrong date format or not correct input")


def rate_film(film_id: int, user_rate: int) -> dict:
    """Take the film rating from user, calculates the average of users ratings
    Increase the number of voters by 1
    Update fields: rating and number_of_rated_users for the current film
        :returns dict of all films data
        :raise abort if no film find id DB with current id"""
    film = Films.query.filter_by(film_id=film_id).first_or_404(description="No film with this id")
    # count the sum of all scores
    temp = film.rating * film.number_of_rated_users
    # count the new average score
    # update film data
    film.rating = (temp + user_rate) / (film.number_of_rated_users + 1)
    film.number_of_rated_users += 1

    db.session.commit()

    film = Films.query.filter_by(film_id=film_id).first()
    directors = get_directors(film_id)
    genres = get_genres(film_id)
    return convert_to_dict(film, directors, genres)


def get_genres(film_id: int):
    """Get genres of current film by id
        :returns all_genres: Genres"""
    all_genres = Films.query.select_from(Films).join(film_genre).join(Genres).filter(
        (Films.film_id == film_id) &
        (Films.film_id == film_genre.c.films_film_id) &
        (film_genre.c.genres_genre_id == Genres.genre_id)
    ).add_columns(Genres.genre_name).all()

    return all_genres


def get_directors(film_id: int):
    """Get directors of current film by id
        :returns all_directors: Directors"""
    all_directors = Films.query.select_from(Films).join(film_director).join(Directors).filter(
        (Films.film_id == film_id) &
        (Films.film_id == film_director.c.films_film_id) &
        (film_director.c.directors_director_id == Directors.director_id)
    ).add_columns(Directors.director_name).all()

    return all_directors


def insert_into_db(current_object) -> None:
    """ Add object of table in DB table
        :raise flask abort if insert into db not successes, code 500
    """
    try:
        db.session.add(current_object)
    except Exception as e:
        db.session.rollback()
        return abort(500, e)
    else:
        db.session.commit()


def insert_film_genres(new_film: Films, genre_names: list[str]) -> None:
    """Add genres into DB table Genres and links to the film_genre table.
        :return None
    """
    for genre_name in genre_names:
        # looking for genre in Genres table
        # if current genre not present in the table - add this genre
        if not Genres.query.filter_by(genre_name=genre_name).first():
            genre = Genres(genre_name=genre_name)
            insert_into_db(genre)
        new_genre = Genres.query.filter_by(genre_name=genre_name).first()
        # add genre_id and film_id into associated table
        new_film.relation_film_genre.append(new_genre)

    db.session.commit()


def insert_film_directors(new_film: Films, director_names: list[str]) -> None:
    """Add directors into DB table Directors and links to the film_director table.
        :return None
    """
    for director_name in director_names:
        # looking for genre in Genres table
        # if current genre not present in the table - add this genre
        if not Directors.query.filter_by(director_name=director_name).first():
            director = Directors(director_name=director_name)
            insert_into_db(director)
        new_director = Directors.query.filter_by(director_name=director_name).first()
        # add director_id and film_id into associated table
        new_film.relation_film_director.append(new_director)

    db.session.commit()


def check_directors(director_names: Optional[List[str]]) -> list[str]:
    """Check if director_names is empty:
    get all directors from DB and convert it to list
        :return director_names: list of strings"""
    # check directors
    if not director_names:
        director_names = []
        # get all directors
        directors = Directors.query.add_columns(Directors.director_name).all()
        # convert to list
        for director in directors:
            director_names.append(director[1])
    return director_names


def check_genres(genre_names: Optional[List[str]]) -> list[str]:
    """Check if genre_names is empty:
    get all genres from DB and convert it to list
        :return genre_names: list of strings"""
    # check genres
    if not genre_names:
        genre_names = []
        # get all genres
        genres = Genres.query.add_columns(Genres.genre_name).all()
        # convert to list
        for genre in genres:
            genre_names.append(genre[1])
    return genre_names


def check_sorting(sorting: Optional[str]) -> Optional[str]:
    """Check sorting parameter
        :return 'rating' or 'release_date' or None"""
    if sorting == 'rating':
        return Films.rating.desc()
    if sorting == 'release_date':
        return Films.release_date.desc()
    return None


def convert_release_range(release_range: Optional[List[str]]) -> list[date]:
    """Check release_range parameter and convert string to date: Date
    if param is None set release range from '1900-01-01' to today date
        :returns release_range: list[date]"""
    if not release_range:
        release_range = [convert_str_to_date("1900-01-01"), date.today()]
    else:
        release_range = [convert_str_to_date(release_range[0]),
                         convert_str_to_date(release_range[1])]
    return release_range


def search_films(film_mask: str, release_range: Optional[List[str]],
                 director_names: Optional[List[str]], genre_names: Optional[List[str]],
                 pagination: int, page_number: int, sorting: str) -> dict:
    """Search film by:
        - partial film name match
        - release (from start date to end date)
        - directors
        - genres
        contain sorting by date or film's rating
        contain pagination (10 by default)
    :returns list of dicts containing all find films parameters"""
    # check and set sorting
    sorting = check_sorting(sorting)

    # check and set release range
    release_range = convert_release_range(release_range)

    # check and set directors
    director_names = check_directors(director_names)

    # check and set genres
    genre_names = check_genres(genre_names)

    # search
    all_films = Films.query.select_from(Films) \
        .join(film_genre) \
        .join(film_director) \
        .join(Genres) \
        .join(Directors) \
        .filter(
        (Films.film_name.ilike("%" + film_mask + "%")) &
        (Films.film_id == film_genre.c.films_film_id) &
        (film_genre.c.genres_genre_id == Genres.genre_id) &
        (Genres.genre_name.in_(genre_names)) &
        (film_director.c.directors_director_id == Directors.director_id) &
        (Directors.director_name.in_(director_names)) &
        (Films.release_date.between(release_range[0], release_range[1]))) \
        .add_columns(
        Films.film_id,
        Films.user_id_added_film,
        Films.film_name,
        Films.description,
        Films.rating,
        Films.number_of_rated_users,
        Films.release_date,
        Films.poster_link
    ).order_by(sorting).paginate(per_page=pagination, page=page_number)

    list_of_films = []
    for i in all_films.items:
        # get all directors of film
        directors = get_directors(i.film_id)
        # get all genres of film
        genres = get_genres(i.film_id)
        # convert to dict
        list_of_films.append(convert_to_dict(i, directors, genres))

    return list_of_films


def insert_film(user_id: int, film_name: str, description: Optional[str], release_date: str,
                poster_link: Optional[str], genre_names: Optional[list[str]],
                director_names: Optional[List[str]]) -> dict:
    """Insert film data in DB
        :returns dict containing all find films parameters
        :raise flask abort if film with same name and release is already in DB, code 404"""
    # convert type str to type Date
    release_date = convert_str_to_date(release_date)

    # check if film already in the DB
    if Films.query.filter_by(film_name=film_name, release_date=release_date).first():
        return abort(404, f'Film with {film_name} name and same release year already exist')
    # create object of Films DB
    new_film = Films(user_id_added_film=user_id, film_name=film_name,
                     description=description, release_date=release_date,
                     poster_link=poster_link)
    insert_into_db(new_film)
    # insert genres into DB
    if genre_names:
        insert_film_genres(new_film, genre_names)
    # insert directors into DB
    if director_names:
        insert_film_directors(new_film, director_names)

    # get all directors and genres parameters of film
    film = Films.query.filter_by(film_id=new_film.film_id).first()
    directors = get_directors(new_film.film_id)
    genres = get_genres(new_film.film_id)

    return convert_to_dict(film, directors, genres)


def edit_film(film_id: int, film_name: Optional[str], description: Optional[str],
              release_date: Optional[str], poster_link: Optional[str],
              director_names: Optional[list], genre_names: Optional[list]) -> dict:
    """Change film parameters
        :returns dict containing all find films parameters
        :raise flask abort if film with current id not in DB, code 404"""
    # check is film in DB
    film = Films.query.filter_by(film_id=film_id).first_or_404(description="No film with this id")
    # change film parameters if it exist
    if film_name:
        film.film_name = film_name
    if description:
        film.description = description
    if release_date:
        film.release_date = release_date
    if poster_link:
        film.poster_link = poster_link
    if director_names:
        insert_film_directors(film, director_names)
    if genre_names:
        insert_film_genres(film, genre_names)

    db.session.commit()

    # get all film params and all genres and directors
    edited_film = Films.query.filter_by(film_id=film_id).first()
    directors = get_directors(edited_film.film_id)
    genres = get_genres(edited_film.film_id)

    return convert_to_dict(edited_film, directors, genres)


def delete_film(film_id: int):
    """Delete the film
    and data from film-director"""
    film = Films.query.filter_by(
        film_id=film_id).first_or_404(description=f"No film with this id {film_id}")
    try:
        db.session.delete(film)
    except Exception as e:
        db.session.rollback()
        return abort(500, e)
    db.session.commit()
    return {"message": "Successfully deleted"}


def delete_director(director_name: str):
    """Delete the director
        """
    director = Directors.query.filter_by(
        director_name=director_name).first_or_404(description="No director with this name")
    try:
        db.session.delete(director)
    except Exception as e:
        db.session.rollback()
        return abort(500, e)
    db.session.commit()
    return {"message": "Successfully deleted"}


def convert_to_dict(film: Films, directors: Directors, genres: Genres) -> dict:
    """ Create dict from attributes to adopt it for json.
        :returns dict containing all find films parameters """
    release_date = datetime.strftime(film.release_date, "%Y.%m.%d")
    film = {"film_id": film.film_id, "user_id": film.user_id_added_film,
            "film_name": film.film_name, "description": film.description,
            "rating": film.rating, "number_of_rated_users": film.number_of_rated_users,
            "release_date": release_date, "poster_link": film.poster_link,
            "director_names": [], "genre_names": []}

    if directors:
        for i in directors:
            film["director_names"].append(i.director_name)
    else:
        film["director_names"].append("unknown")
    if genres:
        for i in genres:
            film["genre_names"].append(i.genre_name)
    else:
        film["genre_names"].append("unknown")

    return film
