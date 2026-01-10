# Bangladeshi Currency Detection using YOLO11

A deep learning project for detecting and classifying Bangladeshi currency notes and coins using YOLOv11.

## Overview

This project leverages the YOLOv11 object detection model to identify and classify various denominations of Bangladeshi currency (notes and coins). The model is trained on a custom dataset containing images of:

- **Notes**: 1, 2, 5, 10, 20, 50, 100, 200, 500, 1000 Taka
- **Coins**: 1, 2, 5 Taka coin
- And other denominations

## Project Structure

```
bd-currency-detection-yolo11/
├── script.ipynb                 # Main Jupyter notebook for training and inference
├── rename.py                    # Utility script for batch renaming images
├── split.py                     # Utility script for splitting dataset
├── yolo11n.pt                   # Pretrained YOLOv11 nano model weights
├── README.md                    # This file
├── dataset/                     # Dataset directory
│   ├── data.yaml               # Dataset configuration
│   ├── train/                  # Training set (70%)
│   │   ├── images/
│   │   └── labels/
│   ├── valid/                  # Validation set (15%)
│   │   ├── images/
│   │   └── labels/
│   └── test/                   # Test set (15%)
│       ├── images/
│       └── labels/
└── runs/                        # Training outputs
    └── bdt_yolo11_train/       # Trained model and logs
        ├── weights/            # Best and last model weights
        ├── results.csv         # Training metrics
        └── args.yaml           # Training configuration
```

## Requirements

- Python 3.8+
- ultralytics
- matplotlib

## Installation

1. **Clone or download the project**
   ```bash
   cd bd-currency-detection-yolo11
   ```

2. **Install dependencies**
   ```bash
   pip install ultralytics matplotlib
   ```

3. **Verify dataset**
   The dataset should be in the `dataset/` directory with the following structure:
   - `dataset/train/` - Training images and labels
   - `dataset/valid/` - Validation images and labels
   - `dataset/test/` - Test images and labels
   - `dataset/data.yaml` - Dataset configuration file

## Docker Setup

### Prerequisites
- Docker installed on your system
- Docker Compose (optional, for easier deployment)

### Building the Docker Image

1. **Build the Docker image**
   ```bash
   docker build -t bd-currency-detection:latest .
   ```

2. **Verify the image was created**
   ```bash
   docker images | grep bd-currency-detection
   ```

### Running with Docker

#### Option 1: Using Docker directly

```bash
docker run -p 8000:8000 --name bdt-api bd-currency-detection:latest
```

This will:
- Start the API server on port 8000
- Make the model available at `http://localhost:8000`

#### Option 2: Using Docker Compose (Recommended)

1. **Start the container**
   ```bash
   docker-compose up -d
   ```

2. **View logs**
   ```bash
   docker-compose logs -f bdt-yolo-api
   ```

3. **Stop the container**
   ```bash
   docker-compose down
   ```

### API Endpoints

#### Live Deployment
- **Live API**: https://bd-currency-detection-latest.onrender.com
- **Live API Docs**: https://bd-currency-detection-latest.onrender.com/docs (Swagger UI)

#### Local Deployment
Once the Docker container is running, you can access:
- **API Root**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:8000/redoc` (ReDoc)

### Docker Configuration

**Dockerfile Details:**
- **Base Image**: Python 3.10-slim (lightweight)
- **Working Directory**: `/app`
- **Port**: 8000 (FastAPI default)
- **Dependencies**: Installs OpenCV dependencies (libgl1, libglib2.0-0)

**docker-compose.yml Details:**
- **Service Name**: bdt-yolo-api
- **Container Name**: bdt-yolo-api
- **Port Mapping**: Host port 8000 → Container port 8000
- **Restart Policy**: unless-stopped (auto-restart on failure)

### Volume Mounting (Optional)

To mount local directories for input/output:

```bash
docker run -p 8000:8000 \
  -v $(pwd)/test-images:/app/test-images \
  -v $(pwd)/results:/app/results \
  --name bdt-api bd-currency-detection:latest
```

### Troubleshooting Docker Issues

**Container won't start:**
- Check if port 8000 is already in use: `lsof -i :8000`
- Review logs: `docker logs bdt-yolo-api`

**Import errors:**
- Ensure all dependencies are in `requirements.txt`
- Rebuild image: `docker build --no-cache -t bd-currency-detection:latest .`

**Permission issues:**
- Run Docker commands with appropriate permissions
- On Linux, add your user to docker group: `sudo usermod -aG docker $USER`

## Usage

### Training

Run the Jupyter notebook [script.ipynb](script.ipynb) or execute training directly:

```python
from ultralytics import YOLO

# Load pretrained model
model = YOLO("yolo11n.pt")

# Train the model
results = model.train(
    data="dataset/data.yaml",
    epochs=100,
    batch=16,
    imgsz=640,
    project="runs",
    name="bdt_yolo11_train"
)
```

**Training Parameters:**
- **Epochs**: 100
- **Batch Size**: 16
- **Image Size**: 640×640
- **Optimizer**: Default (SGD)
- **Confidence Threshold**: 0.25

### Validation

Evaluate the trained model on the validation set:

```python
metrics = model.val(
    data="dataset/data.yaml",
    split="valid",
    imgsz=640
)
```

### Testing

Run inference on test images:

```python
predictions = model.predict(
    source="dataset/test/images",
    imgsz=640,
    conf=0.25,
    save=True
)
```

Results are saved in `runs/detect/` directory.

### Batch Prediction

For custom images or video:

```python
# Single image
results = model.predict(source="path/to/image.jpg", conf=0.25)

