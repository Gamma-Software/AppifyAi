import enum
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
import chains.llm as llm
from auth.auth_connection import AuthSingleton
from utils.parser import parse_current_app
import ui.chat_init as chat_init
from chains.llm import parse
from ui.end_trial import (
    trial_title,
    thanks,
    pay,
    share,
    download,
    download_info,
    no_code,
)
from templates.template_app import init_app


class CommandResult(enum.Enum):
    UNKNOWN = [0, "Unknown command"]
    NOTUNDO = [1, "Nothing to undo"]
    UNDO = [2, "Code reverted"]
    RESET = [3, "Code resetted"]
    SAVE = [4, "Code saved"]


class ChatBot:
    def __init__(self, user_id: int, username: str, python_script_path: str):
        self.python_script_path = python_script_path
        self.background_tasks = set()
        self.user_id = user_id
        self.username = username
        self.auth = AuthSingleton().get_instance()
        self.user_role = self.auth.get_user_role(self.user_id)

    def append_code_history(self, code: str):
        """Store the code into the last_code session data"""
        if "last_code" not in st.session_state:
            st.session_state["last_code"] = []
        st.session_state.last_code.append(code)

    def get_code_history(self) -> str or None:
        """Get the last_code session data"""
        if "last_code" not in st.session_state:
            return None
        return st.session_state.last_code

    def pop_code_history(self):
        """Store the code into the last_code session data"""
        if "last_code" not in st.session_state:
            return None
        else:
            st.session_state.last_code.pop()

    def apply_code(self, code: str):
        if code is None:
            return
        # save code to database
        self.auth.set_code(self.user_id, code)
        self.append_code_history(code)

    @staticmethod
    def check_commands(instruction: str) -> CommandResult or None:
        if instruction.startswith("/undo"):
            if "messages" not in st.session_state:
                return CommandResult.NOTUNDO
            elif len(st.session_state["messages"]) <= 2:
                # If only the greetings of the bot and the current command is there we cannot undo
                return CommandResult.NOTUNDO
            else:
                return CommandResult.UNDO
        if instruction.startswith("/reset"):
            return CommandResult.RESET
        if instruction.startswith("/save"):
            return CommandResult.SAVE
        if instruction.startswith("/"):
            return CommandResult.UNKNOWN
        return None

    def apply_command(self, command: CommandResult, chat_placeholder: DeltaGenerator):
        if command == CommandResult.UNKNOWN:
            chat_placeholder.error("Command unknown")
        if command == CommandResult.NOTUNDO:
            chat_placeholder.error("Nothing to undo")
        if command == CommandResult.UNDO:
            # remove the last code
            self.pop_code_history()
            self.apply_code(st.session_state.last_code[-1])
            # remove the last 4 keys
            if len(st.session_state.messages) > 1:
                for _ in range(min(len(st.session_state.messages), 3)):
                    st.session_state.messages.popitem()
                self.save_chat_history_to_database()
            if "chat_history" in st.session_state:
                if len(st.session_state.chat_history) > 0:
                    st.session_state.chat_history = st.session_state.chat_history[:-1]
            st.experimental_rerun()
        if command == CommandResult.RESET:
            with st.spinner("Resetting..."):
                self.reset_chat()
                chat_placeholder.info("Code resetted")
                st.experimental_rerun()
        if command == CommandResult.SAVE:
            code = self.get_code_history()[-1]
            if code is None or code == init_app:
                chat_placeholder.error("No code to save")
                return
            chat_placeholder.info(
                "Download the file by clicking on the button below.\n"
                "You can then run it with `streamlit run streamlit_app.py`"
            )
            chat_placeholder.download_button(
                label="Download app",
                file_name="streamlit_app.py",
                mime="text/x-python",
                data=code,
            )

    def reset_chat(self):
        print("resetting chat")
        st.session_state["messages"] = {
            "message_0": {
                "role": "assistant",
                "content": chat_init.message_en.format(name=self.username)
                if st.session_state.lang == "en"
                else chat_init.message_fr.format(name=self.username),
            },
        }
        self.save_chat_history_to_database()
        st.session_state.chat_history = []
        self.apply_code(init_app)

    def add_message(self, role: str, content: str):
        idx = len(st.session_state.messages)
        st.session_state.messages.update(
            {f"message_{idx}": {"role": role, "content": content}}
        )

    def end_of_trial(self):
        st.title(trial_title[1 if st.session_state.lang == "fr" else 0])
        st.markdown(thanks[1 if st.session_state.lang == "fr" else 0])
        st.success(pay[1 if st.session_state.lang == "fr" else 0])
        st.markdown(share[1 if st.session_state.lang == "fr" else 0])
        code = parse_current_app(open(self.python_script_path, "r").read())
        if code:
            st.header(download[1 if st.session_state.lang == "fr" else 0])
            c1, c2 = st.columns([1, 0.5])
            c1.markdown(download_info[1 if st.session_state.lang == "fr" else 0])
            if c2.download_button(
                label=download[1 if st.session_state.lang == "fr" else 0],
                file_name="streamlit_app.py",
                mime="text/x-python",
                data=code,
            ):
                st.balloons()
            # TODO add tutorial on how to deploy on web
            # TODO download already compiled app (like .exe)
        else:
            st.warning(no_code[1 if st.session_state.lang == "fr" else 0])

    def setup(self):
        if self.user_role == "guest" and self.check_tries_exceeded():
            self.end_of_trial()
            return

        # If this is the first time the chatbot is launched reset it and the code
        # Add saved messages
        st.session_state.messages = self.auth.get_message_history(self.user_id)

        if not st.session_state.messages:
            self.reset_chat()

        # Process the message history and display it
        # And read and store the code history generated by the bot
        for _, message in st.session_state.messages.items():
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    code, explanation = parse(message["content"])
                    if code is not None:
                        message = f"```python\n{code}\n```"
                        ex = st.expander("Code")
                        ex.code(code)
                        self.append_code_history(code)
                    st.markdown(explanation)
                else:
                    st.markdown(message["content"])

        # In case the chat has not been reset or
        # or the no code has been generated yet
        if "last_code" not in st.session_state:
            st.session_state["last_code"] = [init_app]

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        if "tries" not in st.session_state:
            st.session_state.tries = self.auth.get_tries(self.user_id)
        self.setup_chat()

    def setup_chat(self):
        # Setup user input
        if instruction := st.chat_input("Tell me what to do, or ask me a question"):
            if self.user_role == "guest":
                tries_left = st.secrets["tries"] - st.session_state.tries
                if tries_left <= 0:
                    print("end of trial")
                    st.experimental_rerun()
            # Add user message to the chat
            self.add_message("user", instruction)
            # Process the instruction if the user did not enter a specific command
            user_message_placeholder = st.chat_message("user")
            assistant_message_placeholder = st.chat_message("assistant")

            if command := self.check_commands(instruction):
                user_message_placeholder.write(instruction)
                self.apply_command(command, assistant_message_placeholder)
                self.add_message("assistant", command.value[1])
                self.save_chat_history_to_database()
            else:
                # If its not a command, process the instruction
                user_message_placeholder.markdown(instruction)
                with assistant_message_placeholder:
                    current_assistant_message_placeholder = st.empty()
                    chain = llm.load_conversation_chain(
                        current_assistant_message_placeholder,
                        st.session_state.openai_api_key,
                    )
                    message = ""

                    with st.spinner(
                        "⌛Processing... Please keep this page open until the end of my response."
                    ):
                        # Wait for the response of the LLM and display a
                        # loading message in the meantime
                        try:
                            print("calling chain")
                            llm_result = chain(
                                {
                                    "question": instruction,
                                    "chat_history": st.session_state.chat_history,
                                    "python_code": st.session_state.last_code[-1],
                                }
                            )
                        except Exception as e:
                            current_assistant_message_placeholder.error(f"Error...{e}")
                            raise

                    code = llm_result["code"]
                    explanation = llm_result["explanation"]
                    security_rules_offended = llm_result["revision_request"]
                    # Apply the code if there is one and display the result
                    if code is not None:
                        message = f"```python\n{code}\n```"
                        if not security_rules_offended:
                            self.apply_code(code)
                    message += explanation
                    container = current_assistant_message_placeholder.container()
                    ex = container.expander("Code")
                    ex.code(code)
                    container.markdown(explanation)
                    if security_rules_offended:
                        container.warning(
                            "Your instruction does not comply with our security measures"
                            "(code generated will not be populated). See the docs for "
                            "more information."
                        )
                    if self.user_role == "guest":
                        st.session_state.tries = self.auth.increment_tries(self.user_id)
                        tries_left = st.secrets["tries"] - st.session_state.tries
                        if tries_left == 0:
                            container.error("You have 0 try left.")
                        elif tries_left == 1:
                            container.warning("You have 1 try left.")
                        else:
                            container.info(f"You have {tries_left} tries left.")
                    st.session_state.chat_history.append((instruction, explanation))
                    self.add_message("assistant", message)
                    self.save_chat_history_to_database()

    def check_tries_exceeded(self) -> bool:
        tries = self.auth.get_tries(self.user_id)
        if tries < st.secrets["tries"]:
            return False
        return True

    def prune_chat_history(self):
        # Make sure that the buffer history is not filled with too many messages (max 3)
        if len(st.session_state.chat_history) > 3:
            # Take the last 3 messages
            st.session_state.chat_history = st.session_state.chat_history[-3:]

    def save_chat_history_to_database(self):
        print("saving chat history")
        self.auth.set_message_history(self.user_id, st.session_state.messages)
