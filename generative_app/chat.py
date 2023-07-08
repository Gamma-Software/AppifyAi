import enum

from langchain.chains import LLMChain
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from llm import parse
import llm
import asyncio
from templates.template_app import template_app

class CommandResult(enum.Enum):
    UNKNOWN = [0, "Unknown command"]
    NOTUNDO = [1, "Nothing to undo"]
    UNDO = [2, "Code reverted"]
    RESET = [3, "Code resetted"]
    SAVE = [4, "Code saved"]

class ChatBot:
    def __init__(self, python_script_path: str):
        self.python_script_path = python_script_path
        self.background_tasks = set()

    @staticmethod
    def apply_code(code:str, python_script_path):
        if code is None:
            return
        with open(python_script_path, "w") as app_file:
            app_file.write(template_app.format(code=code))

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
        return None

    def apply_command(self, command: CommandResult, chat_placeholder: DeltaGenerator):
        if command == CommandResult.NOTUNDO:
            chat_placeholder.error("Nothing to undo")
        if command == CommandResult.UNDO:
            self.apply_code(st.session_state.last_code, self.python_script_path)
            chat_placeholder.info("Code reverted")
        if command == CommandResult.RESET:
            self.reset_chat()
        if command == CommandResult.SAVE:
            chat_placeholder.info("Download the file by clicking on the button below.\nYou can then run it with `streamlit run streamlit_app.py`")
            chat_placeholder.download_button("Download app", st.session_state.last_code, "streamlit_app.py")

    def reset_chat(self):
        st.session_state["messages"] = [
            {"role": "assistant",
             "content": """
             Hello! I'm 🤖ChatbotX designed to help you create a Streamlit App.

             here are the few commands to control me:
             /undo: undo the last instruction
             /reset: reset the app
             /save: save the streamlit script in an independant app

             I will generate the Streamlit App here [Sandbox](https://chatbotx-client1.pival.fr/)"""
             },
        ]
        st.session_state.chat_history = []
        self.apply_code("st.write('Hello')", self.python_script_path)
        st.experimental_rerun()

    def setup(self, reset_at_start: bool):
        # If this is the first time the chatbot is launched reset it and the code
        if reset_at_start:
            self.reset_chat()

        # Add cached messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Setup user input
        if instruction := st.chat_input("Tell me what to do"):
            # Save last code
            st.session_state.last_code = open(self.python_script_path).read()
            # Add user message to the chat
            st.session_state.messages.append({"role": "user", "content": instruction})
            # Process the instruction if the user did not enter a specific command
            user_message_placeholder = st.chat_message("user")
            assistant_message_placeholder = st.chat_message("assistant")

            if command := self.check_commands(instruction):
                user_message_placeholder.markdown(instruction)
                self.apply_command(command, assistant_message_placeholder)
                st.session_state.messages.append({"role": "assistant", "content": command.value[1]})
            else:
                # If its not a command, process the instruction
                user_message_placeholder.markdown(instruction)
                with assistant_message_placeholder:
                    current_assistant_message_placeholder = st.empty()
                    #chain = llm.llm_chain(current_assistant_message_placeholder)
                    chain = llm.load_conversation_chain(current_assistant_message_placeholder)
                    message = ""

                    # Wait for the response of the LLM and display a loading message in the meantime
                    loop = asyncio.new_event_loop()
                    try:
                        #llm_result = loop.run_until_complete(chain.apredict(question=instruction, python_code=st.session_state.last_code))
                        llm_result = chain({"question": instruction, "chat_history": st.session_state.chat_history, "python_code": st.session_state.last_code})
                    except Exception as e:
                        current_assistant_message_placeholder.error(f"Error...{e}")
                        raise
                    finally:
                        code, explanation = parse(llm_result["answer"])
                        print(explanation)
                        # Apply the code if there is one and display the result
                        if code:
                            message = f"```python\n{code}\n```\n"
                            self.apply_code(code, self.python_script_path)
                        message += f"{explanation}"
                        current_assistant_message_placeholder.markdown(message)
                        st.session_state.chat_history.append((instruction, explanation))
                        st.session_state.messages.append({"role": "assistant", "content": message})
                        self.prune_chat_history()

    def prune_chat_history(self):
        # Make sure that the buffer history is not filled with too many messages (max 3)
        if len(st.session_state.chat_history) > 3:
            # Take the last 3 messages
            st.session_state.chat_history = st.session_state.chat_history[-3:]

