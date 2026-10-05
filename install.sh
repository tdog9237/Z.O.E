#!/usr/bin/env bash
# ============================================================
#  Z.O.E Student Edition - One-time installer for WSL (Ubuntu)
#  Run from inside the project folder:   bash install.sh
# ============================================================
set -e
cd "$(dirname "$0")"

MODEL="${ZOE_MODEL:-phi4-mini}"
if [ -f .env ]; then
  ENV_MODEL=$(grep -E '^ZOE_MODEL=' .env | cut -d= -f2- || true)
  [ -n "$ENV_MODEL" ] && MODEL="$ENV_MODEL"
fi

say() { echo -e "\n\033[1;36m[Z.O.E SETUP]\033[0m $1"; }

say "Step 1/5: Installing system tools (you may be asked for your Ubuntu password)..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-venv python3-pip curl zstd git

say "Step 2/5: Checking Ollama (the program that runs the AI model on your computer)..."
if curl -s --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null; then
  echo "Ollama is already running."
elif command -v ollama >/dev/null 2>&1; then
  echo "Ollama is installed - starting it in the background..."
  (nohup ollama serve >/tmp/ollama.log 2>&1 &)
  sleep 3
else
  echo "Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
  if ! curl -s --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null; then
    (nohup ollama serve >/tmp/ollama.log 2>&1 &)
    sleep 3
  fi
fi

say "Step 3/5: Downloading Z.O.E's brain: '$MODEL' (one-time download, a few GB)..."
ollama pull "$MODEL"

say "Step 4/5: Creating a Python virtual environment (.venv) and installing libraries..."
python3 -m venv .venv
. .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt -q

say "Step 5/6: Installing the WebRTC Avatar Renderer..."
if [ ! -d "avatar-streamer" ]; then
  git clone https://github.com/avaturn-live/avtr-1.git avatar-streamer
  echo "Avatar streamer downloaded to 'avatar-streamer/'."
  echo "Note: You will need 'pixi' installed to run the interactive-demo later."
else
  echo "Avatar streamer already exists."
fi

say "Step 6/6: Running the automated skill tests..."
python3 test_skills.py

say "All done! Start Z.O.E any time with:   bash start.sh"
