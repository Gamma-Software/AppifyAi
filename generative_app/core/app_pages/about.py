import os
import sys
import time
from typing import Dict, Union
import shutil
from pathlib import Path
import streamlit as st
from auth.auth_connection import AuthSingleton
import ui.chat_init as chat_init
from hydralit import HydraHeadApp
from streamlit.delta_generator import DeltaGenerator


class About(HydraHeadApp):
    def __init__(self, title = '', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self) -> None:
        self.setup_sidebar()

        if st.button("Go back to login"):
            # set access level to a negative number to allow a kick to the unsecure_app set in the parent
            self.set_access(0, 'guest')

            #Do the kick to the signup app
            self.do_redirect()

        user_guide_tab, demo_tab, dev = st.tabs(["What is ChatbotX ?", "Demonstrations", "More about the developer"])
        with user_guide_tab:
            with open(os.path.join(os.getcwd(), f"generative_app/core/ui/{st.session_state.lang}/about.md"), "r") as about_file:
                about = about_file.read()
            st.markdown(about)

        with demo_tab:
            with st.expander("Camera input demo"):
                # Check if the user is already logged in
                st.video("demo/camera_input_demo.mov")
            with st.expander("Data stats"):
                st.video("demo/complex_example.mov")

        with dev:
            st.title("Founder and Developer")
            st.image(os.path.join(os.getcwd(), f"generative_app/core/ui/profile_round.png"))
            with open(os.path.join(os.getcwd(), f"generative_app/core/ui/{st.session_state.lang}/about_dev.md"), "r") as about_file:
                about = about_file.read()
            st.markdown(about)

    def setup_sidebar(self):
        with st.sidebar:
            st.session_state.lang = st.selectbox(
                'Language',
                ('🇺🇸 en', '🇫🇷 fr'))[-2:]