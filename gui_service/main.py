import sys
import random
import redis
import os
import logging
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter, QColor, QPen, QFont

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [GUI] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("game.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# --- Configuration from Environment Variables ---
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_KEY = "aim_direction"


class AimGame(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Aim Controller")
        self.setGeometry(100, 100, 600, 400)

        # Redis client
        self.redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
        logger.info(f"Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")

        # Aim position (center)
        self.aim_x = self.width() // 2
        self.aim_y = self.height() // 2

        # Random goal
        self.goal_x = random.randint(50, 550)
        self.goal_y = random.randint(50, 350)

        # Score
        self.score = 0

        # Timer for updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_from_redis)
        self.timer.start(50)  # 20 FPS

        logger.info("Game started. Waiting for hand input...")

    def update_from_redis(self):
        direction = self.redis_client.getset(REDIS_KEY, "")

        step = 5

        # Move aim based on direction
        if direction == "LEFT":
            self.aim_x -= step
        elif direction == "RIGHT":
            self.aim_x += step
        elif direction == "UP":
            self.aim_y -= step
        elif direction == "DOWN":
            self.aim_y += step

        # Restrict aim to window borders
        self.aim_x = max(0, min(self.aim_x, self.width()))
        self.aim_y = max(0, min(self.aim_y, self.height()))

        # Check if aim reached goal
        if (self.aim_x - self.goal_x) ** 2 + (self.aim_y - self.goal_y) ** 2 <= 15 ** 2:
            self.score += 1
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"SCORE! Total score: {self.score} at {timestamp}")

            # Move goal to new random position
            self.goal_x = random.randint(50, self.width() - 50)
            self.goal_y = random.randint(50, self.height() - 50)
            logger.info(f"New goal position: ({self.goal_x}, {self.goal_y})")

        self.update()  # trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)

        # Draw background
        painter.fillRect(self.rect(), QColor(30, 30, 30))

        # Draw goal (red circle)
        painter.setBrush(QColor(200, 50, 50))
        painter.drawEllipse(self.goal_x - 10, self.goal_y - 10, 20, 20)

        # Draw aim (crosshair)
        painter.setPen(QPen(QColor(50, 200, 50), 2))
        size = 10
        painter.drawLine(self.aim_x - size, self.aim_y, self.aim_x + size, self.aim_y)
        painter.drawLine(self.aim_x, self.aim_y - size, self.aim_x, self.aim_y + size)

        # Draw score
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 16))
        painter.drawText(10, 30, f"Score: {self.score}")

    def closeEvent(self, event):
        logger.info(f"Game ended. Final score: {self.score}")
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AimGame()
    window.show()
    sys.exit(app.exec_())