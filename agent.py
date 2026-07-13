import sys
import os
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject

# Get the absolute path to the directory where this script lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Build the exact path to the image
IMAGE_PATH = os.path.join(BASE_DIR, "witch.png")

# --- 1. THE DESKTOP AVATAR (PyQt6) ---
class MascotWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.layout = QVBoxLayout()
        self.label = QLabel()
        
        # Use the absolute path for the image so it never fails to load
        # We replace backslashes with forward slashes for PyQt styling
        css_path = IMAGE_PATH.replace("\\", "/")
        self.label.setStyleSheet(f"background-image: url('{css_path}'); background-repeat: no-repeat; background-position: center; border: none;")
        self.label.setFixedSize(150, 150)
        
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        
        self.dragging = False
        self.offset = QPoint()
        self.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.dragging = False

class SignalManager(QObject):
    launch_signal = pyqtSignal()

# --- 2. THE LOCAL WEB SERVER (FastAPI) ---
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows your Vercel URL to talk to your local laptop
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

signal_manager = SignalManager()

@app.post("/launch")
async def launch_agent():
    signal_manager.launch_signal.emit()
    return {"status": "success"}

def run_server():
    # Bind specifically to 127.0.0.1 to match the website's fetch request
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    mascot = MascotWidget()
    signal_manager.launch_signal.connect(mascot.show)
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print(f"Arcane OS Bridge Running. Looking for image at: {IMAGE_PATH}")
    sys.exit(qt_app.exec())
