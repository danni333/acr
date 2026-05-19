import redis
import json
import os
import threading
import time
import sqlite3
from datetime import datetime
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from acr.core.ui_system import ACR_THEME, get_header

console = Console(theme=ACR_THEME)

class ACRDashboardChat:
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.r = redis.Redis(host=self.redis_host, port=6379, db=0, decode_responses=True)
        self.pubsub = self.r.pubsub()
        self.is_running = True
        self.messages = []
        self.start_time = time.time()
        self.load_history()

    def load_history(self):
        db_path = "/home/tob/acr/acr_memory.db"
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT timestamp, event_type, payload FROM episodic_memory ORDER BY timestamp DESC LIMIT 10")
                rows = cursor.fetchall()
                for row in reversed(rows):
                    ts, etype, payload = row
                    data = json.loads(payload)
                    if etype == "agent.response":
                        self.messages.append(f"[success]ACR[/success]: {data.get('content', '')[:100]}...")
                conn.close()
            except: pass
        if not self.messages:
            self.messages.append("[dim]In attesa di nuovi eventi...[/dim]")

    def get_sidebar(self):
        uptime = int(time.time() - self.start_time)
        table = Table(show_header=False, border_style="cyan", box=None)
        table.add_row("⏱ Uptime", f"[bold white]{uptime}s[/bold white]")
        table.add_row("📡 Bus", "[bold green]ONLINE[/bold green]")
        table.add_row("🧠 Memoria", f"[bold white]{len(self.messages)} eventi[/bold white]")
        return Panel(table, title="[bold cyan]SYSTEM PULSE[/bold cyan]", border_style="cyan")

    def get_main_chat(self):
        msg_text = Text()
        for m in self.messages[-12:]:
            msg_text.append(f"» {m}\n\n")
        return Panel(msg_text, title="[bold #BB86FC]COGNITIVE TRACE[/bold #BB86FC]", border_style="#BB86FC")

    def make_layout(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=10),
            Layout(name="body"),
            Layout(name="footer", size=3)
        )
        layout["body"].split_row(
            Layout(name="chat", ratio=3),
            Layout(name="sidebar", ratio=1)
        )
        return layout

    def listen(self):
        self.pubsub.psubscribe("**")
        for message in self.pubsub.listen():
            if message['type'] == 'pmessage':
                try:
                    data = json.loads(message['data'])
                    event_type = message['channel']
                    if event_type == "agent.response":
                        content = data['payload'].get('content', '')
                        self.messages.append(f"[bold green]ACR Response:[/bold green] {content}")
                    elif event_type == "plan.created":
                        self.messages.append(f"[dim]Planner ha creato un nuovo piano.[/dim]")
                except: pass

    def run(self):
        while True:
            layout = self.make_layout()
            layout["header"].update(get_header())
            
            # Show Dashboard for a few seconds or until an event
            with Live(layout, refresh_per_second=4, screen=True):
                threading.Thread(target=self.listen, daemon=True).start()
                # Wait for 3 seconds to let user see the status
                for _ in range(30): 
                    layout["body"]["chat"].update(self.get_main_chat())
                    layout["body"]["sidebar"].update(self.get_sidebar())
                    layout["footer"].update(Panel("[dim]Dashboard Attiva | Caricamento Input...[/dim]", border_style="dim"))
                    time.sleep(0.1)

            # Exit Live to ask for input
            goal = Prompt.ask("\n[bold #BB86FC]🎯 Prossimo Obiettivo[/bold #BB86FC] (o 'exit')")
            if goal.lower() in ['exit', 'quit']:
                break
            
            event = {
                "event_type": "goal.update",
                "source": "terminal_chat",
                "payload": {"goal": goal},
                "timestamp": datetime.now().isoformat()
            }
            self.r.publish("goal.update", json.dumps(event))
            self.messages.append(f"[bold cyan]Tu:[/bold cyan] {goal}")
            # Loop continues, re-entering Live mode

if __name__ == "__main__":
    ACRDashboardChat().run()
