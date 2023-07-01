import streamlit as st

warnings.filterwarnings("ignore")

client = os.environ.get("clientid")

st.set_page_config(
    page_title="ChatbotX-Sandbox-{}".format(client),
    page_icon="🤖",
    layout="centered",
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

import sandbox