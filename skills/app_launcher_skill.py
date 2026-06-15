import logging
from agent.skill_system import BaseSkill

logger = logging.getLogger("Jarvis.Skill.AppLauncher")

class AppLauncherSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="AppLauncherSkill",
            description="Launches local applications dynamically on the user's system."
        )
        self.intents = {
            "OPEN_APPLICATION": {
                "description": "Searches and launches a local application by name (e.g. Blender, Discord, Chrome, VS Code).",
                "entities": {
                    "Target": "The name of the application to open (e.g., Blender, Spotify, Notepad)"
                },
                "examples": [
                    "Open Blender",
                    "Launch Discord",
                    "Can you open VS Code?",
                    "Run calculator",
                    "Open Notepad++",
                    "Open paint"
                ]
            }
        }
        
    def execute(self, intent: str, entities: dict, memory, automation_manager) -> str:
        if intent == "OPEN_APPLICATION":
            target = entities.get("Target")
            if not target:
                raise ValueError("An application target name is required for opening an application.")
                
            # Perform dynamic application discovery using ActionExecutor helper
            from agent.action_executor import ActionExecutor
            success = ActionExecutor.discover_and_launch_app(target)
            
            if success:
                # Update memory
                memory.set_active_app(target)
                return automation_manager.rm.get_contextual_response("launch_app", app_name=target.capitalize())
            else:
                # Fallback to standard pre-configured launcher or web player if appropriate
                logger.warning(f"Dynamic discovery failed for application: '{target}'")
                
                # Check for standard preconfigured ones inside automation manager as backup
                preconfigured_result = automation_manager.launch_app(target)
                if "I have no configuration" not in preconfigured_result:
                    memory.set_active_app(target)
                    return preconfigured_result
                    
                # If still not found, search Google or let user know
                return f"I searched your system but could not discover any installed application named '{target}', sir. Should I search online or open Google for you?"
                
        raise ValueError(f"Unsupported intent '{intent}' in AppLauncherSkill.")
