import streamlit as st


def center_text_element(text, element_type, element_placeholder):
    """Center a text element in streamlit

    Args:
        text (str): Text to center
        element_type (str): could be a title, header, subheader or text
        element_placeholder: the placeholder to put the element in
    """
    if element_type not in ["title", "header", "subheader", "text"]:
        raise ValueError("element_type must be one of title, header, subheader or text")
    element_type_map = {
        "title": "h1",
        "header": "h2",
        "subheader": "h3",
        "text": "p",
    }
    element_placeholder.markdown(
        "<{type} style='text-align: center;'>{text}</{type}>".format(
            text=text, type=element_type_map[element_type]
        ),
        unsafe_allow_html=True,
    )


def center_element(element, element_placeholder, *args, **kwargs):
    """Center an element in streamlit

    Args:
        element (str): the streamlit element to center
        element_placeholder: the placeholder to put the element in
    """
    _, c, _ = element_placeholder.columns([1, 1, 1])
    with c:
        element(*args, **kwargs)


# First create placeholders for each element so that we can order them then reference them later
centered_text = st.empty()
centered_button = st.empty()

# Now create the elements no matter the order because the order is defined above
center_text_element("This is a centered text", "text", centered_text)
center_element(st.button, centered_button, "Centered Button", key="centered_button")

# You can now check the button status in the session state
if st.session_state["centered_button"]:
    st.write("Button clicked!")
