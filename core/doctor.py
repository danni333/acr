import os
import redis
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel
from acr.core.ui_system import ACR_THEME, get_header
from acr.core.llm import LLMClient

console = Console(theme=ACR_THEME)

def run_doctor():
    console.print(get_header())
    
    ACR_PATH = "/home/tob/acr"
    issues_found = []
    
    table = Table(title="[info]ACR System Health Check[/info]", border_style="info")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Action Taken", style="green")

    # 1. Check Redis
    redis_status = "[success]ONLINE[/success]"
    action_redis = "None"
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=2)
        r.ping()
    except:
        redis_status = "[warning]OFFLINE[/warning]"
        action_redis = "Proposta: sudo systemctl start redis-server"
        issues_found.append("Redis is offline")
    table.add_row("Redis Bus", redis_status, action_redis)

    # 2. Check Config (.env)
    env_path = os.path.join(ACR_PATH, ".env")
    env_status = "[success]VALID[/success]"
    action_env = "None"
    
    if not os.path.exists(env_path):
        env_status = "[warning]MISSING[/warning]"
        key = Prompt.ask("🔑 [bold]OpenRouter API Key non trovata[/bold]. Inseriscila ora per configurare il sistema", password=True)
        if key:
            with open(env_path, "w") as f:
                f.write(f"OPENROUTER_API_KEY='{key}'\n")
                f.write("REDIS_HOST='localhost'\n")
            env_status = "[success]FIXED[/success]"
            action_env = "Creato file .env con la tua chiave."
        else:
            action_env = "⚠️ Configurazione saltata. Il sistema non funzionerà senza chiave."
            issues_found.append("Missing API Key")
    table.add_row("Configuration", env_status, action_env)

    # 3. Check Memory DB
    db_path = os.path.join(ACR_PATH, "acr_memory.db")
    db_status = "[success]ACTIVE[/success]"
    action_db = "None"
    if not os.path.exists(db_path):
        db_status = "[info]PENDING[/info]"
        action_db = "Verrà creato al primo avvio del Kernel."
    table.add_row("Memory DB", db_status, action_db)

    console.print(table)

    # 4. Smart Agent Advice (if issues remain and LLM is available)
    if issues_found:
        console.print("\n[planner]🧠 Invocazione Agente Diagnostico per consigli avanzati...[/planner]")
        # Check if we have a key now
        if os.path.exists(env_path):
            try:
                llm = LLMClient()
                prompt = (
                    f"Il sistema ACR ha riscontrato i seguenti problemi: {issues_found}.\n"
                    "Documentazione: Il sistema usa Redis per il bus, SQLite per la memoria e OpenRouter per l'LLM.\n"
                    "Fornisci un consiglio breve e risolutivo in italiano per l'utente."
                )
                import asyncio
                advice = asyncio.run(llm.chat([{"role": "user", "content": prompt}]))
                console.print(Panel(advice, title="[planner]Consiglio dell'Agente[/planner]", border_style="planner"))
            except Exception as e:
                console.print(f"[dim]Impossibile contattare l'agente: {e}[/dim]")

if __name__ == "__main__":
    run_doctor()
