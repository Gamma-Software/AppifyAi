import enum
import re
from langchain.chains import LLMChain
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from llm import parse
import llm
import asyncio
from auth.auth_connection import AuthSingleton
from templates.template_app import template_app

class CommandResult(enum.Enum):
    UNKNOWN = [0, "Unknown command"]
    NOTUNDO = [1, "Nothing to undo"]
    UNDO = [2, "Code reverted"]
    RESET = [3, "Code resetted"]
    SAVE = [4, "Code saved"]

class ChatBot:
    def __init__(self, user_id: int, username:str, python_script_path: str):
        self.python_script_path = python_script_path
        self.background_tasks = set()
        self.user_id = user_id
        self.username = username

    def apply_code(self, code:str):
        if code is None:
            return
        # apply 8 space indentation
        code = re.sub(r"^", " " * 8, code, flags=re.MULTILINE)

        # save code to database
        AuthSingleton().get_instance().set_code(self.user_id, code)

        # Save last code
        st.session_state.last_code = self.parse_code(open(self.python_script_path, "r").read())
        print(st.session_state.last_code)

        with open(self.python_script_path, "w") as app_file:
            app_file.write(template_app.format(code=code))

    @staticmethod
    def parse_code(code:str):
        from textwrap import dedent
        python_code = None
        pattern = r"#---start\n(.*?)#---end"
        python_code_match = re.search(pattern, code, re.DOTALL)
        print("code2:", python_code_match)
        if python_code_match:
            python_code = python_code_match.group(1)
            print("code", python_code)
            if python_code == "None":
                python_code = None
        # Remove the 8 space indentation
        if python_code:
            python_code = dedent(python_code)
        return python_code


    @staticmethod
    def check_commands(instruction) -> CommandResult or None:
        if "/undo" in instruction:
            if "last_code" not in st.session_state:
                return CommandResult.NOTUNDO
            else:
                return CommandResult.UNDO
        if "/reset" in instruction:
            return CommandResult.RESET
        if "/save" in instruction:
            return CommandResult.SAVE
        if "/" in instruction:
            return CommandResult.UNKNOWN
        return None

    def apply_command(self, command: CommandResult, chat_placeholder: DeltaGenerator):
        if command == CommandResult.UNKNOWN:
            chat_placeholder.error("Command unknown")
        if command == CommandResult.NOTUNDO:
            chat_placeholder.error("Nothing to undo")
        if command == CommandResult.UNDO:
            self.apply_code(st.session_state.last_code)
            chat_placeholder.info("Code reverted")
        if command == CommandResult.RESET:
            self.reset_chat()
        if command == CommandResult.SAVE:
            chat_placeholder.info("Download the file by clicking on the button below.\nYou can then run it with `streamlit run streamlit_app.py`")
            code = self.parse_code(open(self.python_script_path, "r").read())
            print(code)
            chat_placeholder.download_button(label="Download app", file_name= "streamlit_app.py",
                                             mime='text/x-python', data=code)

    def reset_chat(self):
        st.session_state["messages"] = {
            "message_0":
                {"role": "assistant",
                "content": f"""
                Hello {self.username}! I'm 🤖ChatbotX designed to help you create a Streamlit App.

                here are the few commands to control me:
                /undo: undo the last instruction
                /reset: reset the app
                /save: save the streamlit script in an independant app

                I will generate the Streamlit App in the Generate App tab (Find it in the sidebar menu)"""
                },
        }
        self.save_chat_history()
        st.session_state.chat_history = []
        self.apply_code("import streamlit as st\nst.write('Hello')")
        st.experimental_rerun()

    def add_message(self, role: str, content: str):
        idx = len(st.session_state.messages)
        st.session_state.messages.update({f"message_{idx}": {"role": role, "content": content}})

    def setup(self):
        # If this is the first time the chatbot is launched reset it and the code
        # Add saved messages
        st.session_state.messages = AuthSingleton().get_instance().get_message_history(self.user_id)

        if st.session_state.messages:
            for _, message in st.session_state.messages.items():
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        else:
            self.reset_chat()

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Setup user input
        if instruction := st.chat_input("Tell me what to do"):
            # Add user message to the chat
            self.add_message("user", instruction)
            # Process the instruction if the user did not enter a specific command
            user_message_placeholder = st.chat_message("user")
            assistant_message_placeholder = st.chat_message("assistant")

            if command := self.check_commands(instruction):
                user_message_placeholder.markdown(instruction)
                self.apply_command(command, assistant_message_placeholder)
                self.add_message("assistant", command.value[1])
            else:
                # If its not a command, process the instruction
                user_message_placeholder.markdown(instruction)
                with assistant_message_placeholder:
                    current_assistant_message_placeholder = st.empty()
                    #chain = llm.llm_chain(current_assistant_message_placeholder)
                    chain = llm.load_conversation_chain(current_assistant_message_placeholder)
                    message = ""
                    current_assistant_message_placeholder.info("⌛Processing")

                    # Wait for the response of the LLM and display a loading message in the meantime
                    try:
                        #llm_result = loop.run_until_complete(chain.apredict(question=instruction, python_code=st.session_state.last_code))
                        llm_result = chain({"question": instruction, "chat_history": st.session_state.chat_history, "python_code": st.session_state.last_code})
                    except Exception as e:
                        current_assistant_message_placeholder.error(f"Error...{e}")
                        raise
                    finally:
                        code, explanation = parse(llm_result["answer"])
                        # Apply the code if there is one and display the result
                        if code:
                            message = f"```python\n{code}\n```\n"
                            self.apply_code(code)
                        message += f"{explanation}"
                        current_assistant_message_placeholder.markdown(message)
                        st.session_state.chat_history.append((instruction, explanation))
                        self.add_message("assistant", message)
                        self.prune_chat_history()
                        self.save_chat_history()

    def prune_chat_history(self):
        # Make sure that the buffer history is not filled with too many messages (max 3)
        if len(st.session_state.chat_history) > 3:
            # Take the last 3 messages
            st.session_state.chat_history = st.session_state.chat_history[-3:]

    def save_chat_history(self):
        AuthSingleton().get_instance().set_message_history(self.user_id,  st.session_state.messages)