# Video
results = model.predict(source="path/to/video.mp4", conf=0.25)

# Folder
results = model.predict(source="path/to/images/", conf=0.25)
```

## Dataset Information

### Classes (13 total)
Currency denominations detected by the model. Check `dataset/data.yaml` for the complete class mapping.

### Dataset Statistics
- **Training samples**: ~70% of total images
- **Validation samples**: ~15% of total images
- **Test samples**: ~15% of total images

To view dataset statistics, run the analysis cells in [script.ipynb](script.ipynb):
- Dataset split summary (images/labels/missing/empty)
- Boxes per split and per class
- File consistency checks

## Model Checkpoints

Trained model weights are saved in:
- **Best weights**: `runs/bdt_yolo11_train/weights/best.pt`
- **Last weights**: `runs/bdt_yolo11_train/weights/last.pt`

## Performance

Training metrics and validation results are logged in:
- `runs/bdt_yolo11_train/results.csv` - Training curves
- Training visualizations are available in the runs directory

Key metrics tracked:
- Box loss, Cls loss, DFL loss
- Precision, Recall, mAP50, mAP50-95
- Per-class metrics

## Prediction Accuracy

The YOLOv11 model provides robust detection and classification of Bangladeshi currency denominations with competitive accuracy metrics:

### Model Performance Metrics
- **mAP50**: Mean Average Precision at IoU threshold of 0.50
- **mAP50-95**: Mean Average Precision across IoU thresholds from 0.50 to 0.95
- **Precision**: Percentage of detected objects that are correctly classified
- **Recall**: Percentage of actual objects that were successfully detected

### Accuracy Discussion
The trained model achieves solid performance across different currency denominations. The accuracy varies based on:
- **Image Quality**: Clear, well-lit images yield higher detection accuracy
- **Currency Denomination**: More training samples for a denomination typically result in better detection rates
- **Object Scale**: Very small or very large currency objects may have slightly lower accuracy
- **Multiple Objects**: The model can detect multiple currency items in a single image, though accuracy may vary with object density

### Confidence Threshold Impact
The model uses a confidence threshold of **0.25** by default:
- **Lower threshold** (< 0.25): More detections but increased false positives
- **Higher threshold** (> 0.25): Fewer but more reliable detections

Users can adjust the confidence threshold based on their specific use case requirements.

### Improving Accuracy
To improve prediction accuracy:
1. Provide high-quality, well-lit images
2. Ensure images are taken from multiple angles
3. Include images with various backgrounds
4. Use higher resolution images (640×640 or above)
5. Fine-tune the model on more diverse dataset samples
6. Adjust the confidence threshold for your application's needs

## Utility Scripts

### rename.py
Batch rename images in the dataset (useful for data preprocessing).

### split.py
Split dataset into train/valid/test sets with specified ratios.

## Results

After training, view results in Jupyter notebook or check the runs directory:
- Confusion matrices
- Detection results on test images
- Training/validation curves
- Per-class metrics

## Test Results & Examples

### Test Images
Sample currency images used for testing:
- **5 taka.jpeg** - 5 Taka note detection
- **5 taka coin.jpeg** - 5 Taka coin detection
- **50 taka.jpeg** - 50 Taka note detection
- **50 taka 2.jpeg** - Alternative 50 Taka note image
- **500 taka.jpeg** - 500 Taka note detection
- **none.jpg** - Negative sample (non-currency object)

### Detection Screenshots
Prediction results and API testing:

| Screenshot | Description |
|-----------|-------------|
| `test_5_taka_coin.png` | Detection result for 5 Taka coin |
| `test_50_taka.png` | Detection result for 50 Taka note |
| `test_500_taka.png` | Detection result for 500 Taka note |
| `test_no_taka.png` | Negative detection (no currency) |
| `test_unsupported_image.png` | Handling unsupported image formats |
| `docker-ps.png` | Docker deployment verification |

### Running Tests

To test the model on sample images:

```python
from ultralytics import YOLO

# Load trained model
model = YOLO("runs/bdt_yolo11_train/weights/best.pt")

# Run predictions on test images
results = model.predict(
    source="test-images/",
    imgsz=640,
    conf=0.25,
    save=True
)

# Results will be saved in runs/detect/predict/
```

### API Testing with Screenshots

Once the Docker container or API is running:

1. **Access Swagger UI**: Open `http://localhost:8000/docs`
2. **Upload test images** and view detection results
3. **Check predictions** with confidence scores and bounding boxes

Screenshots demonstrating successful detections and edge cases are available in the `screenshorts/` directory.

## License

This project uses the YOLOv11 model from Ultralytics. Please refer to their documentation and licensing terms.

## References

- [Ultralytics YOLOv11 Documentation](https://docs.ultralytics.com/)
- [YOLOv11 GitHub Repository](https://github.com/ultralytics/ultralytics)

---

**Author**: Masum  
**Last Updated**: January 2026
