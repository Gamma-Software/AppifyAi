import streamlit as st
from ultralytics import YOLO
from PIL import Image
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil

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


def download_cropped_image(results, download_placeholder):
    """Download the cropped image"""
    temp_dir = Path(TemporaryDirectory().name)
    results.save_crop(save_dir=temp_dir, file_name=Path("cropped.jpg"))

    # Zip the directory and download it
    zipped_files = shutil.make_archive("cropped_data", "zip", root_dir=str(temp_dir))
    with open(zipped_files, "rb") as fp:
        download_placeholder.download_button(
            label="Download ZIP",
            data=fp,
            file_name="cropped_data.zip",
            mime="application/zip",
        )


@st.cache_data(show_spinner=True)
def process_image(image, confidence):
    img = Image.open(image)
    results = model(image, conf=confidence)  # predict on an image
    processed_image = results[0].plot()  # Get the processed image
    return results, processed_image


# In case we want to change the confidence of the model
confidence = float(st.sidebar.slider("Select Model Confidence", 25, 100, 40)) / 100

# Select the model type from a selectbox in the sidebar
if model_type := st.sidebar.selectbox("Select Model", model_types.keys()):
    model = yolo_load_model(model_type)

# Upload an image
image = st.file_uploader("image")

# Process and display the image if its uploaded
if image:
    results, processed_image = process_image(image, confidence)
    st.image(
        processed_image,
        caption=f"Image {image.name} processed",
        channels="BGR",
        use_column_width=True,
    )
    download_cropped_image(results[0], st.empty())
