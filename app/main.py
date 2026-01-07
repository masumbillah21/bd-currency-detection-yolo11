import io
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError
from ultralytics import YOLO

APP_TITLE = "BDT Denomination Detection API"
MODEL_PATH = Path("./runs/bdt_yolo11_train/weights/best.pt")

CLASS_NAMES = [
    "1_takar_coin",
    "1_taka",
    "2_taka",
    "2_takar_coin",
    "5_taka",
    "5_takar_coin",
    "10_taka",
    "20_taka",
    "50_taka",
    "100_taka",
    "200_taka",
    "500_taka",
    "1000_taka",
]

app = FastAPI(title=APP_TITLE)

model = None


@app.on_event("startup")
def load_model():
    global model
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model weights not found at: {MODEL_PATH.resolve()}")
    model = YOLO(str(MODEL_PATH))


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/predict")
async def predict(file: UploadFile = File(None)):
    # ---- validate input exists ----
    if file is None:
        raise HTTPException(status_code=400, detail="Missing file field 'file'.")

    # ---- validate content type ----
    if file.content_type not in ("image/jpeg", "image/png"):
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Use JPEG or PNG.",
        )

    # ---- read bytes ----
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read uploaded file.")

    # ---- decode image ----
    try:
        img = Image.open(io.BytesIO(contents)).convert("RGB")
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid image file.")
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to process image.")

    # ---- run inference ----
    try:
        results = model.predict(img, conf=0.25, verbose=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

    r = results[0]
    detections: List[Dict[str, Any]] = []

    if r.boxes is not None and len(r.boxes) > 0:
        # xyxy in pixels, confidence, class id
        boxes_xyxy = r.boxes.xyxy.tolist()
        confs = r.boxes.conf.tolist()
        clss = r.boxes.cls.tolist()

        for box, conf, cls_id in zip(boxes_xyxy, confs, clss):
            cls_id = int(cls_id)
            name = CLASS_NAMES[cls_id] if 0 <= cls_id < len(CLASS_NAMES) else str(cls_id)

            detections.append(
                {
                    "name": name,
                    "confidence": float(conf),
                    "box": {
                        "x1": float(box[0]),
                        "y1": float(box[1]),
                        "x2": float(box[2]),
                        "y2": float(box[3]),
                    },
                }
            )

    # ---- response format required by rubric ----
    response = {
        "filename": file.filename,
        "detections": detections,
        "count": len(detections),
    }
    return JSONResponse(content=response, status_code=200)
