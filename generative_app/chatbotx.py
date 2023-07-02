import warnings
import os
import streamlit as st
import uuid
import sidebar
from chat import ChatBot
import time_sandbox

warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="ChatbotX",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state=sidebar.sidebar_init_state,
    menu_items={
        "Report a bug": "https://github.com/Gamma-Software/ChatbotX/issues",
        "About": """
            # ChatbotX
            Transform conversations into stunning web apps. Dynamic code generation + intuitive interface. Unleash your creativity effortlessly. Use the power of GPT OpenAI LLM and Langchain.

            # Author
            [Valentin Rudloff](https://valentin.pival.fr/) is a French engineer that loves to learn and build things with code.
            [☕ Buy me a coffee](https://www.buymeacoffee.com/valentinrudloff)

            Go to the GitHub repo to learn more about the project. https://github.com/Gamma-Software/ChatbotX
            """,
    },
)

sidebar.setup()

# Generate uuid
if "client_id" not in st.session_state:
    st.session_state["client_id"] = str(uuid.uuid4())

# Check if it's the first run
st.session_state["first_run"] = "first_run" not in st.session_state

generative_app_path = os.path.join(os.getcwd() , "sandbox", "app.py")
#if time_sandbox.setup():
chat = ChatBot(generative_app_path)
chat.setup(st.session_state["first_run"])

st.markdown('<div id="input-container-placeholder"></div>', unsafe_allow_html=True)