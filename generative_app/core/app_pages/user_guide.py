import streamlit as st
from hydralit import HydraHeadApp


class UserGuide(HydraHeadApp):
    def __init__(self, title="", **kwargs):
        self.__dict__.update(kwargs)
        self.title = title

    def run(self) -> None:
        user_guide_tab, demo_tab = st.tabs(["User Guide", "Demonstrations"])
        with user_guide_tab:
            st.write(
                "This page showcase the elements AppifyAi can display. It will help you better"
                "interact with the bot by using the correct words it'll understand."
            )

            with st.expander("Text elements"):
                st.header("This is a header")
                st.subheader("This is a subheader")

            st.info("Section is construction...")

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
