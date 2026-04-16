# 🖐️ Hand-Gesture Mouse Controller

A Human-Computer Interaction (HCI) system built with Python that allows remote control of the operating system cursor using hand gestures. This project completely eliminates the need for physical input devices, using real-time Computer Vision.

## 🚀 Features

*   **Real-Time Tracking:** Utilizes Google's MediaPipe for precise hand landmark detection.
*   **Fluid Cursor Movement:** Implements a moving average smoothing algorithm to eliminate the jittering typically associated with vision systems.
*   **Pinch-to-Click:** Simulates a standard mouse click by calculating the Euclidean distance between the thumb and index finger.
*   **Drag-and-Drop:** Built-in logic allows holding the pinch gesture to perform drag-and-drop actions seamlessly.
*   **Auto-Setup:** The script automatically handles the download of the required MediaPipe model (hand_landmarker.task) upon the first run.

## 🛠️ Tech Stack

*   **Python:** Core logic.
*   **OpenCV (cv2):** Video capture, image processing, and HUD rendering.
*   **MediaPipe:** Hand landmark detection and tracking.
*   **PyAutoGUI:** OS-level mouse control and automation.

## 💻 How to Run

1. **Clone the repository:**
   git clone https://github.com/FedeTaiola/Hand-Gesture-Mouse-Controller.git
   cd Hand-Gesture-Mouse-Controller

2. **Install the dependencies:**
   pip install opencv-python mediapipe pyautogui

3. **Run the application:**
   python main.py

## 🎮 Controls
*   **Move Cursor:** Point with your index finger.
*   **Click:** Briefly pinch your thumb and index finger together.
*   **Drag & Drop:** Pinch and hold, then move your hand.
*   **Quit:** Press ESC to close.
