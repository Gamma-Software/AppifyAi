import streamlit as st
from ultralytics import YOLO
from PIL import Image

model_types = {
    "Segmentation": "yolov8n-seg.pt",
    "Pose": "yolov8n-pose.pt",
    "Object Detection": "yolov8n.pt",
    "Classification": "yolov8n-cls.pt",
}


@st.cache_data()  # Load a model in cache
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


# In case we want to change the confidence of the model
confidence = float(st.sidebar.slider("Select Model Confidence", 25, 100, 40)) / 100

# Select the model type from a selectbox in the sidebar
model_type = st.sidebar.selectbox("Select Model", model_types.keys())
if model_type:
    model = yolo_load_model(model_type)

image = st.file_uploader("image")

# Process and display the image if its uploaded
if image:
    with st.spinner("Predicting..."):
        img = Image.open(image)
        results = model(img, conf=confidence)  # predict on an image
        processed_image = results[0].plot()  # Get the processed image
        st.image(
            processed_image,
            caption=f"Image {image.name} processed",
            channels="BGR",
            use_column_width=True,
        )
