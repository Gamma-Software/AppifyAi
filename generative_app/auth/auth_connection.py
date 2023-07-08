import streamlit as st
import psycopg2
import uuid

def generate_user_session_token() -> str:
    return str(uuid.uuid4())

class Auth:

    def __init__(self, title = '', **kwargs):
        self.conn = self.init_connection()

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

    def insert_query(self, query, insert):
        with self.conn.cursor() as cur:
            cur.execute(query, insert)
            self.conn.commit()
            count = cur.rowcount
            print(count, "Record inserted successfully into mobile table")

    def check_user(self, username:str, password:str):
        # Execute query.

        check_user = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}' LIMIT 50;"
        rows = self.run_query(check_user)
        if len(rows) == 0:
            return False
        else:
            return True

    def get_user_id(self, username:str, password:str):
        # Execute query.
        check_user = f"SELECT user_id FROM users WHERE username = '{username}' AND password = '{password}' LIMIT 1;"
        rows = self.run_query(check_user)
        print('get_user_id', rows[0][0])
        return int(rows[0][0])

    def add_user(self, username:str, password:str, email:str):
        # Execute query.
        add_user = f"INSERT INTO users (\"username\", \"password\", \"email\", \"role\") VALUES (%s,%s,%s,%s);"
        self.insert_query(add_user, (username, password, email, 'guest'))

    def add_user_session(self, user_id:int):
        session_token = generate_user_session_token()

        # Execute query.
        add_user_session = f"INSERT INTO user_sessions (\"user_id\", \"session_token\") VALUES (%s,%s);"
        self.insert_query(add_user_session, (user_id, session_token))

