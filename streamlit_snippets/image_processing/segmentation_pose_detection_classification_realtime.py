import av
import threading
import streamlit as st
from ultralytics import YOLO
from streamlit_webrtc import webrtc_streamer

model_types = {
    "Segmentation": "yolov8n-seg.pt",
    "Pose": "yolov8n-pose.pt",
    "Object Detection": "yolov8n.pt",
    "Classification": "yolov8n-cls.pt",
}
lock = threading.Lock()
model_data = {"results": None}


@st.cache_resource  # Load a model in cache
def yolo_load_model(model_type: str) -> YOLO:
    """Load the Yolo model based on the model type

    Args:
        model_type (str): choose between Segmentation, Pose, Object Detection, Classification
    """
    if model_type not in model_types.keys():
        raise ValueError(
            f"model_type must be one of {list(model_types.keys())} not {model_type}"
        )
    model = YOLO(model_types[model_type])  # load an official model
    return model


if current_mode_type := st.sidebar.selectbox("Choose a model type", list(model_types.keys())):
    model = yolo_load_model(current_mode_type)


def video_frame_callback(frame):
    """This is the callback function that will be called when a new frame is received
    by the webrtc_streamer.Streamlit methods such as st.write() cannot be used inside the callback.
    """
    img = frame.to_ndarray(format="bgr24")

    results = model(img, imgsz=320)
    with lock:
        model_data["results"] = results

    # You can work with the image here... process it then display it back in the player
    return av.VideoFrame.from_ndarray(results[0].plot(), format="bgr24")


ctx = webrtc_streamer(
    key="example",
    video_frame_callback=video_frame_callback,
    media_stream_constraints={
        "video": True,
        "audio": False,
    },
    video_html_attrs={
        "style": {"margin": "0 auto"},
        "controls": False,
        "autoPlay": True,
    },
    rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
)

results_data_placeholder = st.empty()

while ctx.state.playing:
    with lock:
        # Retrieve the image from the webrtc callback
        results = model_data["results"]
    if results is None:
        continue
    if current_mode_type == "Classification":
        results_data_placeholder.write(results[0].probs.top5)
