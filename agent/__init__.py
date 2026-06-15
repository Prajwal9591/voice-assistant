import logging
from agent.context_memory import ContextMemory
from agent.skill_system import SkillSystem
from agent.intent_detector import IntentDetector
from agent.entity_extractor import EntityExtractor
from agent.task_planner import TaskPlanner
from agent.action_executor import ActionExecutor
from agent.response_generator import ResponseGenerator

logger = logging.getLogger("Jarvis.Agent")

class JarvisAgent:
    """
    Cognitive Reasoning Layer coordinating Intent Detection, Entity Extraction,
    Task Planning, Action Execution, and Response Generation.
    """
    def __init__(self, ai_engine, automation_manager):
        logger.info("Initializing Jarvis Intelligent Agent Architecture...")
        
        self.ai = ai_engine
        self.automation = automation_manager
        
        # Initialize sub-modules
        self.memory = ContextMemory()
        self.skills = SkillSystem()
        
        # Load capability plugins
        self.skills.load_skills()
        
        self.intent_detector = IntentDetector(self.ai, self.skills)
        self.entity_extractor = EntityExtractor(self.ai, self.skills)
        self.task_planner = TaskPlanner(self.ai, self.skills)
        self.action_executor = ActionExecutor(self.skills, self.automation)
        self.response_generator = ResponseGenerator(self.ai, self.automation.rm)
        
    def process_query(self, query: str) -> str:
        """
        Main reasoning layer processing verbal commands:
        User Speech -> Intent -> Entity -> Plan -> Execute -> Response
        """
        logger.info(f"--- Jarvis Reasoning Loop Start: '{query}' ---")
        
        # Clean query
        query_clean = query.strip()
        if not query_clean:
            return "Yes, sir?"
            
        # Detect and handle offline composite queries (e.g., "Open YouTube and search Python tutorial")
        if not self.ai.use_gemini and any(sep in query_clean for sep in [" and ", " then "]):
            sep = " and " if " and " in query_clean else " then "
            parts = query_clean.split(sep)
            if len(parts) == 2:
                verbs = ["open", "launch", "run", "start", "search", "google", "play", "send", "tell", "message", "create", "note", "take", "screenshot", "volume"]
                part1_has_verb = any(v in parts[0].lower() for v in verbs)
                part2_has_verb = any(v in parts[1].lower() for v in verbs)
                
                if part1_has_verb and part2_has_verb:
                    logger.info(f"Composite command detected offline. Part 1: '{parts[0]}', Part 2: '{parts[1]}'")
                    
                    # Process Sub-command 1
                    intent1 = self.intent_detector.detect(parts[0], self.memory)
                    entities1 = self.entity_extractor.extract(parts[0], intent1, self.memory)
                    plan1 = self.task_planner.create_plan(intent1, entities1, self.memory)
                    
                    # Temporarily update context memory so sub-command 2 inherits active apps/websites
                    if intent1 not in ["CONVERSATIONAL", "EXIT"]:
                        self.memory.last_intent = intent1
                        if "Target" in entities1:
                            target_name = entities1["Target"]
                            self.memory.last_target = target_name
                            if intent1 == "OPEN_WEBSITE":
                                self.memory.set_active_web(target_name)
                            elif intent1 == "OPEN_APPLICATION":
                                self.memory.set_active_app(target_name)
                                
                    # Process Sub-command 2
                    intent2 = self.intent_detector.detect(parts[1], self.memory)
                    entities2 = self.entity_extractor.extract(parts[1], intent2, self.memory)
                    plan2 = self.task_planner.create_plan(intent2, entities2, self.memory)
                    
                    # Combine plans
                    combined_plan = plan1 + plan2
                    logger.info(f"Combined Multi-step Task Plan: {combined_plan}")
                    
                    # Execute combined plan
                    results = self.action_executor.execute_plan(combined_plan, self.memory)
                    
                    # Generate response
                    response = self.response_generator.generate(results, combined_plan, self.memory)
                    
                    # Final memory updates
                    self.memory.add_turn(query_clean, response)
                    logger.info("--- Jarvis Reasoning Loop Complete (Composite) ---")
                    return response

        # 1. Intent Detection
        intent = self.intent_detector.detect(query_clean, self.memory)
        logger.info(f"Phase 1 - Intent Analysis: '{intent}'")
        
        # 2. Entity Extraction
        entities = self.entity_extractor.extract(query_clean, intent, self.memory)
        logger.info(f"Phase 2 - Entity Extraction: {entities}")
        
        # Check for clarifying follow-up question triggers
        if intent and intent not in ["CONVERSATIONAL", "EXIT"]:
            # Retrieve schema of expected entities for the detected intent
            expected_schema = {}
            for skill_name, skill in self.skills.skills.items():
                if intent in skill.intents:
                    expected_schema = skill.intents[intent].get("entities", {})
                    break
                    
            # Check if any required parameters are missing
            missing_required = None
            
            # For OPEN_APPLICATION / OPEN_WEBSITE, we absolutely require Target
            if intent in ["OPEN_APPLICATION", "OPEN_WEBSITE"] and "Target" not in entities:
                missing_required = "Target"
            # For SEND_MESSAGE, we require Recipient and Message
            elif intent == "SEND_MESSAGE":
                if "Recipient" not in entities:
                    missing_required = "Recipient"
                elif "Message" not in entities:
                    missing_required = "Message"
            # For CREATE_NOTE, we require Content
            elif intent == "CREATE_NOTE" and "Content" not in entities:
                missing_required = "Content"
                
            if missing_required:
                # If we were already in a followup state and resolved it, clear it.
                # Otherwise, set it!
                if self.memory.pending_followup:
                    # Try to merge the new response into entities
                    prev_missing = self.memory.pending_followup.get("missing_entity")
                    entities[prev_missing] = query_clean
                    self.memory.pending_followup = None
                    logger.info(f"Clarified missing parameter '{prev_missing}': '{query_clean}'")
                    # Re-check for any other missing entities
                    if intent == "SEND_MESSAGE" and "Message" not in entities:
                        missing_required = "Message"
                    else:
                        missing_required = None
                        
                if missing_required:
                    self.memory.pending_followup = {
                        "intent": intent,
                        "missing_entity": missing_required,
                        "partial_entities": entities
                    }
                    logger.warning(f"Clarifying follow-up triggered. Missing: '{missing_required}'")
                    # Generate clarifying response directly
                    response = self.response_generator.generate(results=[], plan=[], memory=self.memory)
                    self.memory.add_turn(query_clean, response)
                    return response
        else:
            # If query does not map to a structured intent, handle fallback or conversational chat
            if not intent:
                logger.info("Intent unclear. Routing to AI fallback response.")
                response = self.ai.generate_response(
                    query_clean,
                    conversation_history=self.memory.history,
                    active_app=self.memory.active_application,
                    active_web=self.memory.active_website
                )
                self.memory.add_turn(query_clean, response)
                return response
                
        # If we got here, any clarifying state is completed successfully!
        if self.memory.pending_followup:
            # Clean up
            self.memory.pending_followup = None
            
        # 3. Task Planning
        plan = self.task_planner.create_plan(intent, entities, self.memory)
        logger.info(f"Phase 3 - Task Planner: {plan}")
        
        # 4. Action Execution
        results = self.action_executor.execute_plan(plan, self.memory)
        logger.info(f"Phase 4 - Action Executor: {results}")
        
        # 5. Response Generation
        response = self.response_generator.generate(results, plan, self.memory)
        logger.info(f"Phase 5 - Response Generator: '{response}'")
        
        # 6. Context Memory Updates (Update last metrics, history)
        if intent not in ["CONVERSATIONAL", "EXIT"]:
            self.memory.last_intent = intent
            if "Target" in entities:
                self.memory.last_target = entities["Target"]
                
        self.memory.add_turn(query_clean, response)
        
        logger.info(f"--- Jarvis Reasoning Loop Complete ---")
        return response
