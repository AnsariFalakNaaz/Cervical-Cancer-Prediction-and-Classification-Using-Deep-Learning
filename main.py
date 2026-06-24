# -------------------- Imports --------------------
import tensorflow as tf
import numpy as np
from PIL import Image
import io

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import os

# -------------------- App Init --------------------
app = FastAPI()

# -------------------- CORS --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Load Model --------------------
model = tf.keras.models.load_model("densenet121_aspp_model.h5")

# -------------------- Load Class Mapping --------------------
with open("model_metadata.json", "r") as f:
    metadata = json.load(f)

CLASS_MAP = {
    int(k): v.replace("_filtered_nlm", "").strip().lower()
    for k, v in metadata["class_mapping"].items()
}

# -------------------- Normal Classes --------------------
NORMAL_CLASSES = [
    "normal_superficiel",
    "normal_intermediate",
    "normal_columnar"
]

# -------------------- Utility --------------------
def load_json(filename: str):
    with open(os.path.join(os.getcwd(), filename), "r") as f:
        return json.load(f)

# -------------------- API --------------------

@app.get("/")
async def root():
    return {"message": "API is up and running"}

@app.get("/hospitals/all")
async def get_all_hospitals():
    return load_json("hospitals.json")

@app.get("/precautions")
async def get_all_precautions():
    return load_json("precautions.json")

# -------------------- Prediction --------------------

@app.post("/predict")
async def predict_cervical_image(file: UploadFile = File(...)):
    try:
        # Read image
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image = image.resize((224, 224))

        # Preprocess
        img_array = np.array(image) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Predict
        preds = model.predict(img_array)
        class_index = int(np.argmax(preds))
        confidence = float(np.max(preds))

        # Normalize class name
        class_name = CLASS_MAP.get(class_index, "unknown")

        # ---------------- Precautions ----------------
        precautions_data = load_json("precautions.json")

        # Normalize JSON keys
        normalized_precautions = {
            k.strip().lower(): v
            for k, v in precautions_data.items()
        }

        precautions = normalized_precautions.get(class_name, {
            "classification_type": "Unknown",
            "immediate_action": "No data available.",
            "lifestyle_changes": "No data available.",
            "follow_up": "No data available.",
            "diagnostic_tests": [],
            "treatment_options": []
        })

        # ---------------- Hospitals ----------------
        if class_name in NORMAL_CLASSES:
            hospitals = []
        else:
            hospitals = load_json("hospitals.json")

        return {
            "predicted_class": class_name,
            "confidence": round(confidence, 4),
            "precautions": precautions,
            "hospitals": hospitals
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))