import streamlit as st
import sidebar
from hydralit import HydraHeadApp

from app_pages.chat import ChatBot
from auth.auth_connection import AuthSingleton


class ChatBotApp(HydraHeadApp):
    """
    This is an example signup application to be used to secure
    access within a HydraApp streamlit application.

    This application is an example of allowing an application to
    run from the login without requiring authentication.

    """

    def __init__(self, title="", generative_app_path=None, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.generative_app_path = generative_app_path
        self.auth = AuthSingleton().get_instance()

    def run(self) -> None:
        user_id, username = self.check_access()

        openai_api_key = self.auth.get_openai_key(user_id)
        role = self.auth.get_user_role(user_id)
        if role is None:
            raise Exception("Please contact the developer. (error code: 0)")
        if openai_api_key is None and role == "subscriber":
            raise Exception("Please contact the developer. (error code: 1)")
        if openai_api_key is None and role == "guest":
            openai_api_key = st.secrets["openai_api_key"]
        st.session_state.openai_api_key = openai_api_key

        sidebar.setup()

        # if time_sandbox.setup():
        chat = ChatBot(user_id, username, self.generative_app_path)
        chat.setup()


if __name__ == "__main__":
    ChatBotApp().run()
