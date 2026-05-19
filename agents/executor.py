from typing import Any, Optional
from acr.agents.base import BaseAgent
from acr.models.schemas import Event
from acr.tools.coding_tools import CodeExecutor

class ExecutorAgent(BaseAgent):
    def __init__(self, name: str, bus: Any, llm: Optional[Any] = None):
        super().__init__(name, bus, llm=llm)
        self.code_suite = CodeExecutor()

    async def setup_subscriptions(self):
        await self.bus.subscribe("plan.validated", self.handle_execution)

    async def handle_execution(self, event: Event):
        is_valid = event.payload.get("valid")
        if not is_valid:
            print(f"[Executor] Plan rejected by critic. Aborting.")
            await self.emit("agent.response", {"content": f"Mi dispiace, ma non posso procedere. Il Critic ha sollevato dei dubbi sul piano:\n{event.payload.get('feedback')}"})
            return

        plan = event.payload.get("plan", [])
        goal = event.payload.get("goal", "")
        print(f"[Executor] Executing validated plan from critic")
        
        results_summary = ""
        for step in plan:
            print(f"[Executor] Running step: {step}")
            if self.llm:
                prompt = (
                    f"Task: {step}\n"
                    "Generate a single, NON-INTERACTIVE bash command to execute this task.\n"
                    "CRITICAL RULES:\n"
                    "- NO interactive commands (bash, sh, nano, vim, ssh, top).\n"
                    "- NO markdown backticks.\n"
                    "- Use tools like: echo, ls, cat, grep, python3 -c.\n"
                    "- Respond ONLY with the command string."
                )
                command = await self.llm.chat([{"role": "user", "content": prompt}])
                command = command.split("\n")[0].strip("`").strip()
                
                # Double safety: check for interactive shell commands
                if command.strip() in ['bash', 'sh', 'python3', 'python']:
                    command = f"echo 'Skipped interactive command: {command}'"
                
                print(f"[Executor] LLM suggested command: {command}")
                result = self.code_suite.execute_shell(command)
                results_summary += f"Step: {step}\nResult: {result.get('stdout', '')}\n"
                await self.emit("execution.step_completed", {"step": step, "result": result})
            else:
                await asyncio.sleep(1)
        
        # Generate final human-readable response
        if self.llm:
            summary_prompt = (
                f"Original Goal: {goal}\n"
                f"Execution Summary:\n{results_summary}\n"
                "Based on the execution above, give a direct and conversational response to the user's goal. "
                "If it was a greeting, greet back. If it was a task, confirm completion and share results. "
                "Don't just summarize steps, talk to the user."
            )
            final_response = await self.llm.chat([{"role": "user", "content": summary_prompt}])
            await self.emit("agent.response", {"content": final_response})
        
        await self.emit("execution.completed", {"status": "success", "action": "task_executed"})
