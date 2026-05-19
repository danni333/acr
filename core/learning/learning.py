import os
import json
from datetime import datetime
from acr.core.llm import LLMClient

class LearningManager:
    """Orchestrates autonomous skill creation from successful experiences."""
    def __init__(self, bus, skill_manager, llm: LLMClient):
        self.bus = bus
        self.skill_manager = skill_manager
        self.llm = llm
        self.skills_dir = "/home/tob/acr/skills"

    async def analyze_success(self, goal: str, steps: list, results: list):
        """Analyzes a successful execution to see if it should become a skill."""
        print(f"[Learning] Analyzing success for goal: {goal}")
        
        prompt = (
            f"L'ACR ha completato con successo l'obiettivo: '{goal}'\n"
            f"Passi eseguiti: {json.dumps(steps)}\n"
            f"Risultati: {json.dumps(results)}\n\n"
            "Questo compito è generico e utile da salvare come 'Skill' permanente (file .py)?\n"
            "Se sì, rispondi SOLO con un file Python completo che implementi una funzione 'async def run(params=None)' "
            "che racchiuda questa logica. Altrimenti rispondi 'NO'."
        )
        
        response = await self.llm.chat([
            {"role": "system", "content": "Sei il modulo di apprendimento autonomo di ACR. Distilli esperienze in codice."},
            {"role": "user", "content": prompt}
        ])

        if response.strip().upper() != "NO":
            # Extract code (handle markdown if present)
            code = response.replace("```python", "").replace("```", "").strip()
            skill_name = goal.lower().replace(" ", "_")[:20] + "_autolearn"
            file_path = os.path.join(self.skills_dir, f"{skill_name}.py")
            
            with open(file_path, "w") as f:
                f.write(code)
            
            print(f"[Learning] Nuova Skill appresa autonomamente: {skill_name}")
            await self.bus.publish("skill.learned", {"name": skill_name, "goal": goal})
            self.skill_manager.load_skills()
