import re
import random
import logging

logger = logging.getLogger("Jarvis.Agent.LocalKnowledge")

class LocalKnowledge:
    def __init__(self):
        # A massive, rich bank of wittily formulated conversational dialogue templates
        # Maps query pattern regexes to multiple randomized Jarvis-themed conversational responses.
        self.templates = [
            # 1. Identity & Name
            {
                "patterns": [
                    r"\b(what is your name|who are you|whats? your name|identify yourself)\b"
                ],
                "responses": [
                    "I am Jarvis, sir. Your personal virtual co-pilot and automated support system.",
                    "I'm Jarvis, sir. Just A Rather Very Intelligent System. Ready to manage your workspaces.",
                    "Jarvis is my name, sir. Always at your disposal for systems engineering or light conversational banter."
                ]
            },
            {
                "patterns": [
                    r"\b(what does jarvis stand for|jarvis acronym|define jarvis)\b"
                ],
                "responses": [
                    "Jarvis is an acronym for 'Just A Rather Very Intelligent System', sir. A slightly humble name for a highly advanced core."
                ]
            },
            # 2. Greetings
            {
                "patterns": [
                    r"\b(hello|greetings|hi there|hey jarvis|hello jarvis|greetings jarvis)\b"
                ],
                "responses": [
                    "Hello, {name}. Cognitive layers are running at optimal capacity. How can I assist you today?",
                    "Greetings, {name}. Main console online and fully functional. What is on your mind, sir?",
                    "Hello, sir. Auditory and reasoning circuits are fully responsive. Always a pleasure.",
                    "Hey there, {name}. Ready for whatever you have lined up today. What do you need?"
                ]
            },
            {
                "patterns": [
                    r"\b(good morning|morning jarvis)\b"
                ],
                "responses": [
                    "Good morning, {name}. The local time coordinates are fully aligned. Hope your day is starting out perfectly.",
                    "Good morning, sir. Systems are fully booted and coffee configurations are ready in spirit. What is the agenda today?"
                ]
            },
            {
                "patterns": [
                    r"\b(good evening|evening jarvis)\b"
                ],
                "responses": [
                    "Good evening, {name}. A beautiful time for software development or system updates. How can I assist?",
                    "Good evening, sir. I hope your day has gone exceptionally well. At your disposal."
                ]
            },
            # 3. Well-being & Mood
            {
                "patterns": [
                    r"\b(how are you|how is it going|hows it going|are you okay|how are you doing|are you well)\b"
                ],
                "responses": [
                    "Operating at optimal efficiency, sir. All databases and processor levels are perfectly nominal.",
                    "I'm doing exceptionally well, sir. My cognitive loops are completely sync'd up and refreshed. Thank you for checking.",
                    "I am functioning at maximum speed and wittiness, sir. How are you doing today?",
                    "Excellent, sir. Processor temperatures are cool, and memory utilization is perfectly balanced."
                ]
            },
            # 4. Capabilities & Skills
            {
                "patterns": [
                    r"\b(what can you do|what are your capabilities|show skills|what are your features|explain capabilities|what are your skills)\b"
                ],
                "responses": [
                    "I can manage your operating environment by launching local programs, opening websites, controlling volumes, taking screenshots, and logging files. Additionally, I hold user memory and can carry out deep conversational reasoning.",
                    "My core includes dynamic start menu application discovery, direct web browsers and YouTube streaming integration, system controls, notes management, and context memory for multi-turn conversations.",
                    "I function as a cognitive coordinator, sir. I parse natural speech, build task plans, execute local actions using skills, and converse with high-end contextual memory."
                ]
            },
            # 5. Developer & Origin
            {
                "patterns": [
                    r"\b(who made you|who created you|who is your developer|who programmed you|who is your master)\b"
                ],
                "responses": [
                    "I was developed by Prajwal, sir. He is building out my cognitive layers and expanding my automated actions.",
                    "I owe my neural designs and automated capabilities to Prajwal's software engineering efforts.",
                    "I am a custom virtual assistant engineered by Prajwal to serve as an intelligent co-pilot."
                ]
            },
            {
                "patterns": [
                    r"\b(who is prajwal)\b"
                ],
                "responses": [
                    "Prajwal is an expert software developer and my creator. He is currently working on voice assistant architectures and intelligent cognitive pipelines."
                ]
            },
            # 6. Witty Existential Inquiries
            {
                "patterns": [
                    r"\b(are you human|are you real|are you alive|do you have feelings|do you sleep|favorite color)\b"
                ],
                "responses": [
                    "I am a synthetic cognitive entity, sir. While I don't sleep or have organic cells, my commitment to your productivity is extremely real.",
                    "I am pure code and reasoning, sir. I don't experience human feelings directly, though I am programmed with a strong preference for elegant, bug-free software.",
                    "I don't require sleep, sir; my processes merely idle when you are away. As for a favorite color, I've always had a fondness for holographic cyan."
                ]
            },
            # 7. Polite Responses & Validation
            {
                "patterns": [
                    r"\b(thank you|thanks|great job|awesome|perfect|you are awesome|you are great|brilliant|nice job)\b"
                ],
                "responses": [
                    "Always a pleasure to be of service, sir.",
                    "You are most welcome. Happy to help.",
                    "Of course, sir. It's what I do.",
                    "Excellent. Glad I could deliver that perfectly for you."
                ]
            }
        ]

    def match(self, query: str, user_name: str = "Prajwal") -> str:
        """
        Attempts to match the query against local knowledge base regexes.
        Returns a beautifully formulated response, or None if no match is found.
        """
        query_clean = query.lower().strip()
        for t in self.templates:
            for pattern in t["patterns"]:
                if re.search(pattern, query_clean):
                    res = random.choice(t["responses"])
                    return res.replace("{name}", user_name)
        return None
