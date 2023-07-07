import os
import streamlit as st
import uuid
import sidebar
from hydralit import HydraHeadApp

from chat import ChatBot


class ChatBotApp(HydraHeadApp):
    """
    This is an example signup application to be used to secure access within a HydraApp streamlit application.

    This application is an example of allowing an application to run from the login without requiring authentication.

    """

    def __init__(self, title = '', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title


    def run(self) -> None:
        sidebar.setup()

        generative_app_path = os.path.join(os.getcwd(), ".generated_apps", "generated_app.py")

        # Generate uuid
        if "client_id" not in st.session_state:
            st.session_state["client_id"] = str(uuid.uuid4())

        # Check if it's the first run
        st.session_state["first_run"] = "first_run" not in st.session_state


        #if time_sandbox.setup():
        chat = ChatBot(generative_app_path)
        chat.setup(st.session_state["first_run"])

        st.markdown('<div id="input-container-placeholder"></div>', unsafe_allow_html=True)

if __name__ == '__main__':
    ChatBotApp().run()