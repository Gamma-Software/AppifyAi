import streamlit as st
import cv2
from ultralytics import YOLO


# Load a model
@st.cache_data(show_spinner=True)
def yolo_load_model() -> YOLO:
    model = YOLO("yolov8n.pt")  # load an official model
    return model


def _display_detected_frames(
    conf, model, st_frame, image, is_display_tracking=None, tracker=None
):
    """
    Display the detected objects on a video frame using the YOLOv8 model.

    Args:
    - conf (float): Confidence threshold for object detection.
    - model (YoloV8): A YOLOv8 object detection model.
    - st_frame (Streamlit object): A Streamlit object to display the detected video.
    - image (numpy array): A numpy array representing the video frame.
    - is_display_tracking (bool): A flag indicating whether to display object
    tracking (default=None).

    Returns:
    None
    """

    # Resize the image to a standard size
    # image = cv2.resize(image, (720, int(720 * (9 / 16))))

    # Display object tracking, if specified
    if is_display_tracking:
        res = model.track(image, conf=conf, persist=True, tracker=tracker)
    else:
        # Predict the objects in the image using the YOLOv8 model
        res = model.predict(image, conf=conf)

    # # Plot the detected objects on the video frame
    res_plotted = res[0].plot()
    st_frame.image(
        res_plotted, caption="Detected Video", channels="BGR", use_column_width=True
    )


def play_stored_video(conf, model):
    """
    Plays a stored video file. Tracks and detects objects in real-time using the
    YOLOv8 object detection model.

    Parameters:
        conf: Confidence of YOLOv8 model.
        model: An instance of the `YOLOv8` class containing the YOLOv8 model.

    Returns:
        None

    Raises:
        None
    """

    def display_tracker_options():
        display_tracker = st.radio("Display Tracker", ("Yes", "No"))
        is_display_tracker = True if display_tracker == "Yes" else False
        if is_display_tracker:
            tracker_type = st.radio("Tracker", ("bytetrack.yaml", "botsort.yaml"))
            return is_display_tracker, tracker_type
        return is_display_tracker, None

    is_display_tracker, tracker = display_tracker_options()

    # video = st.file_uploader("Upload Video", type=["mp4", "mov", "avi"])
    video = "streamlit_snippets/IMG_4270.mp4"
    if video:
        with open(video, "rb") as video_file:
            video_bytes = video_file.read()
        if video_bytes:
            st.video(video_bytes)

        if st.sidebar.button("Detect Video Objects"):
            try:
                vid_cap = cv2.VideoCapture(str(video))
                st_frame = st.empty()
                while vid_cap.isOpened():
                    success, image = vid_cap.read()
                    if success:
                        _display_detected_frames(
                            conf, model, st_frame, image, is_display_tracker, tracker
                        )
                    else:
                        vid_cap.release()
                        break
            except Exception as e:
                st.sidebar.error("Error loading video: " + str(e))


model = yolo_load_model()
confidence = float(st.sidebar.slider("Select Model Confidence", 25, 100, 40)) / 100
play_stored_video(confidence, model)
