#!/bin/bash
ACR_PATH="/home/tob/acr"
source "$ACR_PATH/venv/bin/activate"
export PYTHONPATH=$PYTHONPATH:$ACR_PATH
if [ -f "$ACR_PATH/.env" ]; then
    export $(grep -v '^#' "$ACR_PATH/.env" | xargs) > /dev/null 2>&1
fi

case "$1" in
    start)
        echo "🧠 Starting ACR Kernel..."
        python3 -m acr.main > "$ACR_PATH/runtime.log" 2>&1 &
        echo $! > "$ACR_PATH/acr.pid"
        echo "ACR is running in background. PID: $(cat "$ACR_PATH/acr.pid")"
        ;;
    stop)
        if [ -f "$ACR_PATH/acr.pid" ]; then
            echo "🛑 Stopping ACR..."
            kill $(cat "$ACR_PATH/acr.pid") && rm "$ACR_PATH/acr.pid"
            echo "ACR stopped."
        else
            echo "ACR is not running."
        fi
        ;;
    chat)
        python3 "$ACR_PATH/scripts/terminal_chat.py"
        ;;
    logs)
        tail -f "$ACR_PATH/runtime.log"
        ;;
    doctor)
        python3 -m acr.core.doctor
        ;;
    upgrade)
        echo "⬆️ Upgrading ACR..."
        if [ -d "$ACR_PATH/.git" ]; then
            echo "📥 Pulling latest code from GitHub..."
            git -C "$ACR_PATH" pull
        fi
        echo "📦 Updating dependencies..."
        "$ACR_PATH/venv/bin/pip" install --upgrade pip
        if [ -f "$ACR_PATH/requirements.txt" ]; then
            "$ACR_PATH/venv/bin/pip" install -r "$ACR_PATH/requirements.txt"
        else
            "$ACR_PATH/venv/bin/pip" install redis openai rich pydantic-settings streamlit uvicorn fastapi prompt_toolkit chromadb sentence-transformers
        fi
        echo "✅ Upgrade complete! Config and memory preserved."
        ;;
    *)
        echo "Usage: acr {start|stop|chat|logs|doctor|upgrade}"
        ;;
esac
