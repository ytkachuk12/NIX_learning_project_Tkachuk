"""Methods for interacting with the DB:
contain interaction with user's side db"""

from typing import Optional

from flask import abort
import bcrypt

from film_library.models import Users, db


def hashing_pass(password: str) -> str:
    """Hash password with bcrypt module
    :return hash"""
    # password = user input, and generate salt
    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())


def checking_pass(nickname: str, password: str) -> Optional[int]:
    """Check the DB contains nickname and password hash
    :returns user: Users object if nickname and password correct or None"""
    check_user = Users.query.filter_by(nickname=nickname).first_or_404(description="Incorrect nickname")
    if bcrypt.checkpw(password.encode('utf8'), check_user.hash_and_salt):
        return check_user
    return None


def checking_nickname(nickname: str) -> bool:
    """Check the presence of user's nickname in DB
    :return bool"""
    if Users.query.filter_by(nickname=nickname).first():
        return True
    return False


def checking_email(email: str) -> bool:
    """check the presence of user's email in DB
    :return bool"""
    if Users.query.filter_by(email=email).first():
        return True
    return False


def register_user(nickname: str, password: str, email: str, first_name: Optional[str] = None,
                  surname: Optional[str] = None, age: Optional[int] = None, admin: bool = False) -> int:
    """Insert new user in db
    :return user id
    :raise flask abort if nickname is already in db, code 404
    :raise flask abort if email is already in db, code 404
    :raise flask abort if is not possible insert data in DB, code 500"""
    # create and add user to base
    if checking_nickname(nickname):
        return abort(404, f"User {nickname} is already registered.")
    if checking_email(email):
        return abort(404, f"User {email} is already registered.")
    # create hash_pass
    hash_and_salt = hashing_pass(password)
    # create object of Users table and insert it in db
    user = Users(nickname=nickname, hash_and_salt=hash_and_salt, email=email,
                 first_name=first_name, surname=surname, age=age, admin=admin)
    try:
        db.session.add(user)
    except Exception as e:
        db.session.rollback()
        return abort(500, e)
    else:
        db.session.commit()
    return user.id


if __name__ == "__main__":
    pass
