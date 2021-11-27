"""Routes for app here"""
import logging

from flask_login import login_user, login_required, logout_user, LoginManager, current_user
from flask_restx import Resource, reqparse
from werkzeug.exceptions import abort

from film_library import app, api
from film_library.models import Users
from film_library.db_user import register_user, checking_pass
from film_library.db_film import (
    insert_film, delete_film, edit_film,
    get_user_creator, rate_film, search_films, delete_director
)
from film_library.api_models import (
    user_register_resource, user_login_resource, user_model,
    film_search_resource, film_insert_resource, film_change_resource, film_delete_resource,
    film_rate_resource, film_model, director_delete_resource, delete_model
)

login_manager = LoginManager(app)
login_manager.init_app(app)

# add logger. check log info in record.log file in root app folder
logging.basicConfig(filename='record.log', level=logging.DEBUG)


@app.teardown_request
def teardown_request(exception=None):
    """Launch after any request and print log to file record.log"""
    app.logger.info("After request")


@login_manager.user_loader
def load_user(id):
    """ For keeping user in session """
    return Users.query.get(int(id))


@api.route('/')
class HelloWorld(Resource):
    """root resource you can find swagger description here"""
    def get(self):
        """Root route
            :return swagger description of api"""
        return {'hello': 'hello world'}


@api.route('/login')
class LoginUser(Resource):
    """ Route login for login user
        :param nickname: str, required
        :param password: str, required
        :returns json: {id: int, message: str}"""
    @api.doc(body=user_login_resource)
    @api.marshal_with(user_model, code=201, envelope="user")
    def post(self):
        """method post"""
        parser = reqparse.RequestParser()
        parser.add_argument('nickname', type=str, required=True)
        parser.add_argument('password', type=str, required=True)

        args = parser.parse_args()

        user = checking_pass(args['nickname'], args['password'])
        if user:
            login_user(user)
            return {"id": current_user.id, "message": "Successfully logged in"}
        return abort(404, "Password not correct")


@api.route("/logout")
class LogoutUser(Resource):
    """ Route logout for logout user
            :returns json: {id: int, message: str}"""
    @login_required
    @api.marshal_with(user_model, code=200, envelope="users")
    def get(self):
        """method get"""
        user_id = current_user.id
        logout_user()
        return {"id": user_id, "message": "Logged out"}


@api.route('/register')
class RegisterUser(Resource):
    """ Route login for register new user
            :param nickname: str, required
            :param password: str, required
            :param email: str, required
            :param first_name: str
            :param surname: str
            :param age: int
            :param admin: bool, for default is False
            :returns json: {id: int, message: str}"""
    @api.doc(body=user_register_resource)
    @api.marshal_with(user_model, code=200, envelope="users")
    def post(self):
        """method post"""
        parser = reqparse.RequestParser()
        parser.add_argument('nickname', type=str, required=True)
        parser.add_argument('password', type=str, required=True)
        parser.add_argument('email', type=str, required=True)
        parser.add_argument('first_name', type=str)
        parser.add_argument('surname', type=str)
        parser.add_argument('age', type=int)
        parser.add_argument('admin', type=bool, default=False)

        args = parser.parse_args()

        if len(args['password']) < 7:
            return abort(404, f"User {args['password']} is too small.")
        if len(args['nickname']) < 5:
            return abort(404, f"User {args['nickname']} is too small.")

        user_id = register_user(args['nickname'], args['password'], args['email'],
                                args['first_name'], args['surname'], args['age'], args['admin'])

        return {"id": user_id, "message": "Successfully register"}


