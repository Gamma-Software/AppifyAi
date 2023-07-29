import threading
import av
from cvzone.FaceMeshModule import FaceMeshDetector
from streamlit_webrtc import webrtc_streamer

lock = threading.Lock()
img_container = {"faces": None}
detector = FaceMeshDetector(maxFaces=2)


def video_frame_callback(frame):
    """This is the callback function that will be called when a new frame is received
    by the webrtc_streamer.Streamlit methods such as st.write() cannot be used inside the callback.
    """
    img = frame.to_ndarray(format="bgr24")

    # You can work with the image here... process it then display it back in the player
    processed_image, _ = detector.findFaceMesh(img)

    return av.VideoFrame.from_ndarray(processed_image, format="bgr24")


ctx = webrtc_streamer(
    key="example",
    video_frame_callback=video_frame_callback,
    media_stream_constraints={
        "video": {"sampleRate": 5},
        "audio": False,
    },
    video_html_attrs={
        "style": {"margin": "0 auto"},
        "controls": False,
        "autoPlay": True,
    },
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
)
