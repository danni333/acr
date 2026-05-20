import redis
import json
import os
import asyncio
import sqlite3
from datetime import datetime
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, RichLog, Static
from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from acr.core.ui_system import ACR_LOGO, ACR_THEME

class ACRChatApp(App):
    """Refined TUI with Word Wrap, Copy-Paste support, and robust Heartbeat tracking."""
    
    # Disable mouse capture to allow native terminal selection/copy
    mouse_support = False

    CSS = """
    Screen { background: #121212; }
    #main_container { layout: horizontal; }
    #chat_pane { width: 70%; border: solid #BB86FC; background: #1a1a1a; margin: 1; padding: 1; }
    #sidebar_container { width: 30%; layout: vertical; }
    #pulse_pane { height: 30%; border: solid #03DAC6; background: #1a1a1a; margin: 1; padding: 1; }
    #thoughts_pane { height: 70%; border: solid #82AAFF; background: #1a1a1a; margin: 1; padding: 1; }
    Input { dock: bottom; margin: 1; border: double #BB86FC; }
    """

    BINDINGS = [Binding("ctrl+c", "quit", "Quit", show=True)]

    def on_mount(self) -> None:
        # Force mouse support off to allow native selection
        self.mouse_support = False
        
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.r = redis.Redis(host=self.redis_host, port=6379, db=0, decode_responses=True)
        self.pubsub = self.r.pubsub()
        
        asyncio.create_task(self.listen_for_events())
        self.set_interval(2.0, self.update_pulse)
        self.load_history()

    def load_history(self):
        db_path = "/home/tob/acr/acr_memory.db"
        chat_log = self.query_one("#chat_pane", RichLog)
        thought_log = self.query_one("#thoughts_pane", RichLog)
        
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT event_type, payload FROM episodic_memory ORDER BY rowid DESC LIMIT 50")
                rows = cursor.fetchall()
                for etype, payload in reversed(rows):
                    try:
                        data = json.loads(payload)
                        if etype == "agent.response":
                            content = data.get('content', '')
                            # More permissive filter for thoughts
                            if "[Riflessione Interna]" in content or "Riflessione Interna" in content:
                                thought_log.write(f"[bold #82AAFF]🧠 Hist:[/bold #82AAFF] {content.replace('[Riflessione Interna]', '').strip()}")
                            else:
                                chat_log.write(f"[bold green]ACR (Hist):[/bold green] {content}")
                        elif etype == "goal.update":
                            chat_log.write(f"[bold cyan]Tu (Hist):[/bold cyan] {data.get('goal')}")
                    except: pass
                conn.close()
            except Exception as e:
                chat_log.write(f"[red]Errore DB: {e}[/red]")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="main_container"):
            # wrap=True enables Word Wrap
            yield RichLog(id="chat_pane", highlight=True, markup=True, wrap=True)
            with Vertical(id="sidebar_container"):
                yield Static(id="pulse_pane")
                yield RichLog(id="thoughts_pane", markup=True, wrap=True)
        yield Input(placeholder="Inserisci il tuo obiettivo qui e premi INVIO...")
        yield Footer()

    def on_ready(self) -> None:
        self.query_one("#thoughts_pane").border_title = "INTERNAL THOUGHTS"
        self.query_one("#chat_pane").border_title = "COGNITIVE TRACE"

    def update_pulse(self):
        model_path = "/home/tob/acr/workspace/self_model.json"
        uptime_str = "Connecting..."
        health = "Scanning..."
        
        if os.path.exists(model_path):
            try:
                with open(model_path, "r") as f:
                    model = json.load(f)
                    start_ts = model.get("start_time")
                    if start_ts:
                        start_dt = datetime.fromisoformat(start_ts)
                        diff = datetime.now() - start_dt
                        uptime_str = f"{diff.seconds // 60}m {diff.seconds % 60}s"
                    health = model.get("system_stability", "Optimal")
            except: 
                uptime_str = "Read Error"

        table = Table(show_header=False, box=None, expand=True)
        table.add_row("⏱ System Uptime", f"[bold white]{uptime_str}[/bold white]")
        table.add_row("📡 Redis Bus", "[bold green]ONLINE[/bold green]")
        table.add_row("🧠 Stability", f"[bold cyan]{health}[/bold cyan]")
        
        self.query_one("#pulse_pane", Static).update(
            Panel(table, title="[bold cyan]SYSTEM PULSE[/bold cyan]", border_style="cyan")
        )

    async def listen_for_events(self):
        self.pubsub.psubscribe("**")
        chat_log = self.query_one("#chat_pane", RichLog)
        thought_log = self.query_one("#thoughts_pane", RichLog)
        
        while True:
            msg = self.pubsub.get_message(ignore_subscribe_messages=True, timeout=0.1)
            if msg:
                try:
                    data = json.loads(msg['data'])
                    event_type = msg['channel']
                    payload = data.get('payload', {})
                    if event_type == "agent.response":
                        content = payload.get('content', '')
                        if "[Riflessione Interna]" in content or "Riflessione Interna" in content:
                            thought_log.write(f"[bold #82AAFF]🧠 Thought:[/bold #82AAFF] {content.replace('[Riflessione Interna]', '').strip()}")
                        else:
                            chat_log.write(f"\n[bold green]ACR »[/bold green] {content}\n")
                except: pass
            await asyncio.sleep(0.01)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        goal = event.value.strip()
        if goal:
            if goal.lower() in ["exit", "quit"]: self.exit(); return
            self.r.publish("goal.update", json.dumps({
                "event_type": "goal.update", "source": "tui",
                "payload": {"goal": goal}, "timestamp": datetime.now().isoformat()
            }))
            self.query_one("#chat_pane").write(f"[bold cyan]Tu:[/bold cyan] {goal}")
            self.query_one(Input).value = ""

if __name__ == "__main__":
    ACRChatApp().run()
