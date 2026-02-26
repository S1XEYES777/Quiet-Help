import os
import requests
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

# ---------- Flask ----------
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# ---------- HuggingFace ----------
HF_TOKEN = os.environ.get("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

def query_hf(prompt):
    response = requests.post(
        API_URL,
        headers=headers,
        json={"inputs": prompt}
    )

    result = response.json()

    if isinstance(result, list):
        return result[0]["generated_text"]
    elif "error" in result:
        return "Модель загружается или превышен лимит. Попробуйте позже."
    else:
        return "Ошибка ответа модели."

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

# ---------- Socket ----------
@socketio.on('message')
def handle_message(data):
    try:
        user_msg = data['msg']

        prompt = f"""
Ты анонимный помощник психологической поддержки.
Не ставь диагноз.
Не назначай лечение.
Дай мягкие советы (дыхание, прогулка).
Если кризис — предложи обратиться к специалистам в Казахстане
(горячая линия Астана +7 (7172) 55-55-55).

Сообщение пользователя: {user_msg}
"""

        ai_response = query_hf(prompt)

        emit('response', {'msg': ai_response})

    except Exception:
        emit('response', {'msg': 'Ошибка. Попробуйте позже.'})

# ---------- Run ----------
if __name__ == '__main__':
    socketio.run(app)
