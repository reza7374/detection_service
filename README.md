# 🎯 Get The Point Game (Redis + PyQt)

A simple real-time GUI game where an aim (crosshair) is controlled via Redis commands.

---

## 🚀 Setup & Run Guide

### 1️⃣ Install Redis (choose one)

#### Option A — Native install (Ubuntu)

```bash
sudo apt update
sudo apt install redis-server -y
sudo systemctl start redis
```

Verify Redis is running:

```bash
redis-cli ping
# Expected output: PONG
```

---

#### Option B — Docker (recommended)

```bash
docker run -d -p 6379:6379 --name redis redis
```

---

### 2️⃣ Create Python virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### 3️⃣ Install dependencies

```bash
pip install -r requirements-freeze.txt
```

---

### 4️⃣ Run the application

```bash
python main.py
```

---

## 🧪 Control the Game via Redis

Open a new terminal and run:

```bash
redis-cli
```

Send movement commands:

```bash
SET aim_direction LEFT
SET aim_direction RIGHT
SET aim_direction UP
SET aim_direction DOWN
```

---

## 🧩 Notes

- Redis must be running on `localhost:6379`
- Commands are **case-sensitive** (`LEFT`, not `left`)
- The GUI updates every **50ms (20 FPS)**

---

## ⚡ Suggested Improvements

- Replace polling with Redis **Pub/Sub**
- Use vector-based movement (`dx`, `dy`)
- Add smoothing (velocity instead of step movement)
- Support multiple players (different Redis keys)

---

## 🛠️ Project Structure (example)

```
.
├── main.py
├── requirements-freeze.txt
└── README.md
```

---

## 🎮 Enjoy & Extend

This is a base prototype. Extend it with:
- AI-driven control
- Real-time video overlay
- Multiplayer synchronization
