from rich.theme import Theme
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

# ACR Design System - "Obsidian & Electric"
ACR_THEME = Theme({
    "brand": "bold #BB86FC",      # Electric Violet
    "success": "bold #03DAC6",    # Teal
    "warning": "bold #CF6679",    # Coral
    "info": "#03DAC6",
    "planner": "bold #BB86FC",
    "critic": "bold #FF7597",
    "executor": "bold #82AAFF",
    "anomaly": "bold #FF5555",
    "dim": "#555555"
})

ACR_LOGO = r"""
    ___      ______   .______      
   /   \    /      |  |   _  \     
  /  ^  \  |  ,----'  |  |_)  |    
 /  /_\  \ |  |       |      /     
/  _____  \|  `----.  |  |\  \----.
/__/     \__\______|  | _| `._____|
                                   
 [bold #BB86FC]Autobiographical Cognitive Runtime[/bold #BB86FC]
 [dim]v1.0.0 | Production Grade Cognitive System[/dim]
"""

def get_header():
    return Panel(
        Text.from_markup(ACR_LOGO, justify="center"),
        border_style="#BB86FC",
        padding=(1, 2)
    )

def brand_print(console: Console, message: str, style: str = "brand"):
    console.print(f"[{style}]»[/{style}] {message}")
