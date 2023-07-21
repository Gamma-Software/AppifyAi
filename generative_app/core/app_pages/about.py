import os
import streamlit as st
from hydralit import HydraHeadApp


class About(HydraHeadApp):
    def __init__(self, title="", **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self) -> None:
        self.setup_sidebar()

        if st.button("Go back to login"):
            self.set_access(0, "guest")
            self.do_redirect()

        user_guide_tab, demo_tab, dev = st.tabs(
            ["What is AppifyAi ?", "Demonstrations", "More about the developer"]
        )
        with user_guide_tab:
            with open(
                os.path.join(
                    os.getcwd(),
                    f"generative_app/core/ui/{st.session_state.lang}/about.md",
                ),
                "r",
            ) as about_file:
                about = about_file.read()
            st.markdown(about)

        with demo_tab:
            with st.expander("Simple conversation"):
                st.write(
                    "This is a simple conversation showcasing the bot history capabilities. The bot"
                    "understands the context of the conversation and can better interact with you"
                    "and what you are thinking."
                )
                st.image("demo/simple_conversation.png")
            with st.expander("GPX reader"):
                st.write(
                    "This example shows how the bot is capable to understand the user's intent"
                    " as it generated errors in the reading of the GPX file. The user questioned"
                    "him if it know the format asked for an gpx example and use this knowledge"
                    " to update the script."
                )
                st.image("demo/gpx_reader.png")
            with st.expander("Camera input demo"):
                st.video("demo/camera_input_demo.mov")
            with st.expander("Detect and crop faces"):
                st.video("demo/detect_crop_faces.mov")
            with st.expander("Data stats"):
                st.video("demo/complex_example.mov")

        with dev:
            st.title("Founder and Developer")
            st.image(
                os.path.join(os.getcwd(), "generative_app/core/ui/profile_round.png")
            )
            with open(
                os.path.join(
                    os.getcwd(),
                    f"generative_app/core/ui/{st.session_state.lang}/about_dev.md",
                ),
                "r",
            ) as about_file:
                about = about_file.read()
            st.markdown(about)

    def setup_sidebar(self):
        with st.sidebar:
            st.session_state.lang = st.selectbox("Language", ("🇺🇸 en", "🇫🇷 fr"))[-2:]
