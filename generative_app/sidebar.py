import streamlit as st
import os
from PIL import Image

sidebar_init_state = "auto"

def extract_markdown_title(markdown_content: str) -> str:
    """ extract the title from a markdown string """
    title = ""
    for line in markdown_content.split("\n"):
        if line.startswith("#"):
            title = line.replace("#", "").strip()
            break
    return title

def setup():
    with st.sidebar:

        if "lang" not in st.session_state:
            st.session_state.lang = "en"

        placeholder = st.container()

        st.session_state.lang = st.selectbox(
            'Language',
            ('🇺🇸 en', '🇫🇷 fr'))[-2:]

        with placeholder:
            with open(os.path.join(os.getcwd(), f"generative_app/ui/{st.session_state.lang}/sidebar_intro.md"), "r") as sidebar_file:
                sidebar_content = sidebar_file.read()

            st.markdown(sidebar_content, unsafe_allow_html=True)

            _, c2, _ = st.columns([1, 1, 1])
            c2.image(os.path.join(os.getcwd(), f"generative_app/ui/bmc_qr.png"), use_column_width=True)

            with open(os.path.join(os.getcwd(), f"generative_app/ui/{st.session_state.lang}/sidebar_bmc.md"), "r") as sidebar_file:
                sidebar_content = sidebar_file.read()
            st.markdown(sidebar_content, unsafe_allow_html=True)
            st.divider()


            with open(os.path.join(os.getcwd(), f"generative_app/ui/{st.session_state.lang}/sidebar_dev_advice.md"), "r") as sidebar_file:
                sidebar_content = sidebar_file.read()

            with st.expander("👉 " + extract_markdown_title(sidebar_content)):
                _, c, _ = st.columns([0.5, 1, 0.5])
                c.image(os.path.join(os.getcwd(), f"generative_app/ui/profile.jpg"))
                st.markdown(sidebar_content, unsafe_allow_html=True)

            with open(os.path.join(os.getcwd(), f"generative_app/ui/{st.session_state.lang}/sidebar_ex.md"), "r") as sidebar_file:
                sidebar_content = sidebar_file.read()

            with st.expander("👉 " + extract_markdown_title(sidebar_content)):
                st.markdown(sidebar_content)