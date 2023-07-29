import threading
import av
import cv2
import streamlit as st
from matplotlib import pyplot as plt

from streamlit_webrtc import webrtc_streamer

lock = threading.Lock()
img_container = {"img": None}


def video_frame_callback(frame):
    """This is the callback function that will be called when a new frame is received
    by the webrtc_streamer.Streamlit methods such as st.write() cannot be used inside the callback.
    """
    img = frame.to_ndarray(format="bgr24")
    with lock:
        img_container["img"] = img

    # You can work with the image here... process it then display it back in the player
    processed_image = img
    return av.VideoFrame.from_ndarray(processed_image, format="bgr24")


st.title("Real time Histogram")
ctx = webrtc_streamer(
    key="example",
    video_frame_callback=video_frame_callback,
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
)

# Display the histogram in real time
fig_place = st.empty()
fig, ax = plt.subplots(1, 1)

while ctx.state.playing:
    with lock:
        # Retrieve the image from the webrtc callback
        img = img_container["img"]
    if img is None:
        continue
    # Then you can process the image as you wish
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ax.cla()
    ax.hist(gray.ravel(), 256, [0, 256])
    fig_place.pyplot(fig)
