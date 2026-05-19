#!/bin/bash

# ACR - Autobiographical Cognitive Runtime
# Installer Script

set -e

echo "🚀 Starting ACR Installation..."

# 1. Update and install system dependencies
echo "📦 Installing system dependencies (Redis, Python, Venv)..."
sudo apt-get update
sudo apt-get install -y redis-server python3-pip python3-venv build-essential curl

# 2. Setup directory
INSTALL_DIR="$HOME/acr"
if [ ! -d "$INSTALL_DIR" ]; then
    echo "📂 Creating ACR directory at $INSTALL_DIR..."
    mkdir -p "$INSTALL_DIR"
fi

# 3. Virtual Environment setup
echo "🐍 Setting up Python Virtual Environment..."
python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/activate"
pip install --upgrade pip
pip install redis openai rich pydantic-settings streamlit uvicorn fastapi

# 4. Environment variables setup
if [ ! -f "$INSTALL_DIR/.env" ]; then
    echo "🔑 Creating .env file..."
    read -p "Enter your OpenRouter API Key (leave blank to set later): " API_KEY
    echo "OPENROUTER_API_KEY='$API_KEY'" > "$INSTALL_DIR/.env"
    echo "REDIS_HOST='localhost'" >> "$INSTALL_DIR/.env"
fi

# 5. Create the 'acr' command alias
echo "🛠️ Creating 'acr' alias..."
SHELL_RC="$HOME/.bashrc"
if [ -f "$HOME/.zshrc" ]; then
    SHELL_RC="$HOME/.zshrc"
fi

# Define the helper function content
cat << 'EOF' > "$INSTALL_DIR/acr_cmd.sh"
#!/bin/bash
ACR_PATH="$HOME/acr"
source "$ACR_PATH/venv/bin/activate"
export PYTHONPATH=$PYTHONPATH:$ACR_PATH
export $(grep -v '^#' "$ACR_PATH/.env" | xargs)

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
        echo "🩺 ACR Doctor - Diagnostic Report"
        echo "-------------------------------"
        # Check Redis
        if redis-cli ping > /dev/null 2>&1; then echo "✅ Redis: Running"; else echo "❌ Redis: NOT RUNNING"; fi
        # Check .env
        if [ -f "$ACR_PATH/.env" ]; then echo "✅ Config: .env found"; else echo "❌ Config: .env MISSING"; fi
        # Check Memory DB
        if [ -f "$ACR_PATH/acr_memory.db" ]; then echo "✅ Memory: Database found"; else echo "ℹ️ Memory: Database not yet created"; fi
        # Check Venv
        if [ -d "$ACR_PATH/venv" ]; then echo "✅ Environment: Venv found"; else echo "❌ Environment: Venv MISSING"; fi
        ;;
    upgrade)
        echo "⬆️ Upgrading ACR..."
        # 1. Git Pull (if git repo)
        if [ -d "$ACR_PATH/.git" ]; then
            echo "📥 Pulling latest code from GitHub..."
            git -C "$ACR_PATH" pull
        else
            echo "ℹ️ Not a git repository, skipping code pull."
        fi
        # 2. Update Python dependencies
        echo "📦 Updating dependencies..."
        "$ACR_PATH/venv/bin/pip" install --upgrade pip
        if [ -f "$ACR_PATH/requirements.txt" ]; then
            "$ACR_PATH/venv/bin/pip" install -r "$ACR_PATH/requirements.txt"
        else
            # Fallback to core deps
            "$ACR_PATH/venv/bin/pip" install redis openai rich pydantic-settings streamlit uvicorn fastapi
        fi
        echo "✅ Upgrade complete! Config and memory preserved."
        ;;
    *)
        echo "Usage: acr {start|stop|chat|logs|doctor|upgrade}"
        ;;
esac
EOF

chmod +x "$INSTALL_DIR/acr_cmd.sh"

# Add to shell profile if not exists
if ! grep -q "alias acr=" "$SHELL_RC"; then
    echo "alias acr='$INSTALL_DIR/acr_cmd.sh'" >> "$SHELL_RC"
    echo "✅ Alias 'acr' added to $SHELL_RC"
else
    echo "ℹ️ Alias 'acr' already exists in $SHELL_RC"
fi

echo "✨ Installation complete!"
echo "👉 Run 'source $SHELL_RC' to activate the 'acr' command."
echo "👉 Then use 'acr start' to begin."
