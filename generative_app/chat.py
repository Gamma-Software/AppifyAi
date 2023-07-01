from langchain.chains import LLMChain

import streamlit as st
from llm import parse

def generate_app(code:str, python_script_path: str):
    if not code:
        return
    with open(python_script_path, "w") as app_file:
        app_file.write(code)

def reset(python_script_path: str):
    if "messages" in st.session_state:
        st.session_state.messages.clear()
    st.session_state["messages"] = [
            {"role": "assistant", "content": "Hello! I'm 🤖ChatbotX designed to help you create a Streamlit App."},
            {"role": "assistant", "content": "here are the few commands to control me:\n\n/undo: undo the last instruction\n\n/reset: reset the app and the conversation\n\n/save: save the streamlit script in an independant app"},
            {"role": "assistant", "content": "I will generate the Streamlit App in the 🤖GeneratedApp page (see sidebar)"},
        ]
    generate_app("", python_script_path)

def setup(llm: LLMChain, python_script_path: str):
    if "generated" not in st.session_state:
        st.session_state["generated"] = [
            "Hey there, I'm here to help you update this page as you wish 🔍"
        ]
    if "past" not in st.session_state:
        st.session_state["past"] = ["Hey!"]
    if "input" not in st.session_state:
        st.session_state["input"] = ""
    if "stored_session" not in st.session_state:
        st.session_state["stored_session"] = []

    if "messages" not in st.session_state:
        reset(python_script_path)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    instruction = st.chat_input("Tell him what to do")
    if instruction:
        st.session_state.messages.append({"role": "user", "content": instruction})
        with st.chat_message("user"):
            st.markdown(instruction)

        # Process the instruction if the user did not enter a specific command
        check_command = check_commands(instruction, python_script_path)
        if not check_command[0] or check_command[1]:
            if check_command[1]:
                # If an error must be displayed
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    response = check_command[1]
                    message_placeholder.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            else:
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    with message_placeholder:
                        message_placeholder.write("⌛Processing... do not leave this page until I respond.")
                        st.session_state.last_code = open(python_script_path).read()
                        full_response_raw = llm.predict(question=instruction, python_code=st.session_state.last_code)
                        code, explanation = parse(full_response_raw)
                        message = ""
                        if code:
                            generate_app(code, python_script_path)
                            message = "\n".join([f"```python\n{code}\n```", explanation])
                            message_placeholder.markdown(message)
                        else:
                            message = explanation
                            message_placeholder.markdown(message)
                st.session_state.messages.append({"role": "assistant", "content": message})

def check_commands(instruction, python_script_path):
    if "/undo" in instruction:
        if "last_code" not in st.session_state:
            return False, "Nothing to undo"
        else:
            generate_app(st.session_state.last_code, python_script_path)
            return True, "Code reverted"
        return True, None
    if "/reset" in instruction:
        reset(python_script_path)
        return True, "Code resetted"
    if "/save" in instruction:
        print("save")
        return True, None
    return False, None
