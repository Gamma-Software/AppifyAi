import streamlit as st
from hydralit import HydraHeadApp


class DemoApp(HydraHeadApp):
    """
    This is an example login application to be used to secure access within a HydraApp streamlit application.
    This application implementation uses the allow_access session variable and uses the do_redirect method if the login check is successful.

    """

    def __init__(self, title = '', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self) -> None:
        """
        Application entry point.
        """
        # Check if the user is already logged in
        st.title("Camera input demo")
        st.video("demo/camera_input_demo.mov")
        st.title("Data stats")
        st.video("demo/complex_example.mov")