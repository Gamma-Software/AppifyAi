template_app = """import time
import os
from typing import Dict
import streamlit as st
from hydralit import HydraHeadApp


class App(HydraHeadApp):
    def __init__(self, title = '', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title


    def run(self) -> None:
        #---start
{code}
        #---end
"""
