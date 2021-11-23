"""Flask simple web service for film library backend
with DB..."""
from film_library import app


if __name__ == '__main__':
    app.run(debug=True)
