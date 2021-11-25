from film_library import db
from film_library.db_user import register_user
from film_library.db_film import insert_film

USERS = (
    ("yurii", "password", "email1@gmail.com", "yurii", "tkachuk", 20, True),
    ("maxmax", "Password", "email2@gmail.com", "max", "maximov", 20, False),
    ("ivan", "passpass", "email3@gmail.com", "ivan", "ivanov", 10, False)
)

FILMS = (
    (1, "matrix", "some description", "2003-12-12", "link1",
     ["thriller", "fantastic"], ["dir1", "dir2"]),
    (2, "die hard", "description some", "1995-10-10", "link2",
     ["thriller", "detective"], ["dir3"]),
    (3, "big bang", "descript", "2005-07-07", "link3",
     ["comedy", "sitcom"], ["dir4", "dir5"]),
    (2, "some film", "with descript", "2010-10-10", "link4",
     ["comedy"], ["dir2"])
)


def register_test_user():
    for user in USERS:
        register_user(user[0], user[1], user[2], user[3], user[4], user[5], user[6])
        pass


def insert_test_film():
    for film in FILMS:
        insert_film(film[0], film[1], film[2], film[3], film[4], film[5], film[6])


def set_test_db():
    db.drop_all()
    db.create_all()
    register_test_user()
    insert_test_film()


if __name__ == "__main__":
    register_test_user()
    insert_test_film()
