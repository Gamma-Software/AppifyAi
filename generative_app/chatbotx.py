import os
import streamlit as st
import sidebar
from hydralit import HydraHeadApp

from chat import ChatBot


class ChatBotApp(HydraHeadApp):
    """
    This is an example signup application to be used to secure access within a HydraApp streamlit application.

    This application is an example of allowing an application to run from the login without requiring authentication.

    """
    def __init__(self, title = '', generative_app_path = None, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.generative_app_path = generative_app_path


    def run(self) -> None:
        user_id, _ = self.check_access()

        sidebar.setup()

        #if time_sandbox.setup():
        chat = ChatBot(user_id, self.generative_app_path)
        chat.setup()

        st.markdown('<div id="input-container-placeholder"></div>', unsafe_allow_html=True)

if __name__ == '__main__':
    ChatBotApp().run()