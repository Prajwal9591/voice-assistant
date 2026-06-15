import logging
import json
import re

logger = logging.getLogger("Jarvis.Agent.EntityExtractor")

class EntityExtractor:
    def __init__(self, ai_engine, skill_system):
        self.ai = ai_engine
        self.skills = skill_system
        
    def extract(self, query: str, intent: str, memory) -> dict:
        """
        Extracts relevant arguments / entities from the query based on the detected intent.
        Returns a dictionary of entity name -> value.
        """
        entities = {}
        if not intent or intent in ["CONVERSATIONAL", "EXIT"]:
            return entities
            
        # Retrieve expected entity schema for this intent
        intent_schema = None
        for skill_name, skill in self.skills.skills.items():
            if intent in skill.intents:
                intent_schema = skill.intents[intent].get("entities", {})
                break
                
        if not intent_schema:
            return entities
            
        # 1. ONLINE INTELLIGENCE (GEMINI AI ENTITY RESOLVER)
        if self.ai.use_gemini and self.ai.client is not None:
            try:
                prompt = f"""
You are the Entity Extraction layer of Jarvis, an advanced intelligent operating system assistant.
Extract entity parameters from user speech: "{query}"
Detected Intent: "{intent}"

Expected Entity Schema:
{json.dumps(intent_schema, indent=2)}

Context Memory:
- Last Target: "{memory.last_target}"
- Active Application Context: "{memory.active_application}"
- Active Website Context: "{memory.active_website}"

Guidelines:
1. Extract values exactly fitting the entity descriptions.
2. Context Resolution: If the user query is a context-dependent query (e.g. "search Python tutorial" when the active website context is "youtube"), resolve the "Target" entity to "YouTube" accordingly.
3. If an entity is not mentioned or cannot be inferred, do not include it.
4. Respond with ONLY a single valid JSON block, with no other text:
{{
  "EntityName": "ExtractedValue"
}}
"""
                response = self.ai.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                response_text = response.text.strip()
                match = re.search(r"\{.*\}", response_text, re.DOTALL)
                if match:
                    entities = json.loads(match.group(0))
                    entities = {k: v for k, v in entities.items() if v is not None}
                    logger.info(f"Gemini AI extracted entities: {entities}")
                    return entities
            except Exception as e:
                logger.error(f"Gemini entity extraction failed: {e}. Defaulting to offline extractor.")

        # 2. OFFLINE COGNITIVE FALLBACK (REGEX & STRING PARSING)
        query_clean = query.lower().strip()
        
        # OPEN_APPLICATION or OPEN_WEBSITE
        if intent in ["OPEN_APPLICATION", "OPEN_WEBSITE"]:
            target = query_clean
            # Clean polite words and helper phrases
            fillers = [
                "could you open website", "could you open app", "could you open",
                "could you launch", "could you run", "can you open website",
                "can you open app", "can you open", "can you launch", "can you run",
                "please open website", "please open app", "please open",
                "please launch", "please run", "i want to watch videos on",
                "i want to watch videos", "i want to open", "launch YouTube for me",
                "open website", "open app", "open", "launch", "run", "go to", "goto",
                "website", "for me", "please", "could you"
            ]
            for word in fillers:
                target = target.replace(word, "").strip()
            
            # Remove any trailing non-word characters
            target = re.sub(r"^[^\w]+|[^\w]+$", "", target).strip()
            
            # If the resolved target is exactly 'it' or similar, we treat it as missing to trigger clarification!
            if target and target not in ["it", "app", "program", "website", "something", "it for me", ""]:
                entities["Target"] = target.capitalize()
            else:
                logger.info("Target was resolved to 'it' or empty. Keeping Target entity empty to trigger clarifying question.")
                
        # SEND_MESSAGE
        elif intent == "SEND_MESSAGE":
            # Example: "Send hello to Ravi"
            recipient = None
            msg = None
            
            # Recipient extraction
            to_match = re.search(r"\bto\s+([a-zA-Z0-9_]+)\b", query_clean)
            tell_match = re.search(r"\btell\s+([a-zA-Z0-9_]+)\b", query_clean)
            if to_match:
                recipient = to_match.group(1).capitalize()
            elif tell_match:
                recipient = tell_match.group(1).capitalize()
                
            # Message extraction
            saying_match = re.search(r"\bsaying\s+(.+)$", query_clean)
            if saying_match:
                msg = saying_match.group(1)
            else:
                msg_match = re.search(r"\bsend\s+(.+?)\s+to\b", query_clean)
                if msg_match:
                    msg = msg_match.group(1)
                    
            if recipient:
                entities["Recipient"] = recipient
            if msg:
                entities["Message"] = msg
                
        # SEARCH_GOOGLE, SEARCH_YOUTUBE, PLAY_YOUTUBE
        elif intent in ["SEARCH_GOOGLE", "SEARCH_YOUTUBE", "PLAY_YOUTUBE"]:
            q = query_clean
            for phrase in ["search google for", "search for", "google search", "google", "search youtube for", "search youtube", "youtube search", "search on youtube", "play on youtube", "play"]:
                q = q.replace(phrase, "").strip()
            if q:
                entities["Query"] = q
                
        # CREATE_NOTE
        elif intent == "CREATE_NOTE":
            content = query_clean
            for phrase in ["create note saying", "create a note saying", "create note", "create a note", "write note", "make note", "note down", "save note"]:
                content = content.replace(phrase, "").strip()
            if content:
                entities["Content"] = content
                
        # CONTROL_VOLUME
        elif intent == "CONTROL_VOLUME":
            if any(w in query_clean for w in ["up", "increase", "louder"]):
                entities["Action"] = "increase"
            elif any(w in query_clean for w in ["down", "decrease", "quieter", "lower"]):
                entities["Action"] = "decrease"
            elif any(w in query_clean for w in ["mute", "unmute", "silence"]):
                entities["Action"] = "mute"

        # Apply context memory references offline if Target is missing
        # E.g. User says "Search Python tutorial" -> we resolve Target = YouTube if active application is YouTube
        if intent in ["SEARCH_GOOGLE", "SEARCH_YOUTUBE", "PLAY_YOUTUBE"] and "Target" not in entities:
            if memory.active_application == "youtube" or memory.active_website == "youtube" or intent == "SEARCH_YOUTUBE":
                entities["Target"] = "YouTube"
            else:
                entities["Target"] = "Google"

        logger.info(f"Offline Entity Extractor returned: {entities}")
        return entities
