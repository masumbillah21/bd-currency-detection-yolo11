# Deploying BD Currency Detection to Render.com

This guide provides step-by-step instructions for deploying the Bangladeshi Currency Detection API to Render.com.

## Prerequisites

Before you begin, ensure you have:
- A GitHub account with the repository pushed
- A Render.com account (free tier available at https://render.com)
- Git installed on your local machine
- All project files ready (including trained model weights)

## Step 1: Prepare Your Repository

### 1.1 Create a .renderignore file

Create a `.renderignore` file in the root directory to exclude unnecessary files:

```
__pycache__/
*.pyc
*.pyo
*.egg-info/
.DS_Store
.env
.venv
venv/
*.log
dataset/train/
dataset/test/
dataset/valid/
.git/
.github/
screenshorts/
test-images/
```

Save this file as `/path/to/project/.renderignore`

### 1.2 Ensure Model Weights Are Available

The trained model weights must be in the correct directory:
```
runs/
└── detect/
    └── bdt_yolo11_train/
        └── weights/
            ├── best.pt
            └── last.pt
```

**Note**: If the model file is too large (> 100MB), consider:
- Using Git LFS (Large File Storage)
- Uploading to cloud storage and downloading during startup
- Splitting the model into smaller parts

### 1.3 Update requirements.txt

Ensure `requirements.txt` is complete and compatible:

```
fastapi==0.115.6
uvicorn[standard]==0.32.1
ultralytics==8.3.0
pillow==10.4.0
python-multipart==0.0.12
opencv-python-headless==4.10.0.84
```

**Important**: Use `opencv-python-headless` instead of `opencv-python` for server environments.

## Step 2: Create Render Configuration Files

### 2.1 Create render.yaml (Infrastructure as Code)

Create a `render.yaml` file in the root directory for automated deployment:

```yaml
services:
  - type: web
    name: bd-currency-detection
    env: docker
    dockerfilePath: ./Dockerfile
    dockerContext: ./
    plan: free
    envVars:
      - key: PYTHON_VERSION
        value: "3.10"
    autoDeploy: true
    healthCheckPath: /health
    scaling:
      minInstances: 1
      maxInstances: 1
    disk:
      name: model-cache
      mountPath: /app/model_cache
      sizeGB: 10
```

### 2.2 Dockerfile Optimization for Render

Update your `Dockerfile` for Render.com optimization:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY runs/detect/bdt_yolo11_train/weights ./runs/detect/bdt_yolo11_train/weights

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Step 3: Push to GitHub

Ensure your repository is pushed to GitHub with all necessary files:

```bash
git add .
git commit -m "Prepare for Render.com deployment"
git push origin main
```

## Step 4: Deploy on Render.com

### 4.1 Connect GitHub Repository

1. Log in to [Render.com](https://render.com)
2. Click **"New +"** button
3. Select **"Web Service"**
4. Choose **"Connect a GitHub repository"**
5. Search for and select `bd-currency-detection-yolo11`
6. Grant necessary permissions

### 4.2 Configure the Service

1. **Service Name**: `bd-currency-detection` (or your preferred name)
2. **Environment**: Select **"Docker"** from dropdown
3. **Plan**: Choose **"Free"** or **"Starter"** (depending on your needs)
4. **Dockerfile Path**: Leave default or specify `./Dockerfile`
5. **Build Command**: Leave empty (automatic)
6. **Start Command**: Leave empty (from Dockerfile)

### 4.3 Set Environment Variables (Optional)

In the "Environment" section, add if needed:
- `PYTHON_VERSION`: `3.10`
- `PORT`: `8000`

### 4.4 Deploy

Click **"Create Web Service"** and wait for the build and deployment to complete.

## Step 5: Monitor Deployment

### 5.1 Check Deployment Status

- Watch the build logs in the Render dashboard
- Look for messages indicating successful startup
- Verify the service URL is generated

### 5.2 Health Check

Once deployed, verify the API is running:

```bash
curl https://your-service-name.onrender.com/health
```

Expected response:
```json
{"status": "ok", "model_loaded": true}
```

### 5.3 Access the API

- **API Docs**: `https://your-service-name.onrender.com/docs`
- **ReDoc**: `https://your-service-name.onrender.com/redoc`
- **Predictions**: `https://your-service-name.onrender.com/predict`

## Step 6: Make Predictions

### Using cURL

```bash
curl -X POST "https://your-service-name.onrender.com/predict" \
  -F "file=@path/to/image.jpg"
```

### Using Python

```python
import requests

url = "https://your-service-name.onrender.com/predict"
files = {"file": open("test-image.jpg", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

### Using Swagger UI

1. Open: `https://your-service-name.onrender.com/docs`
2. Click **"Try it out"** on `/predict` endpoint
3. Upload an image file
4. Click **"Execute"**
5. View results

## Troubleshooting

### Build Fails: "Model file not found"

**Solution**:
1. Ensure `runs/detect/bdt_yolo11_train/weights/best.pt` is in the repository
2. If file is too large, use Git LFS:
   ```bash
   git lfs install
   git lfs track "*.pt"
   git add .gitattributes
   git add runs/detect/bdt_yolo11_train/weights/best.pt
   git commit -m "Add model weights with Git LFS"
   git push
   ```

### Build Fails: "Out of memory" or "Disk space"

**Solution**:
- Free tier has limited resources
- Upgrade to Starter plan
- Remove unnecessary files (dataset directories)
- Use `.renderignore` to exclude large files

### API Timeout or Slow Responses

**Solution**:
- First prediction may be slower as model loads (add startup delay in health check)
- Upgrade to higher plan for better resources
- Check model inference time on your machine

### "Module not found" Error

**Solution**:
1. Verify all imports in `requirements.txt`
2. Ensure `app/` directory structure is correct
3. Rebuild from scratch:
   ```
   - Delete the service on Render
   - Push any fixes to GitHub
   - Create new service
   ```

### Port Issues

**Solution**:
- Render automatically assigns port 8000 if available
- Don't hardcode ports; use environment variable:
   ```python
   import os
   port = int(os.getenv("PORT", 8000))
   ```

## Performance Tips

### 1. Use Model Caching

Add to `app/main.py`:
```python
import os
from pathlib import Path

CACHE_DIR = Path(os.getenv("MODEL_CACHE", "/tmp/model_cache"))
CACHE_DIR.mkdir(exist_ok=True)
```

### 2. Optimize Image Processing

```python
# Resize large images before prediction
from PIL import Image

def preprocess_image(image: Image.Image, max_size=640):
    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    return image
```

### 3. Add Request Timeout

```python
from fastapi import FastAPI
import asyncio

@app.post("/predict")
async def predict(file: UploadFile):
    try:
        result = await asyncio.wait_for(process_prediction(file), timeout=30.0)
        return result
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Prediction timeout")
```

## Cost Optimization

### Free Tier Limitations
- 750 hours/month (enough for one service running 24/7)
- Shuts down after 15 minutes of inactivity
- Limited compute resources

### Upgrade Path
- **Starter Plan**: $7/month for dedicated resources
- **Standard Plan**: $12/month with better performance
- **Pro Plan**: $25/month for high-performance needs

## Auto-Deployment

Enable auto-deploy for automatic updates:

1. Go to service settings
2. Under "Deploy", toggle **"Auto-Deploy"** ON
3. Choose branch (usually `main`)
4. Service automatically redeploys on push

## Monitoring and Logs

### View Logs

```bash
# Using Render CLI (if installed)
render logs bd-currency-detection
```

Or in the Render dashboard:
1. Click on your service
2. Go to "Logs" tab
3. Filter by level (Error, Warning, Info)

### Monitor Metrics

In the Render dashboard:
- CPU usage
- Memory usage
- Network I/O
- Build and deployment history

## Advanced: Custom Domain

To add a custom domain:

1. Go to your service in Render
2. Click "Settings"
3. Under "Custom Domain", enter your domain
4. Follow DNS configuration steps
5. Update CORS settings in `app/main.py` if needed

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Additional Resources

- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Ultralytics YOLOv11 Docs](https://docs.ultralytics.com/)

## Support

For issues or questions:
- Check [Render Support](https://render.com/docs)
- Review application logs
- Test locally with Docker first
- Verify all files are properly committed to Git
