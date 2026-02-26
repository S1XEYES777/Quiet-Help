from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO, emit
from cryptography.fernet import Fernet
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
# ---------- Шифрование ----------
key = Fernet.generate_key()
fernet = Fernet(key)

# ---------- ИИ-модель (LangChain + Mistral) ----------
from transformers import pipeline
from langchain_community.llms import HuggingFacePipeline

pipe = pipeline(
    "text-generation",
    model="mistralai/Mistral-7B-Instruct-v0.1",
    device=-1,  # CPU
    temperature=0.7,
    max_new_tokens=200,
    do_sample=True
)

llm = HuggingFacePipeline(pipeline=pipe)

prompt = PromptTemplate(
    input_variables=["user_message"],
    template="Ты анонимный помощник в кризисах. Ответь этично, без диагностики или лечения: {user_message}. Дай общие советы (дыхание, прогулки), перенаправь к специалистам в Казахстане (горячие линии +7 (7172) 55-55-55 для Астаны). Если город упомянут — предложи локальную помощь."
)

chain = LLMChain(llm=llm, prompt=prompt)

# ---------- Flask ----------
app = Flask(__name__)
socketio = SocketIO(app)

# ---------- Routes ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/states')
def states():
    return render_template('states.html')

@app.route('/cities')
def cities():
    return render_template('cities.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

# ---------- SocketIO ----------
@socketio.on('message')
def handle_message(data):
    try:
        encrypted_msg = data['msg']
        print("Зашифрованное:", encrypted_msg)
        
        decrypted_msg = fernet.decrypt(encrypted_msg.encode()).decode()
        print("Расшифрованное:", decrypted_msg)
        
        # ИИ-ответ
        response = chain.run(decrypted_msg)
        
        # Ограничения: Если кризис — добавь перенаправление
        if "кризис" in decrypted_msg.lower() or "стресс" in decrypted_msg.lower():
            response += " Обратитесь к локальным специалистам в разделе 'По городам'."
        
        emit('response', {'msg': response}, broadcast=False)
    except Exception as e:
        print("Ошибка:", str(e))
        emit('response', {'msg': 'Ошибка, попробуйте позже.'}, broadcast=False)

# ---------- Run ----------
if __name__ == '__main__':
    socketio.run(app, debug=True)