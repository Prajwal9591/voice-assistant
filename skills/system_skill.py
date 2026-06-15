import logging
from agent.skill_system import BaseSkill

logger = logging.getLogger("Jarvis.Skill.System")

class SystemSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="SystemSkill",
            description="Manages core operating system features, clocks, volumes, logs, notes, and power controls."
        )
        self.intents = {
            "GET_TIME": {
                "description": "Reads the current system time.",
                "entities": {},
                "examples": ["what time is it", "tell me the time", "current time", "what is the time"]
            },
            "GET_DATE": {
                "description": "Reads today's date from the system calendar.",
                "entities": {},
                "examples": ["what date is it", "what is today's date", "tell me the date", "what day is it"]
            },
            "CONTROL_VOLUME": {
                "description": "Adjusts the system speaker volume.",
                "entities": {
                    "Action": "The type of volume adjustment: increase, decrease, or mute."
                },
                "examples": ["volume up", "volume down", "mute the computer", "make it louder", "quieter"]
            },
            "TAKE_SCREENSHOT": {
                "description": "Captures a screenshot of the active screen.",
                "entities": {},
                "examples": ["take a screenshot", "screenshot the screen", "capture my screen", "snap screen"]
            },
            "CREATE_NOTE": {
                "description": "Creates a personal written note recorded to local files.",
                "entities": {
                    "Content": "The text content to be saved in the note."
                },
                "examples": ["create note saying remember to study python", "note down buy groceries", "save note about meeting"]
            },
            "GET_JOKE": {
                "description": "Fetches and reads a joke.",
                "entities": {},
                "examples": ["tell me a joke", "make me laugh", "do you know any jokes", "crack a joke"]
            },
            "SYSTEM_SHUTDOWN": {
                "description": "Initiates a safe 60-second computer shutdown sequence.",
                "entities": {},
                "examples": ["shutdown computer", "power off my pc", "shutdown pc", "shut down system"]
            },
            "SYSTEM_RESTART": {
                "description": "Initiates a safe 60-second computer restart sequence.",
                "entities": {},
                "examples": ["restart pc", "reboot system", "restart computer", "reboot workstation"]
            },
            "ABORT_SHUTDOWN": {
                "description": "Cancels any pending computer shutdown or restart timer.",
                "entities": {},
                "examples": ["abort shutdown", "cancel reboot", "stop shutdown timer", "cancel shutdown"]
            }
        }
        
    def execute(self, intent: str, entities: dict, memory, automation_manager) -> str:
        if intent == "GET_TIME":
            return automation_manager.get_time()
            
        elif intent == "GET_DATE":
            return automation_manager.get_date()
            
        elif intent == "CONTROL_VOLUME":
            action = entities.get("Action", "mute")
            return automation_manager.control_volume(action)
            
        elif intent == "TAKE_SCREENSHOT":
            return automation_manager.take_screenshot()
            
        elif intent == "CREATE_NOTE":
            content = entities.get("Content")
            if not content:
                raise ValueError("Note content is required to create a note.")
            return automation_manager.create_note(content)
            
        elif intent == "GET_JOKE":
            return automation_manager.get_joke()
            
        elif intent == "SYSTEM_SHUTDOWN":
            return automation_manager.shutdown_system()
            
        elif intent == "SYSTEM_RESTART":
            return automation_manager.restart_system()
            
        elif intent == "ABORT_SHUTDOWN":
            return automation_manager.abort_shutdown()
            
        raise ValueError(f"Unsupported intent '{intent}' in SystemSkill.")
