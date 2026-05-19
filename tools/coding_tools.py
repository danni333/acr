import subprocess
import os
from typing import Dict, Any

class CodeExecutor:
    """A suite of tools for code execution and file manipulation."""
    
    def __init__(self, workspace_root: str = "/home/tob/acr/workspace"):
        self.workspace_root = workspace_root
        os.makedirs(self.workspace_root, exist_ok=True)

    def execute_shell(self, command: str) -> Dict[str, Any]:
        """Executes a shell command within the workspace."""
        try:
            # Simple safety check: prevent leaving workspace if possible
            # Note: In production, this should run in a container/sandbox
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
                timeout=30
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except Exception as e:
            return {"error": str(e)}

    def write_file(self, filename: str, content: str) -> Dict[str, Any]:
        """Writes content to a file in the workspace."""
        try:
            filepath = os.path.join(self.workspace_root, filename)
            with open(filepath, "w") as f:
                f.write(content)
            return {"status": "success", "path": filepath}
        except Exception as e:
            return {"error": str(e)}

    def read_file(self, filename: str) -> Dict[str, Any]:
        """Reads content from a file in the workspace."""
        try:
            filepath = os.path.join(self.workspace_root, filename)
            with open(filepath, "r") as f:
                content = f.read()
            return {"content": content}
        except Exception as e:
            return {"error": str(e)}
