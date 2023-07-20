import streamlit as st
import base64
from typing import Tuple, List

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def load_backgound(name: str, filepath: str):
    if name not in st.session_state:
        st.session_state[name] = get_base64(filepath)

def load_backgounds(datas: List[Tuple[str, str]]):
    print("Loading backgrounds...")
    for name, filepath in datas:
        if name not in st.session_state:
            print(f"Loading {name} from {filepath}")
            st.session_state[name] = get_base64(filepath)

def set_sidebar_bg(name: str):
    if name not in st.session_state:
        raise ValueError(f"Sidebar background {name} not loaded")
    sidebar_bg_img = f"""
      <style>
      [data-testid="stSidebar"] > div:first-child {{
      background-image: url("data:image/png;base64,{st.session_state[name]}");
      background-position: center;
      }}
      </style>
      """
    st.markdown(sidebar_bg_img,unsafe_allow_html=True,)

# TODO Too long to process for now
def set_background(name: str):
    if name not in st.session_state:
        raise ValueError(f"Background {name} not loaded")
    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
    background-image:url("data:image/png;base64,{st.session_state[name]}");
    background-size: cover;
    background-attachment: local;
    }}

    [data-testid="stHeader"] {{
    background: rgba(0,0,0,0);
    }}

    [data-testid="stToolbar"] {{
    right: 2rem;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)