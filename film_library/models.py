""" Database model.
Create tables
 """

from flask_login import UserMixin

from film_library import db

# Association table for table films and directors (many to many relationship)
film_director = db.Table('film_director',
                         db.Column('films_film_id',
                                   db.ForeignKey('films.film_id', ondelete='CASCADE'),
                                   primary_key=True),
                         db.Column('directors_director_id',
                                   db.ForeignKey('directors.director_id', ondelete='CASCADE'),
                                   primary_key=True)
                         )

# Association table for table films and genres (many to many relationship)
film_genre = db.Table('film_genre',
                      db.Column('films_film_id',
                                db.ForeignKey('films.film_id', ondelete='CASCADE'),
                                primary_key=True),
                      db.Column('genres_genre_id',
                                db.ForeignKey('genres.genre_id', ondelete='CASCADE'),
                                primary_key=True)
                      )


class Users(UserMixin, db.Model):
    """Create User's table"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nickname = db.Column(db.String(50), unique=True, nullable=False)
    hash_and_salt = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    age = db.Column(db.Integer)
    admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"User's id: {self.id}"


class Films(db.Model):
    """Create Film's table"""
    __tablename__ = 'films'
    film_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id_added_film = db.Column(db.Integer, db.ForeignKey('users.id'))
    film_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String)
    rating = db.Column(db.Float, default=0)
    number_of_rated_users = db.Column(db.Integer, default=0)
    release_date = db.Column(db.Date)
    poster_link = db.Column(db.String, unique=True)

    # relation_film_derector = db.relationship(
    #     'Directors', secondary=film_director, lazy='subquery',
    #     backref=db.backref('relation_film_director', lazy=True, passive_deletes=True))
    #
    # relation_film_genre = db.relationship(
    #     'Genres', secondary=film_genre, lazy='subquery',
    #     backref=db.backref('relation_film_genre', lazy=True, passive_deletes=True))

    def __repr__(self):
        return f"Film's id: {self.film_id}"


class Directors(db.Model):
    """Create Director's table"""
    __tablename__ = 'directors'
    director_id = db.Column(db.Integer, primary_key=True, nullable=False)
    director_name = db.Column(db.String(100), nullable=False)

    add_film_director = db.relationship(
        'Films', secondary=film_director, lazy='subquery',
        backref=db.backref('add_film_director', lazy=True, passive_deletes=True)
        )

    def __repr__(self):
        return f"Director's id: {self.director_id}"


class Genres(db.Model):
    """Create genre's table"""
    __tablename__ = 'genres'
    genre_id = db.Column(db.Integer, primary_key=True, nullable=False)
    genre_name = db.Column(db.String(100), nullable=False)

    add_film_genre = db.relationship(
        'Films', secondary=film_genre, lazy='subquery',
        backref=db.backref('add_film_genre', lazy=True, passive_deletes=True)
        )

    def __repr__(self):
        return f"Genre's id: {self.genre_id}"


db.create_all()
