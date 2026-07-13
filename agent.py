import sys
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject

# --- 1. THE DESKTOP AVATAR (PyQt6) ---
class MascotWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # Make it stay on top, borderless, and transparent
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Load the Avatar Image
        self.layout = QVBoxLayout()
        self.label = QLabel()
        self.label.setStyleSheet("background-image: url('witch.png'); background-repeat: no-repeat; background-position: center; border: none;")
        self.label.setFixedSize(150, 150) # Adjust to fit your image
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        
        self.dragging = False
        self.offset = QPoint()

        # Start hidden. The website will tell it to show!
        self.hide()

    # Dragging logic
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.dragging = False

# We use a Signal to safely talk between the Web Server thread and the UI thread
class SignalManager(QObject):
    launch_signal = pyqtSignal()

# --- 2. THE LOCAL WEB SERVER (FastAPI) ---
app = FastAPI()

# VERY IMPORTANT: Allow your Vercel/GitHub website to talk to your local computer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace "*" with your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

signal_manager = SignalManager()

@app.post("/launch")
async def launch_agent():
    # When the website clicks the button, trigger the PyQt window to appear
    signal_manager.launch_signal.emit()
    return {"status": "success", "message": "Avatar launched on desktop!"}

def run_server():
    # Run FastAPI on port 8000 without blocking the UI
    uvicorn.run(app, host="127.0.0.1", port=8000)

# --- 3. START EVERYTHING ---
if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    
    # Create the avatar window
    mascot = MascotWidget()
    
    # Connect the web server signal to the UI's 'show' function
    signal_manager.launch_signal.connect(mascot.show)
    
    # Start the web server in the background so it doesn't freeze the UI
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    print("Arcane OS Bridge Running. Waiting for website launch command...")
    
    # Start the Desktop UI Loop
    sys.exit(qt_app.exec())
