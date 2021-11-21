from flask_restx import model, fields

from film_library import api

user_register_resource = api.model('User_register', {
    "nickname": fields.String(required=True, description="string more than 4 symbols and less than 50"),
    "password": fields.String(required=True, description="string more than 6 symbols and less than 50"),
    "email": fields.String(required=True)
    })

user_login_resource = api.model('User_login', {
    "nickname": fields.String(required=True),
    "password": fields.String(required=True)
    })

user_model = api.model("User", {
    "id": fields.Integer(required=True),
    "message": fields.String()
    })

film_search_resource = api.model('Film_search', {
    'film_mask': fields.String(),
    'release_range': fields.String(description="dates must be in 'YYYY-MM-DD' \
    format and separate by comma without space"),
    'director_names': fields.String(description="must be separate by comma without space"),
    'genre_names': fields.String(description="must be separate by comma without space"),
    'pagination': fields.Integer(),
    'page_number': fields.Integer(),
    'sorting': fields.String(description="can be 'rating' or 'release_date'")
    })

film_insert_resource = api.model('Film_insert', {
    'film_name': fields.String(required=True),
    'description': fields.String(),
    'release_date': fields.String(required=True, description="date must be in 'YYYY-MM-DD' format"),
    'poster_link': fields.String(),
    'director_names': fields.String(),
    'genre_names': fields.String()
    })

film_change_resource = api.model('Film_change', {
    'film_id': fields.Integer(required=True),
    'film_name': fields.String(),
    'description': fields.String(),
    'release_date': fields.String(description="date must be in 'YYYY-MM-DD' format"),
    'poster_link': fields.String(),
    'director_names': fields.String(description="must be separate by comma without space"),
    'genre_names': fields.String(description="must be separate by comma without space")
    })

# why film_id has bag?
film_delete_resource = api.model('Film_delete', {
    'id': fields.Integer(required=True)
    })

film_rate_resource = api.model('Film_rate', {
    'film_id': fields.String(required=True),
    'user_rate': fields.Integer(required=True, description="must be more than 0 and less than 6")
    })

film_model = api.model("Film", {
    "film_id": fields.Integer(required=True),
    "user_id": fields.Integer(required=True),
    "film_name": fields.String(required=True),
    "description": fields.String(required=True),
    "rating": fields.Float(required=True),
    "number_of_rated_users": fields.Integer(required=True),
    "release_date": fields.String(required=True),
    "poster_link": fields.String(required=True),
    "director_names": fields.String(description="must be separate by comma without space"),
    "genre_names": fields.String(description="must be separate by comma without space")
})
