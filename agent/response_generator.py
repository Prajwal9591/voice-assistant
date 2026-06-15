import logging
import random

logger = logging.getLogger("Jarvis.Agent.ResponseGenerator")

class ResponseGenerator:
    def __init__(self, ai_engine, response_manager):
        self.ai = ai_engine
        self.rm = response_manager
        
    def generate(self, results: list, plan: list, memory) -> str:
        """
        Formulates a voice assistant verbal feedback based on step execution results.
        If no results exist, handles conversational queries or fallback answers.
        """
        # 1. Check if the plan is conversational or exit
        if plan:
            action = plan[0].get("action")
            if action == "CONVERSATIONAL":
                query = memory.history[-1]["user"] if memory.history else ""
                # Use our highly advanced context-aware AI Engine to generate the conversational response
                return self.ai.generate_response(
                    query,
                    conversation_history=memory.history,
                    active_app=memory.active_application,
                    active_web=memory.active_website
                )
            elif action == "EXIT":
                return "TERMINATE"
                
        # 2. Check for empty execution results
        if not results:
            if memory.pending_followup:
                entity = memory.pending_followup.get("missing_entity")
                if entity == "Target":
                    return "Which application would you like me to open, sir?"
                elif entity == "Recipient":
                    return "Who would you like me to send this message to, sir?"
                elif entity == "Message":
                    return "What message would you like me to send, sir?"
                else:
                    return f"Could you please specify the {entity.lower()}, sir?"
            return "I am on standby, sir. How can I assist you?"
            
        # 3. Analyze step results and construct verbal feedback
        feedback_parts = []
        for res in results:
            step = res.get("step", {})
            success = res.get("success", False)
            
            if success:
                result_str = res.get("result", "")
                if result_str:
                    feedback_parts.append(result_str)
            else:
                err_msg = res.get("error", "An unexpected execution error occurred")
                feedback_parts.append(f"I encountered a problem executing that step, sir: {err_msg}")
                
        if feedback_parts:
            # Combine individual step reports
            return " ".join(feedback_parts)
            
        return "Command completed successfully, sir."
