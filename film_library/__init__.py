"""Flask simple web service for film library backend
with DB..."""
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api

# create and configure the app
app = Flask(__name__)

app.config.from_mapping(
    DEBUG=True,
    # a default secret that should be overridden by instance config
    SECRET_KEY='DEV',
    # The database URI that should be used for the connection
    SQLALCHEMY_DATABASE_URI=os.environ.get(
        'SQLALCHEMY_DATABASE_URI',
        default='postgresql+psycopg2://yurii:mypass@localhost:5432/postgres'),
    # Flask-SQLAlchemy will track modifications of objects and emit signals
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# create db object
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# initialize RestX object
api = Api(app)

# import models
from film_library import routes, models
