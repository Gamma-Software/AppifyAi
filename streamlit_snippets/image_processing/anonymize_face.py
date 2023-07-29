import threading
import av
import cv2
from cvzone.FaceDetectionModule import FaceDetector
from streamlit_webrtc import webrtc_streamer

lock = threading.Lock()
img_container = {"faces": None}
detector = FaceDetector()


def anonymize_face_simple(image, factor=3.0):
    """ Simply blurs the face in the image by a factor"""
    (h, w) = image.shape[:2]
    kW = int(w / factor)
    kH = int(h / factor)
    if kW % 2 == 0:
        kW -= 1
    if kH % 2 == 0:
        kH -= 1
    return cv2.GaussianBlur(image, (kW, kH), 0)


def video_frame_callback(frame):
    """This is the callback function that will be called when a new frame is received
    by the webrtc_streamer.Streamlit methods such as st.write() cannot be used inside the callback.
    """
    img = frame.to_ndarray(format="bgr24")

    # You can work with the image here... process it then display it back in the player
    _, bboxs = detector.findFaces(img, draw=False)

    if bboxs:
        # Crop the face from the original image
        face = img[
            bboxs[0]["bbox"][1]: bboxs[0]["bbox"][1] + bboxs[0]["bbox"][3],
            bboxs[0]["bbox"][0]: bboxs[0]["bbox"][0] + bboxs[0]["bbox"][2],
        ]

        face = anonymize_face_simple(face, factor=3.0)

        # Draw the face on the black image
        img[
            bboxs[0]["bbox"][1]: bboxs[0]["bbox"][1] + bboxs[0]["bbox"][3],
            bboxs[0]["bbox"][0]: bboxs[0]["bbox"][0] + bboxs[0]["bbox"][2],
        ] = face

    return av.VideoFrame.from_ndarray(img, format="bgr24")


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
