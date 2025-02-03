import json
import os
import openai
import cv2
import numpy as np
from flask import Flask, render_template, Response

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json! Ustaw API OpenAI.")
    exit(1)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

OPENAI_API_KEY = config["OPENAI_API_KEY"]
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

def generate_ai_face():
    """Generuje interaktywne AI Wizjonera (Zordon AI)"""
    face = np.zeros((500, 500, 3), dtype=np.uint8)
    cv2.putText(face, "RLdC AI", (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    return face

def video_stream():
    """Strumieniuje obraz AI Wizjonera"""
    while True:
        frame = generate_ai_face()
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index():
    """Strona główna Zordon AI"""
    return render_template('zordon_ai.html')

@app.route('/video_feed')
def video_feed():
    """Strumień wideo"""
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
