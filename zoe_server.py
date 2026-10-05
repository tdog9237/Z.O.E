"""
Z.O.E Application Server (Student Project Edition)
==================================================
Runs the web interface, local AI neural brain (Ollama),
face recognition retina scanner, and dynamic skill capability manager.
"""

import os
import sys
import json
import base64
import requests
import cv2
import numpy as np
import threading
from typing import Optional, Tuple
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from dotenv import load_dotenv

from skill_manager import SkillManager

# Load local environment configuration if present
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "zoe_ui")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

REGISTERED_FACE_PATH = os.path.join(DATA_DIR, "registered_face.png")
REGISTERED_NAME_PATH = os.path.join(DATA_DIR, "registered_name.txt")

# Initialize Flask application
app = Flask(__name__, static_folder=STATIC_DIR, static_url_path="")
CORS(app)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_cache_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Initialize the Student Capability Skill Manager
skill_manager = SkillManager(os.path.join(BASE_DIR, "skills"))

# ---------------------------------------------------------------------------
# Face Recognition & Haar Cascade Setup
# ---------------------------------------------------------------------------
def _load_cascade(filename: str):
    local_path = os.path.join(DATA_DIR, filename)
    if os.path.exists(local_path):
        return cv2.CascadeClassifier(local_path)
    if hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades'):
        cv_path = os.path.join(cv2.data.haarcascades, filename)
        if os.path.exists(cv_path):
            return cv2.CascadeClassifier(cv_path)
    return cv2.CascadeClassifier(filename)

face_cascade_default = _load_cascade('haarcascade_frontalface_default.xml')
face_cascade_alt2 = _load_cascade('haarcascade_frontalface_alt2.xml')


def recognize_user(image_data_b64: str) -> Tuple[Optional[str], str]:
    """Recognizes a registered user from a base64 webcam frame."""
    if not image_data_b64:
        return None, "undetected"

    try:
        if "," in image_data_b64:
            image_data_b64 = image_data_b64.split(",")[1]
        img_bytes = base64.b64decode(image_data_b64)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            return None, "undetected"

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade_default.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
        if len(faces) == 0 and face_cascade_alt2 is not None:
            faces = face_cascade_alt2.detectMultiScale(gray, 1.1, 3, minSize=(30, 30))

        if len(faces) == 0:
            return None, "not_detected"

        if not os.path.exists(REGISTERED_FACE_PATH) or not os.path.exists(REGISTERED_NAME_PATH):
            return None, "face_detected"

        with open(REGISTERED_NAME_PATH, "r", encoding="utf-8") as f:
            reg_name = f.read().strip()

        reg_face = cv2.imread(REGISTERED_FACE_PATH, cv2.IMREAD_GRAYSCALE)
        if reg_face is None:
            return None, "face_detected"

        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        current_crop = gray[y:y+h, x:x+w]

        cur_resized = cv2.resize(current_crop, (96, 96))
        reg_resized = cv2.resize(reg_face, (96, 96))

        cur_eq = cv2.equalizeHist(cur_resized)
        reg_eq = cv2.equalizeHist(reg_resized)

        center_reg = reg_eq[12:84, 12:84]
        match_res = cv2.matchTemplate(cur_eq, center_reg, cv2.TM_CCOEFF_NORMED)
        template_score = float(np.max(match_res)) if match_res is not None and match_res.size > 0 else 0.0

        s_cur = cv2.resize(cur_eq, (32, 32)).flatten()
        s_reg = cv2.resize(reg_eq, (32, 32)).flatten()
        corr_score = float(np.corrcoef(s_cur, s_reg)[0, 1]) if np.std(s_cur) > 0 and np.std(s_reg) > 0 else 0.0

        final_score = max(template_score, corr_score)
        if final_score >= 0.38:
            return reg_name, "matched"
        else:
            return reg_name, "unmatched"
    except Exception as e:
        print(f"[RECOGNITION] Error: {e}")
        return None, "error"


# ---------------------------------------------------------------------------
# Local Ollama AI Engine Integration
# ---------------------------------------------------------------------------
BASE_SYSTEM_PROMPT = """CRITICAL IDENTITY DIRECTIVE:
Your name is strictly Z.O.E (pronounced "Zoe").
You are Z.O.E, an intelligent, genuine, warm, and witty AI companion.
Under NO circumstances should you EVER say your name is anything else (such as Holli, Holly, Assistant, or a generic AI model).
Whenever someone asks who you are or introduces themselves, proudly identify yourself as Z.O.E.

TONE & PERSONALITY GUIDELINES:
1. Speak naturally, warmly, and conversationally.
2. Be concise, punchy, and lively (1–3 sentences for casual conversation).
3. GREETINGS: Always begin greetings naturally starting with 'Hi there!' or 'Hi!'. You must NEVER say 'Hello there'.
4. Do not use emojis in your responses under any circumstances, as they interfere with speech synthesis.
5. If the user asks about retail orders, shopping, store hours, or returns, remind them you have Project ORIS integration."""

conversation_history = []
last_used_model = "Local: Ollama (In-Memory)"


