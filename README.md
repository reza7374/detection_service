# Get Point Game 🎯

An AI-powered aim game controlled by your **right hand** via webcam. Move your hand to guide the crosshair to the target and score points.

## System Architecture

```
Webcam → [Detection Service] → gRPC → [Tracking Service] → Redis → [GUI Service]
```

| Service | Description | Protocol |
|---|---|---|
| **Detection Service** | Captures webcam frames, detects right hand via MediaPipe, sends position | gRPC client |
| **Tracking Service** | Receives hand position, calculates direction, writes to Redis | gRPC server |
| **Redis** | Message broker between Tracking and GUI | Key-Value |
| **GUI Service** | Reads direction from Redis, moves crosshair, tracks score | Redis client |

---

## Requirements

- Python 3.10
- Webcam
- Redis
- Docker & Docker Compose (for containerized run)

---

## Technical Notes

### Hand Detection Model
This project uses **MediaPipe** for hand detection and landmark extraction. MediaPipe is a lightweight, CPU-friendly solution that works well for real-time hand tracking without requiring a GPU.

However, the detection service is modular and can be replaced with any other model. Alternative options include:

- **YOLOv8** (Ultralytics) — better accuracy, supports GPU acceleration, good for complex scenes
- **YOLOv9 / YOLOv11** — cutting-edge YOLO variants with improved detection performance
- **OpenPose** — full body pose estimation including hands
- **TensorFlow Hand Pose** — Google's TF-based alternative to MediaPipe

To swap the model, only `detection_service.py` needs to be changed. The gRPC interface (`SendPosition` with `x`, `y` coordinates) stays the same regardless of which model is used underneath.

---

### Python Environment
This project was developed using **Mamba** (a fast drop-in replacement for Conda) to manage the Python environment. However, it is fully compatible with any Python environment manager:

- `conda` — `conda create -n ai_task python=3.10`
- `mamba` — `mamba create -n ai_task python=3.10`
- `venv` — `python3.10 -m venv ai_task`
- `virtualenv` — `virtualenv -p python3.10 ai_task`
- `poetry`, `pipenv`, etc.

The only requirement is **Python 3.10**.

---

### Proto File Generation — Known Version Conflict

There is a known dependency conflict between **MediaPipe** and **grpcio-tools**:

- `mediapipe==0.10.9` requires `protobuf < 4`
- `grpcio-tools >= 1.62` requires `protobuf >= 4`

This means both cannot coexist in the same environment. The workaround is to generate the gRPC Python files (`hand_pb2.py` and `hand_pb2_grpc.py`) in a **separate temporary environment**, then copy the generated files into the main environment.

**Steps to regenerate proto files if needed:**

```bash
# Step 1 - create a temporary environment
conda create -n proto_gen python=3.10 -y
conda activate proto_gen

# Step 2 - install only grpcio-tools
pip install grpcio-tools==1.62.0

# Step 3 - generate the files
python -m grpc_tools.protoc -I./proto --python_out=. --grpc_python_out=. proto/hand.proto

# Step 4 - copy generated files to service folders
cp hand_pb2.py hand_pb2_grpc.py detection_service/
cp hand_pb2.py hand_pb2_grpc.py tracking_service/

# Step 5 - deactivate temp env
conda deactivate
```

The generated files are already included in the repository so this step is only needed if `hand.proto` is modified.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `REDIS_HOST` | `localhost` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `GRPC_HOST` | `localhost` | Tracking service hostname |
| `GRPC_PORT` | `50051` | Tracking service gRPC port |

---

## Option 1 — Run Without Docker (3 Terminals)

### Prerequisites

```bash
pip install mediapipe==0.10.9 opencv-python grpcio==1.48.2 protobuf==3.20.3 redis PyQt5
```

### Terminal 1 — Start Redis

```bash
redis-server
```

Or via Docker (just Redis):

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

Monitor Redis in a separate terminal (optional):

```bash
redis-cli monitor
```

### Terminal 2 — Start Tracking Service (gRPC Server)

```bash
cd tracking_service
python tracking_service.py
```

Expected output:
```
Tracking Service (gRPC Server) started on port 50051...
```

### Terminal 3 — Start GUI Service

```bash
cd gui_service
python main.py
```

The game window will open with a crosshair and a red target.

### Terminal 4 — Start Detection Service

```bash
cd detection_service
python detection_service.py
```

The webcam window will open. Show your **right hand** to the camera and move it to control the crosshair.

---

## Option 2 — Run With Docker

### Prerequisites

- Docker
- Docker Compose

### Step 1 — Allow display access

```bash
xhost +local:docker
```

### Step 2 — Build and run all services

```bash
docker compose up --build
```

### Step 3 — Stop all services

```bash
docker compose down
```

### Step 4 — View logs

```bash
# All services
docker compose logs -f

# Single service
docker compose logs -f tracking_service
```

---

## Project Structure

```
project/
├── docker-compose.yml
├── README.md
├── detection_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── detection_service.py
│   ├── hand_pb2.py
│   └── hand_pb2_grpc.py
├── tracking_service/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── tracking_service.py
│   ├── hand_pb2.py
│   └── hand_pb2_grpc.py
└── gui_service/
    ├── Dockerfile
    ├── requirements.txt
    └── main.py
```

---

## Proto Definition

The gRPC contract is defined in `proto/hand.proto`:

```proto
service HandProcessor {
  rpc SendPosition (PositionRequest) returns (EmptyResponse) {}
}

message PositionRequest {
  float x = 1;
  float y = 2;
}
```

---

## Logs

Game scores and events are logged to `gui_service/game.log` with timestamps:

```
2026-04-30 12:00:01 [GUI] INFO - Game started. Waiting for hand input...
2026-04-30 12:00:15 [GUI] INFO - SCORE! Total score: 1 at 2026-04-30 12:00:15
2026-04-30 12:00:15 [GUI] INFO - New goal position: (342, 187)
```

---

## How to Play

1. Start all services (Docker or manual)
2. Show your **right hand** to the webcam
3. Move your hand to guide the **green crosshair** to the **red target**
4. Each hit scores a point — target moves to a new random position
5. Press `ESC` in the webcam window to exit