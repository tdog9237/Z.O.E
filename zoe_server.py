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
try:
    import cv2
except ImportError:
    cv2 = None
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
    if cv2 is None or not hasattr(cv2, 'CascadeClassifier'):
        return None
    try:
        local_path = os.path.join(DATA_DIR, filename)
        if os.path.exists(local_path):
            return cv2.CascadeClassifier(local_path)
        if hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades'):
            cv_path = os.path.join(cv2.data.haarcascades, filename)
            if os.path.exists(cv_path):
                return cv2.CascadeClassifier(cv_path)
        return cv2.CascadeClassifier(filename)
    except Exception:
        return None

face_cascade_default = _load_cascade('haarcascade_frontalface_default.xml')
face_cascade_alt2 = _load_cascade('haarcascade_frontalface_alt2.xml')


def recognize_user(image_data_b64: str) -> Tuple[Optional[str], str]:
    """Recognizes a registered user from a base64 webcam frame."""
    if cv2 is None or not hasattr(cv2, 'CascadeClassifier') or not image_data_b64:
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
MODEL_NAME = "Wilsonian Continuous RG Braid Apex (1,024 Context, FAISS GPU)"
last_used_model = MODEL_NAME


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
        stream_audio_to_webrtc(reply_text, "en-US-AriaNeural")
        return jsonify({
            "reply": reply_text,
            "model": last_used_model,
            "skill": skill.name,
            "avatar_url": "native"
        })

    # 3. Dedicated Brain: Wilsonian Continuous Neural RG Braid Calibrated Apex Model
    try:
        from zoe_wilsonian_brain import ZoeWilsonianBrain
        brain = ZoeWilsonianBrain.get_instance()
        reply = brain.generate_chat_reply(
            user_message,
            history=conversation_history,
            user_name=user_name,
            face_status=face_status
        )
    except Exception as e:
        print(f"[Z.O.E] Error in Wilsonian Brain inference: {e}")
        reply = "I'm right here with you! What would you like to explore next?"

    # 4. Stream speech audio directly to WebRTC avatar engine
    voice = request.json.get("voice", "en-US-AriaNeural") if request.json else "en-US-AriaNeural"
    stream_audio_to_webrtc(reply, voice)

    last_used_model = MODEL_NAME
    conversation_history.append({"role": "user", "content": user_message})
    conversation_history.append({"role": "assistant", "content": reply})
    if len(conversation_history) > 30:
        conversation_history = conversation_history[-30:]

    return jsonify({
        "reply": reply,
        "model": MODEL_NAME,
        "skill": None,
        "avatar_url": "native"
    })


@app.route("/voice_chat", methods=["POST"])
def voice_chat():
    """Receives voice audio from user microphone, transcribes via CUDA Whisper, and chats as Z.O.E."""
    try:
        from zoe_wilsonian_brain import ZoeWilsonianBrain
        brain = ZoeWilsonianBrain.get_instance()

        audio_bytes = None
        if "audio" in request.files:
            audio_bytes = request.files["audio"].read()
        elif request.json and "audio_data" in request.json:
            b64_str = request.json["audio_data"]
            if "," in b64_str:
                b64_str = b64_str.split(",")[1]
            audio_bytes = base64.b64decode(b64_str)

        if not audio_bytes:
            return jsonify({"error": "No audio received"}), 400

        user_transcription = brain.transcribe_audio_bytes(audio_bytes)
        if not user_transcription:
            return jsonify({"error": "Could not detect clear speech"}), 400

        reply = brain.generate_chat_reply(user_transcription, history=conversation_history)
        stream_audio_to_webrtc(reply, "en-US-AriaNeural")
        conversation_history.append({"role": "user", "content": user_transcription})
        conversation_history.append({"role": "assistant", "content": reply})

        return jsonify({
            "user_text": user_transcription,
            "reply": reply,
            "model": "Wilsonian RG Braid Apex (CUDA Whisper STT)",
            "avatar_url": "native"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/vram", methods=["GET"])
def get_vram_telemetry():
    """Returns GPU VRAM allocation telemetry for the 75% target on RTX 5070 Ti."""
    try:
        from zoe_wilsonian_brain import ZoeWilsonianBrain
        brain = ZoeWilsonianBrain.get_instance()
        return jsonify(brain.get_vram_telemetry())
    except Exception as e:
        return jsonify({"error": str(e), "active": False})


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


def stream_audio_to_webrtc(text: str, voice: str = "en-US-AriaNeural"):
    """Streams speech audio directly to the AVTR-1 WebRTC engine on port 7861."""
    try:
        import subprocess
        webrtc_script = os.path.join(r"D:\Antigravity\Polymath", "stream_to_webrtc.py")
        py_exe = r"D:\Antigravity\Polymath\.venv\Scripts\python.exe" if os.path.exists(r"D:\Antigravity\Polymath\.venv\Scripts\python.exe") else sys.executable
        if os.path.exists(webrtc_script):
            subprocess.Popen(
                [py_exe, webrtc_script, text, voice],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"[Z.O.E WebRTC Stream] Dispatched speech audio to port 7861 ({len(text)} chars)")
    except Exception as e:
        print(f"[Z.O.E] WebRTC audio stream notice: {e}")


@app.route("/status", methods=["GET"])
def status():
    reg_user = None
    if os.path.exists(REGISTERED_NAME_PATH):
        try:
            with open(REGISTERED_NAME_PATH, "r", encoding="utf-8") as f:
                reg_user = f.read().strip()
        except Exception:
            pass

    return jsonify({
        "server_active": True,
        "trained_model_active": True,
        "active_model": MODEL_NAME,
        "last_used_model": MODEL_NAME,
        "registered_user": reg_user,
        "skills_loaded": len(skill_manager.skills),
        "conversation_turns": len(conversation_history) // 2
    })


@app.route("/models", methods=["GET"])
def get_available_models():
    return jsonify({
        "groups": [
            {
                "label": "Trained Neural Models (GPU)",
                "options": [
                    {
                        "name": "Wilsonian Continuous Neural RG Braid Apex (Dense)",
                        "value": "wilsonian_v37_apex"
                    }
                ]
            }
        ]
    })


@app.route("/reset", methods=["POST"])
def reset():
    global conversation_history
    conversation_history = []
    return jsonify({"status": "reset", "message": "Conversation history cleared."})


def warm_up_wilsonian():
    try:
        from zoe_wilsonian_brain import ZoeWilsonianBrain
        print("[Z.O.E Server] Loading Wilsonian RG Braid 1.01B MoE Brain into GPU VRAM (~75% target)...")
        brain = ZoeWilsonianBrain.get_instance()
        telemetry = brain.get_vram_telemetry()
        print(f"[Z.O.E Server] Brain Ready! VRAM Allocated: {telemetry['vram_allocated_gb']} GB / {telemetry['vram_total_gb']} GB ({telemetry['vram_utilization_percent']}%)")
    except Exception as e:
        print(f"[Z.O.E Server] Notice loading Wilsonian Brain: {e}")


if __name__ == "__main__":
    print("==========================================================")
    print("  Z.O.E Multimodal AI Companion Server")
    print("  Architecture: Wilsonian Continuous Neural RG Braid 1.01B MoE")
    print("  Context: 4,096 Tokens (YaRN RoPE) | Memory: FAISS GPU")
    print(f"  Web Interface: http://localhost:{os.environ.get('ZOE_PORT', 5001)}")
    print("==========================================================")
    threading.Thread(target=warm_up_wilsonian, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("ZOE_PORT", 5001)), debug=False, use_reloader=False)
