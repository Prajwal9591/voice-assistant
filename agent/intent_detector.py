import logging
import json
import re

logger = logging.getLogger("Jarvis.Agent.IntentDetector")

class IntentDetector:
    def __init__(self, ai_engine, skill_system):
        self.ai = ai_engine
        self.skills = skill_system
        
    def detect(self, query: str, memory) -> str:
        """
        Determines what the user wants to do.
        Returns the intent name (e.g. 'OPEN_APPLICATION'), or None if unclear.
        """
        query_clean = query.lower().strip()
        
        # 0. Check for clarifying question pending state first
        if memory.pending_followup:
            intent = memory.pending_followup.get("intent")
            logger.info(f"Active pending clarifying question context found. Restoring intent: '{intent}'")
            return intent
            
        # Get all registered intents from loaded skills
        available_intents = {}
        for skill_name, skill in self.skills.skills.items():
            for intent_name, intent_info in skill.intents.items():
                available_intents[intent_name] = {
                    "description": intent_info.get("description", ""),
                    "examples": intent_info.get("examples", [])
                }
                
        # 1. ONLINE INTELLIGENCE (GEMINI AI INTENT REASONING)
        if self.ai.use_gemini and self.ai.client is not None:
            try:
                # We construct a rich classification prompt
                prompt = f"""
You are the Intent Classification layer of Jarvis, an advanced intelligent AI operating system assistant.
Classify the user's speech command: "{query}"

Available Intents and descriptions:
{json.dumps(available_intents, indent=2)}

Context memory coordinates:
- Last Intent: {memory.last_intent}
- Last Target: {memory.last_target}
- Active Application: {memory.active_application}
- Active Website: {memory.active_website}

Classification Guidelines:
- If the user query is a simple greeting or general talk (e.g. "hello", "how are you", "who are you", "thank you", "thanks"), return "CONVERSATIONAL".
- If the user wants to close, exit, or shut down the Jarvis assistant itself, return "EXIT".
- Otherwise, map to the most appropriate intent from the Available Intents list. If none are a clear match, return null.

You MUST respond with a single valid JSON block in this exact schema, with no other formatting:
{{
  "intent": "INTENT_NAME_OR_CONVERSATIONAL_OR_EXIT_OR_NULL"
}}
"""
                response = self.ai.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                response_text = response.text.strip()
                match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if match:
                    res_json = json.loads(match.group(0))
                    intent = res_json.get("intent")
                    if intent and intent != "null" and intent != "NULL":
                        logger.info(f"Gemini AI detected intent: '{intent}'")
                        return intent
            except Exception as e:
                logger.error(f"Gemini intent classification failed: {e}. Defaulting to Offline Cognitive Layer.")

        # 2. OFFLINE COGNITIVE FALLBACK (DYNAMIC DICTIONARY/REGEX ENGINE)
        # Check standard conversational terms with word boundaries
        conversational_greetings = ["hello", "greetings", "hi", "hey", "how are you", "who are you", "thank you", "thanks", "appreciate"]
        is_greeting = False
        for w in conversational_greetings:
            if re.search(r"\b" + re.escape(w) + r"\b", query_clean):
                # Ensure it's not a message command
                if not ("send" in query_clean and "to" in query_clean) and not ("tell" in query_clean):
                    is_greeting = True
                    break
        if is_greeting:
            return "CONVERSATIONAL"
        if query_clean in ["exit", "quit", "close", "goodbye", "terminate", "exit app", "close app", "power off jarvis"]:
            return "EXIT"
            
        # Match against skill examples
        best_intent = None
        max_score = 0
        
        for intent_name, intent_info in available_intents.items():
            examples = intent_info.get("examples", [])
            for ex in examples:
                ex_clean = ex.lower().strip()
                # Exact or substring match
                if ex_clean in query_clean or query_clean in ex_clean:
                    score = len(ex_clean)
                    if score > max_score:
                        max_score = score
                        best_intent = intent_name
                        
        # Keyword-based fallbacks for offline accuracy
        if not best_intent:
            fallback_keywords = {
                "OPEN_APPLICATION": ["open", "launch", "run", "start", "execute"],
                "OPEN_WEBSITE": ["open website", "website", "goto", "go to", ".com", ".org", ".net"],
                "SEARCH_GOOGLE": ["search google for", "search for", "google", "search"],
                "SEARCH_YOUTUBE": ["search youtube", "youtube search", "find on youtube"],
                "PLAY_YOUTUBE": ["play", "watch", "stream"],
                "SEND_MESSAGE": ["send message", "send hello", "tell ravi", "message", "send text"],
                "CREATE_NOTE": ["note", "write note", "make note", "save note", "note down"],
                "TAKE_SCREENSHOT": ["screenshot", "capture screen", "take a screenshot", "snap screen"],
                "CONTROL_VOLUME": ["volume", "louder", "quieter", "mute", "unmute", "increase volume", "decrease volume"],
                "GET_TIME": ["time", "clock"],
                "GET_DATE": ["date", "today", "calendar", "day is it"],
                "GET_JOKE": ["joke", "funny", "humor", "laugh"],
                "SYSTEM_SHUTDOWN": ["shutdown pc", "shutdown computer", "shutdown system", "power off pc"],
                "SYSTEM_RESTART": ["restart pc", "reboot system", "restart computer"],
                "ABORT_SHUTDOWN": ["abort shutdown", "cancel shutdown", "stop shutdown"]
            }
            
            for intent_name, keywords in fallback_keywords.items():
                if intent_name in available_intents:
                    for kw in keywords:
                        if re.search(r"\b" + re.escape(kw) + r"\b", query_clean):
                            best_intent = intent_name
                            break
                    if best_intent:
                        break
                        
        logger.info(f"Offline Cognitive Layer detected intent: '{best_intent}'")
        return best_intent