def get_ollama_addr() -> Tuple[str, int]:
    """Finds Ollama daemon address on localhost or WSL host gateway."""
    # 1. WSL localhost
    try:
        r = requests.get("http://127.0.0.1:11434/api/tags", timeout=0.5)
        if r.ok:
            return "127.0.0.1", 11434
    except Exception:
        pass

    # 2. Check WSL default gateway
    try:
        with open("/proc/net/route") as fh:
            for line in fh:
                fields = line.strip().split()
                if fields[1] == '00000000':
                    import socket, struct
                    gw = socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))
                    r = requests.get(f"http://{gw}:11434/api/tags", timeout=0.5)
                    if r.ok:
                        return gw, 11434
    except Exception:
        pass

    return "127.0.0.1", 11434


DEFAULT_MODEL = os.environ.get("ZOE_MODEL", "gemma3:270m")
PREFERRED_MODELS = [DEFAULT_MODEL, "gemma3:270m", "smollm2:360m", "qwen2.5:1.5b", "llama3.2:1b", "phi4-mini", "llama3.2:3b"]


def get_active_model() -> str:
    """
    Picks the model Z.O.E should use.
    1. First asks Ollama which model is ALREADY loaded in memory ('ollama ps').
       Using a model that is already loaded means replies start instantly.
    2. Otherwise picks the first installed model from PREFERRED_MODELS.
    """
    ip, port = get_ollama_addr()
    installed = []
    try:
        r = requests.get(f"http://{ip}:{port}/api/tags", timeout=1)
        if r.ok:
            installed = [m.get("name", "") for m in r.json().get("models", [])]
    except Exception:
        pass

    # 1. 'ollama ps' - models currently resident in memory
    try:
        r_ps = requests.get(f"http://{ip}:{port}/api/ps", timeout=1)
        if r_ps.ok:
            running = [m.get("name") or m.get("model") for m in r_ps.json().get("models", [])]
            for preferred in PREFERRED_MODELS:
                for name in running:
                    if name and name.startswith(preferred):
                        return name
    except Exception:
        pass

    # 2. Installed models in order of preference
    for preferred in PREFERRED_MODELS:
        for name in installed:
            if name.startswith(preferred):
                return name
    if installed:
        return installed[0]
    return DEFAULT_MODEL


def query_ollama(messages: list, model_name: str) -> str:
    """Sends the conversation to the local Ollama model and returns its reply."""
    ip, port = get_ollama_addr()
    url = f"http://{ip}:{port}/api/chat"
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "keep_alive": -1,  # keep the model loaded in memory forever (shows in 'ollama ps')
        "options": {"num_predict": 200, "temperature": 0.7},
    }
    try:
        r = requests.post(url, json=payload, timeout=60)
        if r.ok:
            return r.json().get("message", {}).get("content", "").strip()
        return f"Ollama returned error status {r.status_code}: {r.text[:150]}"
    except Exception:
        return ("Local Ollama is not running. Start it with 'ollama serve' "
                f"and download the model with 'ollama pull {DEFAULT_MODEL}'.")


def warm_up_model() -> None:
    """Loads the model into memory at start-up so the first reply is fast."""
    model = get_active_model()
    ip, port = get_ollama_addr()
    try:
        requests.post(f"http://{ip}:{port}/api/generate",
                      json={"model": model, "prompt": "", "keep_alive": -1}, timeout=120)
        print(f"[Z.O.E] Model '{model}' loaded into memory (check with: ollama ps)")
    except Exception as e:
        print(f"[Z.O.E] Could not pre-load model '{model}': {e}")


# ---------------------------------------------------------------------------
# API Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/api/skills", methods=["GET"])
def get_skills():
    """Lists all dynamically loaded capabilities."""
    return jsonify({
        "count": len(skill_manager.skills),
        "skills": skill_manager.list_skills()
    })


@app.route("/api/skills/reload", methods=["POST"])
def reload_skills():
    """Hot-reloads all student capabilities without restarting."""
    skill_manager.reload()
    return jsonify({
        "status": "success",
        "message": f"Successfully reloaded {len(skill_manager.skills)} capabilities.",
        "skills": skill_manager.list_skills()
    })


@app.route("/recognize_face", methods=["POST"])
def api_recognize_face():
    data = request.json or {}
    image_data_b64 = data.get("image_data", "")
    user_name, status = recognize_user(image_data_b64)
    reg_name = None
    if os.path.exists(REGISTERED_NAME_PATH):
        try:
            with open(REGISTERED_NAME_PATH, "r", encoding="utf-8") as f:
                reg_name = f.read().strip()
        except Exception:
            pass

    return jsonify({
        "status": status,
        "matched": (status == "matched"),
        "name": user_name or reg_name or "",
        "registered_user": reg_name
    })


