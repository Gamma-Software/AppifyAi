import time
import streamlit as st
from hydralit import HydraHeadApp
from hydralit_components import HyLoader, Loaders
import traceback
import sys

class LoadingApp(HydraHeadApp):

    def __init__(self, title = 'Loader', delay=0,loader=Loaders.standard_loaders, **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.delay = delay
        self._loader = loader

    def run(self,app_target):
        app_title = ''
        if hasattr(app_target,'title'):
            app_title = app_target.title

            if app_title == 'ChatbotX':
                try:
                    app_target.run()
                except Exception as e:
                    st.error('An error has occurred, please report it here https://github.com/Gamma-Software/ChatbotX/issues (add screenshot and error details)')
                    st.code(traceback.format_exc())
            else:
                try:
                    app_target.run()
                except Exception as e:
                    st.error('An error occured, please ask the bot to fix it. For instance, give him the following instruction: ')
                    st.code('Fix this error: {}'.format(traceback.format_exception_only(e)[0]))
                    with st.expander("Full Traceback"):
                        st.code(traceback.format_exc())
