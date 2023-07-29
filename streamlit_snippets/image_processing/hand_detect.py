import threading
import av
import streamlit as st
from cvzone.HandTrackingModule import HandDetector
from streamlit_webrtc import webrtc_streamer

lock = threading.Lock()
img_container = {"distance": None}
detector = HandDetector(detectionCon=0.8, maxHands=2)

finger_type = {"Thumb": 0, "Index": 1, "Middle": 2, "Ring": 3, "Pinky": 4}


def get_hand_info(hand_data):
    lmList2 = hand_data["lmList"]  # List of 21 Landmark points of the first hand
    bbox1 = hand_data["bbox"]  # Bounding box info x,y,w,h of the first hand
    centerPoint1 = hand_data["center"]  # center of the hand cx,cy
    handType1 = hand_data["type"]  # Hand Type "Left" or "Right"
    fingerTips1 = [
        lmList2[id][0:2] for id in detector.tipIds
    ]  # Finger tip coordinates of the first hand from thumb to little finger
    return lmList2, bbox1, centerPoint1, handType1, fingerTips1


def video_frame_callback(frame):
    img = frame.to_ndarray(format="bgr24")
    # Find the hand and its landmarks
    hands, img = detector.findHands(img)  # with draw
    # hands = detector.findHands(img, draw=False)  # without draw

    if hands:
        hand1Info = get_hand_info(hands[0])

        if len(hands) == 2:
            hand2Info = get_hand_info(hands[1])

            # Find Distance between the two index. Could be same hand or different hands
            distance, _, img = detector.findDistance(
                hand1Info[4][finger_type["Index"]],
                hand2Info[4][finger_type["Index"]],
                img,
            )  # with draw
            # Send the distance
            with lock:
                img_container["distance"] = distance
    # Draw the image with the hand annotations
    return av.VideoFrame.from_ndarray(img, format="bgr24")


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

# Save the distance between the two fingers in a list in the session state
st.session_state["length"] = []

# First add placeholder for the plot
plot_place = st.empty()

while ctx.state.playing:
    with lock:
        # Retrieve the image from the webrtc callback
        distance = img_container["distance"]
    if distance is None:
        continue
    # Add the new distance to the list and update the plot
    st.session_state["distance"].append(distance)
    plot_place.line_chart(st.session_state["distance"])
