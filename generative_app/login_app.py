import time
from typing import Dict, Union
import shutil
from pathlib import Path
import streamlit as st
from auth.auth_connection import Auth, generate_user_session_token
from hydralit import HydraHeadApp
from streamlit.delta_generator import DeltaGenerator


class LoginApp(HydraHeadApp):
    """
    This is an example login application to be used to secure access within a HydraApp streamlit application.
    This application implementation uses the allow_access session variable and uses the do_redirect method if the login check is successful.

    """

    def __init__(self, title = '', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title
        self.auth = Auth()


    def run(self) -> None:
        """
        Application entry point.
        """

        st.markdown("<h1 style='text-align: center;'>Login to ChatbotX 💫</h1>", unsafe_allow_html=True)

        c1,c2,c3, = st.columns([2,2,2])

        form_data, login_message_placeholder = self._create_login_form(c2)

        pretty_btn = """
        <style>
        div[class="row-widget stButton"] > button {
            width: 100%;
        }
        </style>
        <br><br>
        """
        c2.markdown(pretty_btn,unsafe_allow_html=True)

        if form_data['submitted']:
            self._do_login(form_data, login_message_placeholder)


    def _create_login_form(self, parent_container) -> Union[Dict, DeltaGenerator]:

        login_form = parent_container.form(key="login_form")

        login_message = parent_container.empty()

        form_state = {}
        form_state['username'] = login_form.text_input('Username')
        form_state['password'] = login_form.text_input('Password',type="password")
        form_state['submitted'] = login_form.form_submit_button('Login')

        parent_container.markdown("<p style='text-align: center;'>Guest login -> joe & joe</p>", unsafe_allow_html=True)

        if parent_container.button('Sign Up',key='signupbtn'):
            # set access level to a negative number to allow a kick to the unsecure_app set in the parent
            self.set_access(-1, 'guest')

            #Do the kick to the signup app
            self.do_redirect()

        return form_state, login_message


    def _do_login(self, form_data, msg_container) -> None:
        access_level = self._check_login(form_data)

        if access_level > 0:
            with msg_container:
                st.success(f"✔️ Login success")
                time.sleep(1)
                with st.spinner("now redirecting to application...."):
                    time.sleep(1)

                    #access control uses an int value to allow for levels of permission that can be set for each user, this can then be checked within each app seperately.
                    self.set_access(access_level, form_data['username'])

                    # Seed the sandbox if not already done
                    self.seed_sandbox(access_level, form_data['username'])

                    # Add user sesssion
                    self.auth.add_user_session(access_level)

                    #Do the kick to the home page
                    self.do_redirect()
        else:
            self.session_state.allow_access = 0
            self.session_state.current_user = None
            with msg_container:
                st.error(f"❌ Login unsuccessful, 😕 please check your username and password and try again.")


    def _check_login(self, login_data) -> int:
        #this method returns a value indicating the success of verifying the login details provided and the permission level, 1 for default access, 0 no access etc.
        if login_data['username'] == 'joe' or login_data['password'] == 'joe':
            return 1
        if self.auth.check_user(login_data['username'], login_data['password']):
            return self.auth.get_user_id(login_data['username'], login_data['password'])
        return -1

    def seed_sandbox(self, level, username):
        # Check if the sandbox exists
        sandboxes_path = Path(__file__).parent / 'sandboxes'
        template_sandbox_app = Path(__file__).parent / 'templates' / 'app.py'
        sandbox_user_path = sandboxes_path / f"{username}_{level}.py"
        if sandboxes_path.exists():
            if not sandbox_user_path.exists():
                # Create the sandbox app
                shutil.copyfile(src=template_sandbox_app, dst=sandbox_user_path)
                print(f"Created sandbox app for {username} at {sandbox_user_path}")