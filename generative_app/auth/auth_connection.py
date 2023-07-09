import streamlit as st
import psycopg2
import uuid
import json
import datetime
import auth.cookie_manager as cookie_manager
from typing import Dict, List, Any, Tuple, Union

from auth.utils import crypt_password, is_password_ok

def generate_user_session_token() -> str:
    return str(uuid.uuid4())

class Auth:
    def __init__(self, expiration_time=10):
        self.conn = self.init_connection()
        self.cookies = cookie_manager.CookieManager()
        self.token_expiration_min = expiration_time

    # Initialize connection.
    # Uses st.cache_resource to only run once.
    def init_connection(self):
        return psycopg2.connect(**st.secrets["postgres"])

    # Perform query.
    # Uses st.cache_data to only rerun when the query changes or after 10 min.
    def run_query(self, query):
        with self.conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()

    def insert_query(self, query, insert: Tuple[Any] or List[Any]):
        with self.conn.cursor() as cur:
            cur.execute(query, insert)
            self.conn.commit()
            count = cur.rowcount

    def check_user(self, username:str, password:str):
        # Execute query.
        get_pass = f"SELECT password FROM users WHERE username = '{username}' LIMIT 1;"
        password_bytes = self.run_query(get_pass)
        if password_bytes:
            return is_password_ok(password, password_bytes[0][0])
        return False

    def get_user_id(self, username:str, password:str) -> int:
        # Execute query.
        check_user = f"SELECT user_id, password FROM users WHERE username = '{username}' LIMIT 1;"
        user_id, password_bytes = self.run_query(check_user)[0]
        if user_id and is_password_ok(password, password_bytes):
            return int(user_id)
        return -1

    def get_username_from_id(self, user_id:int):
        # Execute query.
        get_username = f"SELECT username FROM users WHERE user_id = '{user_id}' LIMIT 1;"
        if rows := self.run_query(get_username):
            return str(rows[0][0])
        return None

    def is_mail_exists(self, username:str):
        # Execute query.
        get_mail = f"SELECT email FROM users WHERE username = '{username}' LIMIT 1;"
        rows = self.run_query(get_mail)
        if rows:
            return str(rows[0][0])
        return None

    def add_user(self, username:str, password:str, email:str):
        # Execute query.
        add_user = f"INSERT INTO users (\"username\", \"password\", \"email\", \"role\") VALUES (%s,%s,%s,%s);"
        self.insert_query(add_user, (username, crypt_password(password), email, 'guest'))

    def get_user_session(self, user_id:str) -> bool:
        check_code = f"SELECT * FROM UserSessions WHERE user_id = '{user_id}' LIMIT 1;"
        if self.run_query(check_code):
            return True
        return False

    def add_user_session(self, user_id:int):
        # Check if the user already has a session.
        if self.get_user_session(user_id):
            # Remove the user session before anything.
            self.remove_user_session(user_id)

        session_token = generate_user_session_token()
        expires_at = datetime.datetime.now() + datetime.timedelta(minutes=self.token_expiration_min)

        # Execute query.
        add_user_session = "INSERT INTO UserSessions (\"user_id\", \"session_token\", \"created_at\", \"last_accessed\") VALUES (%s,%s,%s,%s);"
        self.insert_query(add_user_session, (user_id, session_token, datetime.datetime.now(), datetime.datetime.now()))

        # Set cookie. The expiration should be 10 minutes from now.
        self.cookies.set('user_token', session_token, expires_at=expires_at)

    def extend_user_session(self, user_id:int, user_token:str):
        auto_login = self.can_auto_login()
        if auto_login[0] and auto_login[2] == "User token not found.":
            raise Exception("User cannot extend session because the token is expired")

        expires_at = datetime.datetime.now() + datetime.timedelta(minutes=self.token_expiration_min)

        # Execute query.
        add_user_session = "UPDATE UserSessions SET last_accessed = %s WHERE user_id = %s;"
        self.insert_query(add_user_session, [datetime.datetime.now(), user_id])

        # Reset expiration cookie. The expiration should be 10 minutes from now.
        if user_cookie := self.cookies.get('user_token'):
            self.cookies.delete('user_token')
            self.cookies.set('user_token', user_cookie, expires_at=expires_at)
        else:
            raise Exception("User cookie not found.")

    def remove_user_session(self, user_id:int):
        """ Remove user session from database and the user token """
        query = "DELETE FROM UserSessions WHERE user_id = %s;"
        self.insert_query(query, (user_id, ))
        self.cookies.delete('user_token')

    def can_auto_login(self) -> Union[bool, int, str]:
        user_token = self.cookies.get('user_token')
        if not user_token:
            return False, None, "User token not found."

        """ Check if user can auto login. If not you should consider logging them out."""
        query = f"SELECT last_accessed, user_id FROM UserSessions WHERE session_token = '{user_token}' LIMIT 1;"
        if result := self.run_query(query):
            last_accessed, user_id = result[0]
            if last_accessed:
                last_accessed = last_accessed
                token_expired = datetime.datetime.now() > last_accessed + datetime.timedelta(minutes=self.token_expiration_min)
                return not token_expired, user_id, "User logged out due to inactivity." if token_expired else "User logged in."
        return False, None, "User session not found."

    def get_code(self, user_id:int) -> str | None:
        # Execute query.
        check_code = f"SELECT source_code FROM UserData WHERE user_id = '{user_id}' LIMIT 1;"
        code = self.run_query(check_code)
        if code:
            return code[0][0]
        return None

    def get_message_history(self, user_id:int) -> Dict | None:
        # Execute query.
        check_code = f"SELECT message_history FROM userdata WHERE user_id = '{user_id}' LIMIT 1;"
        message_history = self.run_query(check_code)

        if message_history:
            if message_history[0][0]:
                return message_history[0][0]
        return None

    def set_code(self, user_id:int, code:str) -> str:
        # Replace " with ' to avoid SQL syntax error.
        code = code.replace('"', "''")

        # Check if user_id exists.
        check_user_id = f"SELECT user_id FROM userdata WHERE user_id = '{user_id}' LIMIT 1;"
        if self.run_query(check_user_id):
            # Execute query to update
            update_code = "UPDATE userdata SET source_code = %s WHERE user_id = %s;"
            self.insert_query(update_code, [code, user_id])
        else:
            # Execute query to insert
            insert_code = "INSERT INTO userdata (\"user_id\", \"source_code\") VALUES (%s,%s);"
            self.insert_query(insert_code, (user_id, code))


    def set_message_history(self, user_id:int, message_history: Dict) -> str:
        # Check if user_id exists.
        check_user_id = f"SELECT user_id FROM userdata WHERE user_id = '{user_id}' LIMIT 1;"
        if self.run_query(check_user_id):
            # Execute query to update
            update_messages = "UPDATE userdata SET message_history = %s WHERE user_id = %s;"
            self.insert_query(update_messages, [json.dumps(message_history), user_id])
        else:
            # Execute query to update.
            insert_messages = "INSERT INTO userdata (\"user_id\", \"message_history\") VALUES (%s,%s);"
            self.insert_query(insert_messages, (user_id, json.dumps(message_history)))

class AuthSingleton:
    __instance = None
    def get_instance(self) -> Auth:
        if AuthSingleton.__instance is None :
            AuthSingleton.__instance = Auth(20)
        return AuthSingleton.__instance