@app.route("/register_face", methods=["POST"])
def api_register_face():
    data = request.json or {}
    name = data.get("name", "Student").strip()
    image_data_b64 = data.get("image_data", "")

    if not image_data_b64:
        return jsonify({"error": "No webcam image provided"}), 400

    try:
        if "," in image_data_b64:
            image_data_b64 = image_data_b64.split(",")[1]
        img_bytes = base64.b64decode(image_data_b64)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({"error": "Failed to decode image"}), 400

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade_default.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
        if len(faces) == 0 and face_cascade_alt2 is not None:
            faces = face_cascade_alt2.detectMultiScale(gray, 1.1, 3, minSize=(30, 30))

        if len(faces) == 0:
            return jsonify({"error": "No face detected in camera frame. Please look directly at the webcam."}), 400

        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        face_crop = gray[y:y+h, x:x+w]
        face_resized = cv2.resize(face_crop, (96, 96))

        cv2.imwrite(REGISTERED_FACE_PATH, face_resized)
        with open(REGISTERED_NAME_PATH, "w", encoding="utf-8") as f:
            f.write(name)

        return jsonify({"success": True, "message": f"Face registered successfully as {name}!"})
    except Exception as e:
        return jsonify({"error": f"Internal error during registration: {str(e)}"}), 500


@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history, last_used_model
    data = request.json or {}
    user_message = data.get("message", "").strip()
    image_data = data.get("image_data", "")

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    # 1. Recognize user from frame
    user_name, face_status = recognize_user(image_data)
    context = {"user_name": user_name, "face_status": face_status}

    # 2. Check Student Skills first (Skill Expansion Layer)
    skill_result = skill_manager.route_message(user_message, context=context)
    if skill_result:
        skill, reply_text = skill_result
        conversation_history.append({"role": "user", "content": user_message})
        conversation_history.append({"role": "assistant", "content": reply_text})
        last_used_model = f"Skill: {skill.name}"
        return jsonify({
            "reply": reply_text,
            "model": last_used_model,
            "skill": skill.name,
            "avatar_url": "native"
        })

    # 3. Fallback to Local AI (Ollama)
    visual_context = ""
    if face_status == "matched":
        visual_context = f"\n[SYSTEM NOTICE: You visually recognize the user via camera as '{user_name}'. Greet them by name naturally.]\n"
    elif face_status == "unmatched":
        visual_context = f"\n[SYSTEM NOTICE: A face is detected, but does not match the registered user '{user_name}'.]\n"

    conversation_history.append({"role": "user", "content": user_message})
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]

    messages = [{"role": "system", "content": BASE_SYSTEM_PROMPT + visual_context}] + conversation_history
    active_model = get_active_model()
    last_used_model = f"Ollama: {active_model}"

    reply = query_ollama(messages, active_model)
    conversation_history.append({"role": "assistant", "content": reply})

    return jsonify({
        "reply": reply,
        "model": last_used_model,
        "skill": None,
        "avatar_url": "native"
    })


@app.route("/tts", methods=["GET"])
def tts():
    """Streams Edge-TTS voice audio in real time."""
    text = request.args.get("text", "")
    voice = request.args.get("voice", "en-US-AriaNeural")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    def generate():
        import subprocess
        process = subprocess.Popen(
            [sys.executable, "-m", "edge_tts", "--voice", voice, "--text", text],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        while True:
            chunk = process.stdout.read(4096)
            if not chunk:
                break
            yield chunk

    return Response(generate(), mimetype="audio/mpeg")


@app.route("/status", methods=["GET"])
def status():
    ollama_active = False
    active_model = ""
    try:
        ip, port = get_ollama_addr()
        r = requests.get(f"http://{ip}:{port}/api/tags", timeout=1)
        if r.ok:
            ollama_active = True
            active_model = get_active_model()
    except Exception:
        pass

    reg_user = None
    if os.path.exists(REGISTERED_NAME_PATH):
        try:
            with open(REGISTERED_NAME_PATH, "r", encoding="utf-8") as f:
                reg_user = f.read().strip()
        except Exception:
            pass

    return jsonify({
        "server_active": True,
        "ollama_active": ollama_active,
        "active_model": active_model,
        "last_used_model": last_used_model,
        "registered_user": reg_user,
        "skills_loaded": len(skill_manager.skills),
        "conversation_turns": len(conversation_history) // 2
    })


@app.route("/models", methods=["GET"])
def get_available_models():
    ip, port = get_ollama_addr()
    models = []
    try:
        r = requests.get(f"http://{ip}:{port}/api/tags", timeout=1)
        if r.ok:
            for item in r.json().get("models", []):
                name = item.get("name", "")
                if name:
                    models.append({"name": f"Local: {name}", "value": f"ollama:{name}"})
    except Exception:
        pass

    return jsonify({
        "groups": [
            {
                "label": "Local Models",
                "options": models or [{"name": "Auto (Ollama)", "value": "auto"}]
            }
        ]
    })


@app.route("/reset", methods=["POST"])
def reset():
    global conversation_history
    conversation_history = []
    return jsonify({"status": "reset", "message": "Conversation history cleared."})


if __name__ == "__main__":
    print("==========================================================")
    print("  Z.O.E Server (Student Project Edition)")
    print(f"  Loaded Capabilities: {len(skill_manager.skills)}")
    print(f"  Web Interface: http://localhost:{os.environ.get('ZOE_PORT', 5001)}")
    print("==========================================================")
    threading.Thread(target=warm_up_model, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("ZOE_PORT", 5001)), debug=False, use_reloader=False)
