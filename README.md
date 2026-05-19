# ACR - Autobiographical Cognitive Runtime 🧠

ACR is a production-quality, research-grade cognitive agent system designed for persistent, continuous multi-agent coordination.

## 🚀 Quick Install

To install ACR on a Debian 13 (or compatible) system, simply run:

```bash
curl -fsSL https://raw.githubusercontent.com/danni333/acr/main/scripts/install.sh | bash
```

*Note: After installation, restart your terminal or run `source ~/.bashrc` to activate the `acr` command.*

## 🛠️ Commands

Once installed, you can use the `acr` CLI to manage the cognitive runtime:

| Command | Description |
|---------|-------------|
| `acr start` | Starts the cognitive kernel in the background |
| `acr chat` | Opens the interactive terminal chat interface |
| `acr logs` | Shows real-time system reasoning and agent logs |
| `acr doctor` | Runs a system diagnostic check |
| `acr upgrade` | Safely updates code and dependencies |
| `acr stop` | Safely shuts down the kernel and agents |

## 🧠 Architecture

ACR implements a modular cognitive architecture based on:
- **Autobiographical Memory**: Episodic, Semantic, and Procedural layers stored in SQLite.
- **Causal Reasoning**: Tracing event ancestry for explainable agent actions.
- **OpenCode Integration**: Autonomous code execution and file manipulation.
- **Event Bus**: Redis-based pub/sub for agent communication.

## 📁 Project Structure

- `acr/core/`: Kernel, Event Bus, and Runtime logic.
- `acr/agents/`: Specialized agents (Planner, Critic, Executor, etc.).
- `acr/memory/`: 3-layer memory management system.
- `acr/tools/`: Integration with external tools (CodeExecutor).
- `workspace/`: Isolated directory for agent-generated files.

## 📄 License
MIT License.
