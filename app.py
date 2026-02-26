import os
import requests
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

API_KEY = os.environ.get("OPENROUTER_API_KEY")

def query_ai(message):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek/deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "Ты спокойный и поддерживающий помощник. Не ставь диагноз и не назначай лечение."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                "temperature": 0.7
            },
            timeout=30
        )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception:
        return "Ошибка соединения. Попробуйте позже."

@app.route("/")
def home():
    return render_template("index.html")

@socketio.on("message")
def handle_message(data):
    user_msg = data.get("msg", "")
    ai_response = query_ai(user_msg)
    emit("response", {"msg": ai_response})

if __name__ == "__main__":
    socketio.run(app)
