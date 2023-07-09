import streamlit as st
import extra_streamlit_components as stx
import datetime
from auth_connection import Auth
st.write("# Cookie Manager")

auth = Auth(5)

c1, c2, c3 = st.columns(3)

with c1:
    st.subheader("User session:")
    user_id = int(st.number_input("user_id", key="0"))

    if st.button("Add user session"):
        auth.add_user_session(user_id)
    if st.button("Extend user session"):
        auth.extend_user_session(user_id, auth.cookies.get('user_token'))
    if st.button("Remove user session"):
        auth.remove_user_session(user_id)

    if st.button("Can autologin ?"):
        st.write(auth.can_auto_login(auth.cookies.get('user_token')))
with c2:
    st.subheader("Get user token:")
    if st.button("Get user token"):
        st.write(auth.cookies.get('user_token'))