import time
import os
from typing import Dict
import streamlit as st
from hydralit import HydraHeadApp


class SignUpApp(HydraHeadApp):
    """
    This is an example signup application to be used to secure access within a HydraApp streamlit application.

    This application is an example of allowing an application to run from the login without requiring authentication.

    """

    def __init__(self, title = '', **kwargs):
        self.__dict__.update(kwargs)
        self.title = title


    def run(self) -> None:
        """
        Application entry point.

        """

        st.markdown("<h1 style='text-align: center;'>Secure Hydralit Signup</h1>", unsafe_allow_html=True)

        pretty_btn = """
        <style>
        div[class="row-widget stButton"] > button {
            width: 100%;
        }
        </style>
        <br><br>
        """
        c1,c2,c3, = st.columns([2,2,2])
        c2.markdown(pretty_btn,unsafe_allow_html=True)

        if 'MSG' in os.environ.keys():
            st.info(os.environ['MSG'])

        form_data = self._create_signup_form(c2)

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
            self._do_signup(form_data, c2)


    def _create_signup_form(self, parent_container) -> Dict:

        login_form = parent_container.form(key="login_form")

        form_state = {}
        form_state['username'] = login_form.text_input('Username')
        form_state['password'] = login_form.text_input('Password',type="password")
        form_state['password2'] = login_form.text_input('Confirm Password',type="password")
        #form_state['access_level'] = login_form.selectbox('Example Access Level',(1,2))
        form_state['submitted'] = login_form.form_submit_button('Sign Up')

        if parent_container.button('Login',key='loginbtn'):
            # set access level to a negative number to allow a kick to the unsecure_app set in the parent
            self.set_access(0, None)

            #Do the kick to the signup app
            self.do_redirect()

        return form_state

    def _do_signup(self, form_data, msg_container) -> None:
        if form_data['submitted'] and (form_data['password'] != form_data['password2']):
            st.error('Passwords do not match, please try again.')
        else:
            with st.spinner("🤓 now redirecting to login...."):
                self._save_signup(form_data)
                time.sleep(2)

                #access control uses an int value to allow for levels of permission that can be set for each user, this can then be checked within each app seperately.
                self.set_access(0, None)

                #Do the kick back to the login screen
                self.do_redirect()

    def _save_signup(self, signup_data):
        #get the user details from the form and save somehwere

        #signup_data
        # this is the data submitted

        #just show the data we captured
        signup_data['access_level'] = 0 # Should be generated based on the user index
        what_we_got = f"""
        captured signup details: \n
        username: {signup_data['username']} \n
        password: {signup_data['password']} \n
        access level: {signup_data['access_level']} \n
        """

        st.write(what_we_got)

