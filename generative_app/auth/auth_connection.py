import streamlit as st
import psycopg2
import uuid
import json
from typing import Dict

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
        add_user_session = "INSERT INTO UserSessions (\"user_id\", \"session_token\") VALUES (%s,%s);"
        self.insert_query(add_user_session, (user_id, session_token))

    def get_code(self, user_id:int) -> str:
        # Execute query.
        check_code = f"SELECT source_code FROM UserData WHERE user_id = '{user_id}' LIMIT 1;"
        code = self.run_query(check_code)
        if code:
            return code[0][0]
        return None

    def get_message_history(self, user_id:int) -> Dict:
        # Execute query.
        check_code = f"SELECT message_history FROM userdata WHERE user_id = '{user_id}' LIMIT 1;"
        message_history = self.run_query(check_code)
        if message_history:
            return message_history
        return Dict()

    def set_code(self, user_id:int, code:int) -> str:
        # Replace " with ' to avoid SQL syntax error.
        code = code.replace('"', "''")

        # Check if user_id exists.
        check_user_id = f"SELECT user_id FROM userdata WHERE user_id = '{user_id}' LIMIT 1;"
        if self.run_query(check_user_id):
            # Execute query to update
            update_code = f"UPDATE userdata SET source_code='{code}' WHERE user_id='{user_id}';"
            self.insert_query(update_code, (user_id, code))
        else:
            # Execute query to insert
            insert_code = "INSERT INTO userdata (\"user_id\", \"source_code\") VALUES (%s,%s);"
            self.insert_query(insert_code, (user_id, code))


    def set_message_history(self, user_id:int, message_history: Dict) -> str:
        # Check if user_id exists.
        check_user_id = f"SELECT user_id FROM userdata WHERE user_id = '{user_id}' LIMIT 1;"
        if self.run_query(check_user_id):
            # Execute query to update
            update_messages = f"UPDATE userdata SET message_history='{message_history}' WHERE user_id='{user_id}';"
            self.insert_query(update_messages, (user_id, json.dumps(message_history)))
        else:
            # Execute query to update.
            insert_messages = "INSERT INTO userdata (\"user_id\", \"message_history\") VALUES (%s,%s);"
            self.insert_query(insert_messages, (user_id, json.dumps(message_history)))

    def list_to_dict(self, rows) -> Dict:
        # Convert list of tuples to dict.
        return {f'message_{idx}': row for idx, row in enumerate(rows)}

if __name__ == '__main__':
    auth = Auth()
    message = [
            {"role": "assistant",
             "content": """
             Hello! I'm 🤖ChatbotX designed to help you create a Streamlit App.

             here are the few commands to control me:
             /undo: undo the last instruction
             /reset: reset the app
             /save: save the streamlit script in an independant app

             I will generate the Streamlit App here [Sandbox](https://chatbotx-client1.pival.fr/)"""
             },
        ]
    print(auth.list_to_dict(message))
    auth.set_message_history(10, auth.list_to_dict(message))
    print(auth.get_message_history(1))
    for _, values in auth.get_message_history(1).items():
        for role, message in values.items():
            print("role:", role)
            print("message:", message)