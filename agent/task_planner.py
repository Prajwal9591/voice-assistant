import logging
import json
import re

logger = logging.getLogger("Jarvis.Agent.TaskPlanner")

class TaskPlanner:
    def __init__(self, ai_engine, skill_system):
        self.ai = ai_engine
        self.skills = skill_system
        
    def create_plan(self, intent: str, entities: dict, memory) -> list:
        """
        Creates a list of execution steps. Each step is a dictionary containing:
        - "skill": the name of the skill class to execute
        - "action": the target intent/action
        - "params": parameters for execution
        """
        plan = []
        if not intent:
            return plan
            
        if intent == "CONVERSATIONAL":
            plan.append({"action": "CONVERSATIONAL"})
            return plan
            
        if intent == "EXIT":
            plan.append({"action": "EXIT"})
            return plan

        # Get handled skill names
        skill_executors = {}
        for name, skill in self.skills.skills.items():
            if intent in skill.intents:
                skill_executors[name] = skill.description
                
        # 1. ONLINE INTELLIGENCE (GEMINI AI TASK PLANNER)
        if self.ai.use_gemini:
            try:
                prompt = f"""
You are the Task Planner layer of Jarvis, an advanced intelligent operting system agent.
Formulate a step-by-step execution plan to satisfy the user intent: "{intent}"
Extracted entity values: {json.dumps(entities)}

Available Skills:
{json.dumps(skill_executors, indent=2)}

Context Memory:
- Active Application: {memory.active_application}
- Active Website: {memory.active_website}

Your plan MUST be a JSON array of step objects. Each step object must have:
- "skill": name of the skill to execute (e.g., "WebSkill", "AppLauncherSkill", etc.)
- "action": the action/intent name
- "params": dictionary of parameter arguments

Example:
For a multi-step query like "Open YouTube and search Python tutorial":
[
  {{"skill": "WebSkill", "action": "OPEN_WEBSITE", "params": {{"Target": "YouTube"}}}},
  {{"skill": "WebSkill", "action": "SEARCH_YOUTUBE", "params": {{"Query": "Python tutorial"}}}}
]

Return ONLY the raw JSON array of steps:
"""
                response_text = self.ai.generate_response(prompt)
                match = re.search(r"\[.*\]", response_text, re.DOTALL)
                if match:
                    plan = json.loads(match.group(0))
                    logger.info(f"Gemini AI Task Planner generated plan: {plan}")
                    return plan
            except Exception as e:
                logger.error(f"Gemini task planning failed: {e}. Defaulting to offline planner.")

        # 2. OFFLINE COGNITIVE FALLBACK (DETERMINISTIC PLAN BUILDER)
        skill_name = None
        for name, skill in self.skills.skills.items():
            if intent in skill.intents:
                skill_name = name
                break
                
        if skill_name:
            # Check for specific composite queries offline
            # E.g. Intent: OPEN_APPLICATION, Target: YouTube, and we have a Query inside entities
            if intent in ["OPEN_APPLICATION", "OPEN_WEBSITE"] and entities.get("Target") == "YouTube" and "Query" in entities:
                plan.append({"skill": "WebSkill", "action": "OPEN_WEBSITE", "params": {"Target": "YouTube"}})
                plan.append({"skill": "WebSkill", "action": "SEARCH_YOUTUBE", "params": {"Query": entities.get("Query")}})
            elif intent == "SEARCH_YOUTUBE" and entities.get("Target") == "YouTube" and "Query" in entities:
                plan.append({"skill": "WebSkill", "action": "SEARCH_YOUTUBE", "params": {"Query": entities.get("Query")}})
            else:
                plan.append({
                    "skill": skill_name,
                    "action": intent,
                    "params": entities
                })
                
        logger.info(f"Offline Task Planner generated plan: {plan}")
        return plan
