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


class UserGuide(HydraHeadApp):

    def __init__(self, title = '', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self) -> None:
        st.markdown("<h1 style='text-align: center;'>User Guide</h1>", unsafe_allow_html=True)
        st.write("This page showcase the elements ChatbotX can display. It will help you better interact with the bot by using the correct words it'll understand.")


        with st.expander("Text elements"):
            st.header("This is a header")
            st.subheader("This is a subheader")

        st.info()


        st.divider()
        with st.expander("Video demo interacting with ChatbotX"):
            # Check if the user is already logged in
            st.title("Camera input demo")
            st.video("demo/camera_input_demo.mov")
            st.title("Data stats")
            st.video("demo/complex_example.mov")