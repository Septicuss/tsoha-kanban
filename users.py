from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text
from db import db
import boards

class User:

    def __init__(self, fetched_user):
        self.user_id = fetched_user.id
        self.username = fetched_user.username
        self.password_hash = fetched_user.password

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def get_collaborated_boards(self):
        return boards.get_collaborated_boards(self.user_id)

    def get_owned_boards(self):
        return boards.get_owned_boards(self.user_id)

    def has_access_to_board(self, board_id: int):
        return boards.get_board(board_id).can_modify(self.user_id)

    def delete(self):
        delete_user(self.user_id)

def get_user(username: str):
    sql = text("""
        SELECT * FROM users WHERE username = :username
    """)
    params = {'username': username}
    result = db.session.execute(sql, params)
    user = result.fetchone()

    if not user:
        return None
    return User(user)

def get_user_by_id(user_id: int):
    sql = text("""
        SELECT * FROM users
        WHERE id = :user_id
    """)
    result = db.session.execute(sql, {'user_id': user_id})
    user = result.fetchone()

    if not user:
        return None
    return User(user)

def user_exists(username: str):
    sql = text("SELECT * FROM users WHERE username = :username")
    params = {"username": username}
    user = db.session.execute(sql, params).fetchone()
    return bool(user)

def create_user(username: str, raw_password: str):

    hashed_password = generate_password_hash(raw_password)

    sql =  text("""
        INSERT INTO users (username, password) 
        VALUES (:username, :password)
        ON CONFLICT (username) DO NOTHING 
    """)
    params = {"username": username, "password": hashed_password}

    result = db.session.execute(sql, params)
    db.session.commit()

    return result.rowcount > 0

def delete_user(user_id: id):
    sql = text("""
        DELETE FROM users 
        WHERE id = :user_id
    """)
    db.session.execute(sql, {'user_id': user_id})
    db.session.commit()