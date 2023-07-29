import streamlit as st


def center_text_element(text: str, element_type: str, element_placeholder):
    """Center a text element in streamlit where the element type is one of title, header, subheader
    or text
    Args:
        text (str): Text to center
        element_type (str): could be a title, header, subheader or text
        element_placeholder: Streamlit placeholder to put the element in
    """
    if element_type not in ["title", "header", "subheader", "text"]:
        raise ValueError("element_type must be one of title, header, subheader or text")
    element_type_map = {
        "title": "h1",
        "header": "h2",
        "subheader": "h3",
        "text": "p",
    }
    # Use unsafe_allow_html to allow modification of the CSS style
    element_placeholder.markdown(
        "<{type} style='text-align: center;'>{text}</{type}>".format(
            text=text, type=element_type_map[element_type]
        ),
        unsafe_allow_html=True,
    )


# First create placeholders for each element so that we can order them then reference them later
centered_text = st.empty()

# Now create the elements no matter the order because the order is defined above
center_text_element("This is a centered text", "text", centered_text)
