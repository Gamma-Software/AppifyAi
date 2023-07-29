import re
import streamlit as st
from langchain.llms import OpenAI

st.title("My custom AI application")

openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")


def process_llm(template, data):
    # Instantiate LLM model
    llm = OpenAI(
        model_name="text-davinci-003", openai_api_key=openai_api_key, temperature=0
    )
    prompt_query = template.format(**dict(data))
    # Run LLM model
    response = llm(prompt_query)
    # Print results
    return st.markdown(response)


with st.sidebar.expander("Prompt"):
    st.write("Please write the prompt template here. Use {variable} to add a variable.")
    prompt_template = st.text_area(
        "Enter the prompt",
        "Translate the following sentence to {language}: {sentence}",
    )
    variables = re.findall(r"\{([^}]+)\}", prompt_template)

with st.form("myform"):
    form_data = []
    for variable in variables:
        form_data.append(
            (variable, st.text_input(f"Enter {variable}:", "", key=variable))
        )
    submitted = st.form_submit_button("Submit")
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
    elif submitted:
        process_llm(prompt_template, form_data)
