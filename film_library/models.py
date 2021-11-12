""" Database model.
Create tables
 """
from sqlalchemy.dialects.postgresql import UUID

from film_library.app import db

# Association table for table films and directors (many to many relationship)
film_director = db.Table('film_director',
                         db.Column('films_film_id', db.ForeignKey('films.film_id'), primary_key=True),
                         db.Column('directors_director_id', db.ForeignKey('directors.director_id'), primary_key=True)
                         )


# Association table for table films and genres (many to many relationship)
film_genre = db.Table('film_genre',
                      db.Column('films_film_id', db.ForeignKey('films.film_id'), primary_key=True),
                      db.Column('genres_genre_id', db.ForeignKey('genres.genre_id'), primary_key=True)
                      )


class Users(db.Model):
    """Create User's table"""
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    nickname = db.Column(db.String(50), unique=True, nullable=False)
    hash_pass = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer)

    #films = db.relationship('films', backref='users', lazy=True)

    def __repr__(self):
        return f"User's id: {self.user_id}"


class Films(db.Model):
    """Create Film's table"""
    __tablename__ = 'films'
    film_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id_added_film = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    film_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String)
    rating = db.Column(db.Float, default=0)
    release_date = db.Column(db.Date)
    poster_link = db.Column(db.String, unique=True)

    def __repr__(self):
        return f"Film's id: {self.film_id}"


class Directors(db.Model):
    """Create Director's table"""
    director_id = db.Column(db.Integer, primary_key=True, nullable=False)
    director_name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Director's id: {self.director_id}"


class Genres(db.Model):
    """Create genre's table"""
    genre_id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"Genre's id: {self.genre_id}"


db.create_all()
