from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
import io
import tempfile
import os
from fastapi import Depends
from app.dependencies import get_current_user

router = APIRouter()

model = YOLO("yolov8n.pt")

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]

def save_temp_image(file_bytes: bytes, suffix=".jpg") -> str:
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp_file.write(file_bytes)
    tmp_file.close()
    return tmp_file.name

def load_image_from_bytes(image_bytes: bytes) -> np.ndarray:
    try:
        image_pil = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Unsupported or corrupted image.")
    image_np = np.array(image_pil)
    return cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)

def detect_objects_with_model(image: np.ndarray):
    rgb_img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = model(rgb_img, verbose=False)[0]
    detections = []
    for box in results.boxes:
        label_id = int(box.cls[0])
        label = model.names[label_id]
        conf = float(box.conf[0])  # Lấy confidence
        if label in ["dog", "cat"]:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append({
                "label": label,
                "confidence": conf,
                "bbox": [x1, y1, x2, y2]
            })
    return detections


def draw_bounding_boxes(image: np.ndarray, detections: list):
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        label = det["label"]
        conf = det["confidence"]
        label_text = f"{label} {conf:.2f}"

        # Vẽ bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Vẽ label text + confidence lên góc trái trên
        (text_width, text_height), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(image, (x1, y1 - text_height - 6), (x1 + text_width, y1), (0, 255, 0), -1)
        cv2.putText(image, label_text, (x1, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 0, 0), 1)
    return image

@router.post("/detect-object-with-authorize/")
async def detect_object(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image format.")

    image_bytes = await file.read()

    tmp_path = save_temp_image(image_bytes, suffix=os.path.splitext(file.filename)[-1])
    
    try:
        image_np = load_image_from_bytes(image_bytes)

        detections = detect_objects_with_model(image_np)
        image_with_boxes = draw_bounding_boxes(image_np, detections)
        _, img_encoded = cv2.imencode(".jpg", image_with_boxes)
        return StreamingResponse(io.BytesIO(img_encoded.tobytes()), media_type="image/jpeg")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.post("/detect-object/")
async def detect_object(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image format.")

    image_bytes = await file.read()

    tmp_path = save_temp_image(image_bytes, suffix=os.path.splitext(file.filename)[-1])
    
    try:
        image_np = load_image_from_bytes(image_bytes)

        detections = detect_objects_with_model(image_np)
        image_with_boxes = draw_bounding_boxes(image_np, detections)
        _, img_encoded = cv2.imencode(".jpg", image_with_boxes)
        return StreamingResponse(io.BytesIO(img_encoded.tobytes()), media_type="image/jpeg")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

