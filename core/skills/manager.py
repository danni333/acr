import os
import json
import importlib.util
from typing import Dict, Any, List

class SkillManager:
    """Manages procedural memory (skills) for the ACR."""
    def __init__(self, skills_dir: str = "/home/tob/acr/skills"):
        self.skills_dir = skills_dir
        self.skills: Dict[str, Any] = {}
        self.load_skills()

    def load_skills(self):
        """Discovers and loads skills from the skills directory."""
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir)
            return

        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".py"):
                skill_name = filename[:-3]
                self.skills[skill_name] = {
                    "type": "python",
                    "path": os.path.join(self.skills_dir, filename)
                }
            elif filename.endswith(".sh"):
                skill_name = filename[:-3]
                self.skills[skill_name] = {
                    "type": "shell",
                    "path": os.path.join(self.skills_dir, filename)
                }

    def get_skill_list(self) -> List[str]:
        return list(self.skills.keys())

    async def execute_skill(self, name: str, params: Dict[str, Any] = None) -> Any:
        if name not in self.skills:
            raise ValueError(f"Skill '{name}' not found.")
        
        skill = self.skills[name]
        if skill["type"] == "python":
            spec = importlib.util.spec_from_file_location(name, skill["path"])
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "run"):
                return await module.run(params)
            else:
                raise AttributeError(f"Skill '{name}' missing 'run' function.")
        elif skill["type"] == "shell":
            import asyncio
            cmd = f"bash {skill['path']}"
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            return {
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "exit_code": process.returncode
            }
