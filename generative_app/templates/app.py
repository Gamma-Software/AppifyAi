import time
import os
from typing import Dict
import streamlit as st
from hydralit import HydraHeadApp


class App(HydraHeadApp):
    """
    This is an example signup application to be used to secure access within a HydraApp streamlit application.

    This application is an example of allowing an application to run from the login without requiring authentication.

    """

    def __init__(self, title = '', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title


    def run(self) -> None:
        """
        Application entry point.
        """
        # --- start sandbox
        st.write("This is your sandbox application.")
        # --- end sandbox