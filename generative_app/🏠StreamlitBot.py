import warnings
import os
import streamlit as st

import sidebar
import chat
import llm

warnings.filterwarnings("ignore")


st.set_page_config(
    page_title="Generative Streamlit App",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state=sidebar.sidebar_init_state,
    menu_items={
        "Report a bug": "https://github.com/Gamma-Software/GenerativeApp/issues",
        "About": """Generative App is a chatbot designed to help you creating Streamlit apps. It is built using OpenAI's GPT-4 and Streamlit.
            Go to the GitHub repo to learn more about the project. https://github.com/Gamma-Software/GenerativeApp
            """,
    },
)

st.title("Generative Streamlit App")
st.caption("Build Streamlit apps with the help of a chatbot 🤖")

sidebar.setup()

openai_api_key = st.secrets["openai_api_key"]

if openai_api_key:
    assistant = llm.setup(openai_api_key)
    generative_app_path = os.path.join(os.getcwd() , "generative_app", "pages" ,"🤖GeneratedApp.py")
    chat.setup(assistant, generative_app_path)

st.markdown('<div id="input-container-placeholder"></div>', unsafe_allow_html=True)