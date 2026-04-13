# Real-time People Tracking System

FastAPI application for real-time people detection, tracking, and counting using YOLOv8 (ONNX), ByteTrack, and OpenCV.

## Features

- Detects only people (`class=0`) from webcam, RTSP stream, or video file.
- Tracks people with persistent IDs (ByteTrack).
- Counts `IN` and `OUT` when tracks cross a virtual line.
- Streams annotated frames via MJPEG (`/video_feed`).
- Broadcasts telemetry in real-time via WebSocket (`/ws/telemetry`).
- Handles video reconnects automatically.

## Tech Stack

- Python
- FastAPI + Uvicorn
- Ultralytics (YOLOv8 ONNX inference)
- OpenCV
- ONNX Runtime

## Project Structure

```text
app/
  api/
    telemetry.py        # WebSocket telemetry endpoint
    video.py            # MJPEG video endpoint
  core/
    counter.py          # Line-crossing IN/OUT logic
    detector_tracker.py # YOLO + ByteTrack wrapper
    stream_manager.py   # Video source read/reconnect
    telemetry_state.py  # Shared thread-safe state
    visualizer.py       # Drawing boxes, IDs, stats
  services/
    pipeline_service.py # Main processing loop
  main.py               # FastAPI app entrypoint
models/
  README.md             # Model placement/export note
static/
  index.html            # Simple UI viewer
```

## Quick Start

### 1) Create environment and install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Configure environment variables

Copy `.env.example` to `.env` and adjust values if needed.

```bash
copy .env.example .env
```

### 3) Add model file

Place your ONNX model at:

```text
models/yolov8n.onnx
```

You can export with Ultralytics:

```bash
yolo export model=yolov8n.pt format=onnx
```

### 4) Run server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open:

- `http://localhost:8000`
- `http://localhost:8000/video_feed`

## API Endpoints

- `GET /` - Serves `static/index.html`
- `GET /video_feed` - MJPEG stream
- `WS /ws/telemetry` - JSON telemetry stream

Example telemetry payload:

```json
{
  "fps": 21.45,
  "total_in": 3,
  "total_out": 1,
  "current_count": 5,
  "tracking_ids": [2, 4, 8, 11, 14],
  "status": "running",
  "timestamp": 1712900000.12
}
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `MODEL_PATH` | `models/yolov8n.onnx` | ONNX model path |
| `VIDEO_SOURCE` | `0` | Camera index, RTSP URL, or video file path |
| `CONF_THRESHOLD` | `0.35` | Detection confidence threshold |
| `IOU_THRESHOLD` | `0.45` | Tracking IOU threshold |
| `LINE_POSITION_RATIO` | `0.50` | Virtual line position by frame height ratio |
| `RECONNECT_DELAY_SEC` | `2.0` | Delay before reconnect attempt |
| `JPEG_QUALITY` | `80` | MJPEG quality |
| `TELEMETRY_INTERVAL_SEC` | `0.25` | WebSocket telemetry push interval |

## Publish to GitHub (Public)

Recommended before publishing:

- Do not commit `.env` (only keep `.env.example`).
- Do not commit `.venv/`.
- Do not commit large model binaries unless needed (or use Git LFS).

Commands:

```bash
git init
git add .
git commit -m "Initial commit: people tracking system"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

Then set repository visibility to **Public** in GitHub settings.
DEMO:
<img width="1771" height="902" alt="image" src="https://github.com/user-attachments/assets/fb131428-fc15-469b-af77-2a41822fe121" />

## License

MIT (or your preferred license).
