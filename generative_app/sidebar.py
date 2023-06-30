import streamlit as st
import os

sidebar_init_state = "auto"

def setup():
    with st.sidebar:
        with open(os.path.join(os.getcwd(), "generative_app/ui/sidebar.md"), "r") as sidebar_file:
            sidebar_content = sidebar_file.read()

        with open(os.path.join(os.getcwd(), "generative_app/ui/styles.md"), "r") as styles_file:
            styles_content = styles_file.read()

        st.markdown(sidebar_content)
        st.write(styles_content, unsafe_allow_html=True)