import time
import logging

logger = logging.getLogger("Jarvis.Agent.ContextMemory")

class ContextMemory:
    """
    Context memory maintains conversation state, current active contexts
    (active app/website) and follow-up states to avoid redundant commands
    and implement context memory capabilities.
    """
    def __init__(self):
        self.history = []
        self.last_intent = None
        self.last_target = None
        self.active_application = None  # Stores lowercase name of last opened application
        self.active_website = None      # Stores lowercase name of last opened website
        self.pending_followup = None    # Stores dictionary details if waiting for user input
        self.variables = {}
        
    def add_turn(self, user_query: str, assistant_response: str):
        """Saves a conversation turn to local history."""
        self.history.append({
            "timestamp": time.time(),
            "user": user_query,
            "assistant": assistant_response
        })
        if len(self.history) > 10:
            self.history.pop(0)

    def set_active_app(self, app_name: str):
        """Sets the currently active application context."""
        self.active_application = app_name.lower().strip()
        self.last_target = app_name.strip()
        logger.info(f"Active application context switched to: '{self.active_application}'")

    def set_active_web(self, web_name: str):
        """Sets the currently active website context."""
        self.active_website = web_name.lower().strip()
        self.last_target = web_name.strip()
        logger.info(f"Active website context switched to: '{self.active_website}'")

    def clear(self):
        """Resets the context memory."""
        self.history.clear()
        self.last_intent = None
        self.last_target = None
        self.active_application = None
        self.active_website = None
        self.pending_followup = None
        self.variables.clear()
        logger.info("Context memory cleared successfully.")
