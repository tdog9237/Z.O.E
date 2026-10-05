#!/usr/bin/env bash
# ============================================================
#  Z.O.E Student Edition - start the app
#  Run from inside the project folder:   bash start.sh
#  Then open http://localhost:5001 in Chrome or Edge on Windows.
# ============================================================
cd "$(dirname "$0")"

if [ ! -d .venv ]; then
  echo "Z.O.E is not installed yet. Run:  bash install.sh"
  exit 1
fi

# Make sure Ollama is running
if ! curl -s --max-time 2 http://127.0.0.1:11434/api/tags >/dev/null; then
  echo "[Z.O.E] Starting Ollama in the background..."
  (nohup ollama serve >/tmp/ollama.log 2>&1 &)
  sleep 3
fi

# Start WebRTC Avatar Streamer if installed
if [ -d "avatar-streamer" ]; then
  echo "[Z.O.E] Starting WebRTC Avatar Streamer in the background..."
  export STREAMER_HOST=0.0.0.0
  (cd avatar-streamer && ~/.pixi/bin/pixi run interactive-demo >/tmp/avatar-streamer.log 2>&1 &)
fi

. .venv/bin/activate
echo "[Z.O.E] Open http://localhost:5001 in your browser. Press Ctrl+C to stop."
python3 zoe_server.py
