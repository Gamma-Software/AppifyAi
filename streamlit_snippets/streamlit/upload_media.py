import streamlit as st

video = st.file_uploader("Upload video", type=["mov", "mp4", "avi"])
if video:
    st.video(video)
image = st.file_uploader("Upload image", type=["png", "jpeg", "jpg"])
if image:
    st.image(image)
