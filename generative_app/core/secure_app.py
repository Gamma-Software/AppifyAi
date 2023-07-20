from hydralit import HydraApp

from app_pages.login_app import LoginApp
from app_pages.signup import SignUpApp
from app_pages.about import About
from app_pagesa.ppifyai import ChatBotApp
from app_pages.load_app import LoadingApp
from app_pages.user_guide import UserGuide
import sidebar
from version import VERSION

import os
import re
from utils.parser import parse_current_app
from templates.template_app import template_app
from auth.auth_connection import AuthSingleton

import streamlit as st

#Only need to set these here as we are add controls outside of Hydralit, to customise a run Hydralit!
st.set_page_config(
    page_title="AppifyAi",
    #page_icon="🤖",
    layout="wide",
    initial_sidebar_state=sidebar.sidebar_init_state,
    menu_items={
        "Report a bug": "https://github.com/Gamma-Software/AppifyAi/issues",
        "About": f"""
            # AppifyAi - {VERSION}
            Transform conversations into stunning web apps. Dynamic code generation + intuitive interface. Unleash your creativity effortlessly. Use the power of GPT OpenAI LLM and Langchain.

            # Author
            [Valentin Rudloff](https://valentin.pival.fr/) is a French engineer that loves to learn and build things with code.
            [☕ Buy me a coffee](https://www.buymeacoffee.com/valentinrudloff)

            # Security measures
            The chatbot will never apply generated codes that:
            - Upload files
            - Execute any files or commands based on user input

            Go to the GitHub repo to learn more about the project. https://github.com/Gamma-Software/AppifyAi
            """,
    },
)

if __name__ == '__main__':
    over_theme = {'txc_inactive': '#FFFFFF','menu_background':'#26272f','txc_active':'white','option_active':'#3e404f'}
    #this is the host application, we add children to it and that's it!
    app = HydraApp(
        title='AppifyAi',
        favicon="🤖",
        #hide_streamlit_markers=hide_st,
        #add a nice banner, this banner has been defined as 5 sections with spacing defined by the banner_spacing array below.
        #use_banner_images=["./resources/hydra.png",None,{'header':"<h1 style='text-align:center;padding: 0px 0px;color:grey;font-size:200%;'>Secure Hydralit Explorer</h1><br>"},None,"./resources/lock.png"],
        #banner_spacing=[5,30,60,30,5],
        nav_container=st.sidebar,
        use_navbar=True,
        navbar_sticky=False,
        navbar_animation=False,
        navbar_theme=over_theme
    )

    # Authentication instance
    auth = AuthSingleton().get_instance()

    #we want to have secure access for this HydraApp, so we provide a login application
    #optional logout label, can be blank for something nicer!
    app.add_app("About", About(title='About'), is_unsecure=True)
    app.add_app("Logout", LoginApp(title='Login'), is_home=True, is_login=True)
    app.add_app("User Guide", UserGuide(title='User Guide'), icon="📜", is_unsecure=True)
    app.add_app("Signup", icon="🛰️", app=SignUpApp(title='Signup'), is_unsecure=True)
    app.add_loader_app(LoadingApp(delay=1))

    #check user access level to determine what should be shown on the menu
    user_access_level, username = app.check_access()

    #we can inject a method to be called everytime a user logs out
    #---------------------------------------------------------------------
    @app.logout_callback
    def mylogout_cb():
        if user_access_level:
            print('Remove user session of user {} with access level {}'.format(username, user_access_level))
            auth.remove_user_session(user_access_level)
    #---------------------------------------------------------------------

    #we can inject a method to be called everytime a user logs in
    #---------------------------------------------------------------------
    @app.login_callback
    def mylogin_cb():
        pass
    #---------------------------------------------------------------------

    #if we want to auto login a guest but still have a secure app, we can assign a guest account and go straight in
    #app.enable_guest_access()

    # If the menu is cluttered, just rearrange it into sections!
    # completely optional, but if you have too many entries, you can make it nicer by using accordian menus
    path_to_script = ""
    if user_access_level == 1:
        complex_nav = {
            'About': ['About']
        }
    elif user_access_level > 0:
        sandboxe_name = "_".join([username, str(user_access_level)])

        # Dynamically import the sandbox
        import importlib
        path_to_script = os.path.join(os.getcwd(), 'generative_app', 'sandboxes', f"{sandboxe_name}.py")
        spec = importlib.util.spec_from_file_location(f"{username}_{user_access_level}", path_to_script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        app_to_add = module.App("Generated App")

        #if path not in sys.path:
        #    sys.path.append(path)
        #print(sys.path)
        title =  f"{username} - Generated App"
        #app_to_add = importlib.import_module(f"{sandboxe_name}", "../..").App("Generated App")

        #add all your application classes here
        app.add_app("AppifyAi", icon="💬", app=ChatBotApp(title="AppifyAi", generative_app_path=path_to_script))

        #add all your application classes here
        app.add_app(title, icon="💫", app=app_to_add)
        complex_nav = {
            'AppifyAi': ['AppifyAi'],
        }
        complex_nav.update({title: [title]})
        complex_nav.update({'User Guide': ['User Guide']})
    else:
        complex_nav = {
            'User Guide': ['User Guide']
        }


    #and finally just the entire app and all the children.
    app.run(complex_nav)


    #print user movements and current login details used by Hydralit
    #---------------------------------------------------------------------
    # user_access_level, username = app.check_access()
    # print(int(user_access_level),'- >', username)

    prev_app, curr_app = app.get_nav_transition()
    print(prev_app,'- >', curr_app)
    if path_to_script != "":
        if curr_app == f"{username} - Generated App":
            #  Current code
            with open(path_to_script, "r") as app_file:
                current_code = parse_current_app(app_file.read())

            code_generated = auth.get_code(user_access_level)
            if code_generated is not None:
                if current_code.split() != code_generated.split():
                    print("Applying generated code...")
                    with st.spinner("Applying generated code..."):
                        with open(path_to_script, "w") as app_file:
                            # Indent code
                            code_generated = re.sub(r"^", " " * 8, code_generated, flags=re.MULTILINE)
                            app_file.write(template_app.format(code=code_generated))
                        # Reload app
                        st.experimental_rerun()
    # print('Other Nav after: ',app.session_state.other_nav_app)
    #---------------------------------------------------------------------
