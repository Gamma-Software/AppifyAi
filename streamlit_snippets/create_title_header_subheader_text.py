import streamlit as st


def create_title(text, element_placeholder):
    element_placeholder.title(text)


def create_header(text, element_placeholder):
    element_placeholder.header(text)


def create_subheader(text, element_placeholder):
    element_placeholder.subheader(text)


def create_text(text, element_placeholder):
    element_placeholder.text(text)


# First create placeholders for each element so that we can order them then reference them later
title = st.empty()
header = st.empty()
subheader = st.empty()
text = st.empty()

# Now create the elements no matter the order because the order is defined above
create_text("This is a text", text)
create_title("This is a title", title)
create_header("This is a header", header)
create_subheader("This is a subheader", subheader)
