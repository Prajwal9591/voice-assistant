import logging
from agent.skill_system import BaseSkill

logger = logging.getLogger("Jarvis.Skill.Communication")

class CommunicationSkill(BaseSkill):
    def __init__(self):
        super().__init__(
            name="CommunicationSkill",
            description="Manages messaging and communications with contacts."
        )
        self.intents = {
            "SEND_MESSAGE": {
                "description": "Sends a message containing text to a specific contact recipient.",
                "entities": {
                    "Recipient": "The name of the recipient/contact (e.g. Ravi, John, Dad)",
                    "Message": "The text message content to send"
                },
                "examples": [
                    "Send hello to Ravi",
                    "Send a message to John saying I will be late",
                    "Tell Dad that I am coming home",
                    "Message Sarah asking if we are still on"
                ]
            }
        }
        
    def execute(self, intent: str, entities: dict, memory, automation_manager) -> str:
        if intent == "SEND_MESSAGE":
            recipient = entities.get("Recipient")
            message = entities.get("Message")
            
            if not recipient:
                raise ValueError("A recipient name is required to send a message.")
            if not message:
                raise ValueError("A message text body is required.")
                
            logger.info(f"Sending message to '{recipient}': '{message}'")
            # In a real assistant, this might interface with WhatsApp Web, Twilio, or email.
            # Here, we will perform a simulated high-end response and update context
            feedback = f"I have sent the message to {recipient} saying: '{message}', sir."
            return feedback
            
        raise ValueError(f"Unsupported intent '{intent}' in CommunicationSkill.")
