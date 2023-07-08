from hydralit import HydraApp
import hydralit_components as hc

from login_app import LoginApp
from signup import SignUpApp
from chatbotx import ChatBotApp
from load_app import LoadingApp
import sidebar

import streamlit as st

#Only need to set these here as we are add controls outside of Hydralit, to customise a run Hydralit!
st.set_page_config(
    #page_title="ChatbotX",
    #page_icon="🤖",
    layout="wide",
    initial_sidebar_state=sidebar.sidebar_init_state,
    menu_items={
        "Report a bug": "https://github.com/Gamma-Software/ChatbotX/issues",
        "About": """
            # ChatbotX
            Transform conversations into stunning web apps. Dynamic code generation + intuitive interface. Unleash your creativity effortlessly. Use the power of GPT OpenAI LLM and Langchain.

            # Author
            [Valentin Rudloff](https://valentin.pival.fr/) is a French engineer that loves to learn and build things with code.
            [☕ Buy me a coffee](https://www.buymeacoffee.com/valentinrudloff)

            Go to the GitHub repo to learn more about the project. https://github.com/Gamma-Software/ChatbotX
            """,
    },
)

if __name__ == '__main__':
    over_theme = {'txc_inactive': '#FFFFFF','menu_background':'#26272f','txc_active':'white','option_active':'#3e404f'}
    #this is the host application, we add children to it and that's it!
    app = HydraApp(
        title='ChatBotX',
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


    #we want to have secure access for this HydraApp, so we provide a login application
    #optional logout label, can be blank for something nicer!
    app.add_app("Login", LoginApp(title='Login'), is_home=True, is_login=True)

    #we have added a sign-up app to demonstrate the ability to run an unsecure app
    #only 1 unsecure app is allowed
    app.add_app("Signup", icon="🛰️", app=SignUpApp(title='Signup'), is_unsecure=True)

    #specify a custom loading app for a custom transition between apps, this includes a nice custom spinner
    app.add_loader_app(LoadingApp(delay=1))

    #we can inject a method to be called everytime a user logs out
    #---------------------------------------------------------------------
    @app.logout_callback
    def mylogout_cb():
        print('I was called from Hydralit at logout!')
    #---------------------------------------------------------------------

    #we can inject a method to be called everytime a user logs in
    #---------------------------------------------------------------------
    @app.login_callback
    def mylogin_cb():
        print('I was called from Hydralit at login!')
    #---------------------------------------------------------------------

    #if we want to auto login a guest but still have a secure app, we can assign a guest account and go straight in
    #app.enable_guest_access()

    #check user access level to determine what should be shown on the menu
    user_access_level, username = app.check_access()

    # If the menu is cluttered, just rearrange it into sections!
    # completely optional, but if you have too many entries, you can make it nicer by using accordian menus
    if user_access_level > 0:
        from sandboxes import APPS
        sandbox_app = [item for item in APPS if item[0] == "_".join([username, str(user_access_level)])]
        if len(sandbox_app) == 0:
            raise ValueError("No sandbox found for user {} with access level {}".format(username, user_access_level))
        title = "Generated App"
        _, path_to_script, app_to_add = sandbox_app[0]

        #add all your application classes here
        print(path_to_script)
        app.add_app("ChatbotX", icon="💬", app=ChatBotApp(title="ChatbotX", generative_app_path=path_to_script))

        #add all your application classes here
        app.add_app(title, icon="💫", app=app_to_add)
        complex_nav = {
            'ChatbotX': ['ChatbotX'],
        }
        complex_nav.update({title: [title]})
    else:
        complex_nav = {
            'ChatbotX': ['ChatbotX'],
        }


    #and finally just the entire app and all the children.
    app.run(complex_nav)


    #print user movements and current login details used by Hydralit
    #---------------------------------------------------------------------
    # user_access_level, username = app.check_access()
    # prev_app, curr_app = app.get_nav_transition()
    # print(prev_app,'- >', curr_app)
    # print(int(user_access_level),'- >', username)
    # print('Other Nav after: ',app.session_state.other_nav_app)
    #---------------------------------------------------------------------