@api.route('/films')
class FilmsInteraction(Resource):
    """ Route films for add, delete, update and search films"""
    @api.marshal_with(film_model, code=200, envelope="films")
    @api.doc(body=film_search_resource)
    def get(self):
        """method get for search films by film mask, date-time, directors, genres
        method has pagination sorting parameters
            :param film_mask: str, required
            :param release_range: str
            :param director_names: str
            :param genre_names: str
            :param pagination: int, by default is 10
            :param page_number: int by default is 1
            :param sorting: str, can be "rating" or "release_range"
            :return json{films: [list of films]"""
        parser = reqparse.RequestParser()
        parser.add_argument('film_mask', type=str, location='args', required=True)
        # filter args
        parser.add_argument('release_range', type=str, action='split')
        parser.add_argument('director_names', type=str, action='split')
        parser.add_argument('genre_names', type=str, action='split')
        # pagination
        parser.add_argument('pagination', type=int, default=10)
        parser.add_argument('page_number', type=int, default=1)
        # sorting args
        parser.add_argument('sorting', type=str)

        args = parser.parse_args()

        all_films = search_films(
            args['film_mask'], args['release_range'], args['director_names'],
            args['genre_names'], args['pagination'], args['page_number'],
            args['sorting'])

        return all_films

    @api.marshal_with(film_model, code=201, envelope="films")
    @api.doc(body=film_insert_resource)
    @login_required
    def post(self):
        """method post for insert new films in DB
            :param film_name: str, required
            :param description: str
            :param release_date: str, required
            :param poster_link: str, unique
            :param genre_names: str
            :param director_names: str
            :return json {film: [{all film data}]}
            """
        parser = reqparse.RequestParser()
        parser.add_argument('film_name', type=str, required=True)
        parser.add_argument('description', type=str)
        parser.add_argument('release_date', type=str, required=True)
        parser.add_argument('poster_link', type=str)
        parser.add_argument('genre_names', type=str, action='split')
        parser.add_argument('director_names', type=str, required=True, action='split')

        args = parser.parse_args()

        # take user id from flask_login
        user_id = current_user.id

        film = insert_film(user_id, args["film_name"], args["description"], args["release_date"],
                           args["poster_link"], args["genre_names"], args["director_names"])

        return film, 201

    @api.marshal_with(film_model, code=201, envelope="films")
    @api.doc(body=film_change_resource)
    @login_required
    def put(self):
        """method put for update film data in DB
            :param film_id: str, required
            :param film_name: str
            :param description: str
            :param release_data: str
            :param poster_link: str
            :param director_names: str
            :param genre_names: str
            :return json {film: [{all film data}]}
            """
        parser = reqparse.RequestParser()
        parser.add_argument("film_id", type=int, required=True)
        parser.add_argument("film_name", type=str)
        parser.add_argument("description", type=str)
        parser.add_argument("release_date", type=str)
        parser.add_argument("poster_link", type=str)
        parser.add_argument("director_names", type=str, action='split')
        parser.add_argument("genre_names", type=str, action='split')

        args = parser.parse_args()

        # take user object from flask_login
        user = current_user

        # check if this user did not creat this film or user is not admin
        if user.id != get_user_creator(args['film_id']) and not current_user.admin:
            abort(404, f"You can modify the films created by you Only, id: {user.id}")

        film = edit_film(
            args['film_id'], args['film_name'], args['description'], args['release_date'],
            args['poster_link'], args['director_names'], args['genre_names']
        )
        return film, 201

    @login_required
    @api.doc(body=film_delete_resource)
    @api.marshal_with(delete_model, code=200, envelope="deletes")
    def delete(self):
        """method delete for delete film from DB
            :param id: str, required
            :return json{message: str}
            """
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, required=True)

        args = parser.parse_args()

        # take user id from flask_login
        user = current_user

        # check if this user did not creat this film or user is not admin
        if user.id != get_user_creator(args['id']) and not current_user.admin:
            abort(404, f"You can modify the films created by you Only, id: {user.id}")

        return delete_film(args['id'])


@api.route("/directors")
class DelDirector(Resource):
    """ Route directors for delete directors from DB
        """
    @login_required
    @api.marshal_with(delete_model, code=200, envelope="deletes")
    @api.doc(body=director_delete_resource)
    def delete(self):
        """method delete for delete director from DB
        :param director_name: str, required
        :return json{message: str}"""
        parser = reqparse.RequestParser()
        parser.add_argument('director_name', type=str, required=True)

        args = parser.parse_args()

        # check if this user is not admin
        if not current_user.admin:
            abort(400, "You can't modify directors")

        return delete_director(args['director_name'])


@api.route('/film/rate')
class FilmsRate(Resource):
    """ Route film/rate for rate film
            """
    @api.marshal_with(film_model, code=200, envelope="films")
    @api.doc(body=film_rate_resource)
    def get(self):
        """method get for rate film
            :param film_id: str, required
            :param user_rate: int, required, in [0, 5] include
            :return json{film:[{all film param}}
            """
        parser = reqparse.RequestParser()
        parser.add_argument('film_id', type=int, required=True)
        parser.add_argument('user_rate', type=int, required=True)

        args = parser.parse_args()

        if args['user_rate'] > 5 or args['user_rate'] < 1:
            return abort(400, "Wrong rate value")
        film = rate_film(args['film_id'], args['user_rate'])
        return film
