import logging
import os
import sys

# Configure stdout logging to see the full reasoning pipeline traces
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

from ai_engine import AIEngine
from automation import AutomationManager
from agent import JarvisAgent

def run_agent_test():
    print("======================================================================")
    print("          STARTING COGNITIVE AGENT PIPELINE VERIFICATION SUITE       ")
    print("======================================================================")
    
    # Initialize engines
    ai = AIEngine()
    automation = AutomationManager()
    agent = JarvisAgent(ai, automation)
    
    # Test Queries representing each conversational & reasoning requirement
    test_queries = [
        # 1. Conversational Realism & Local Knowledge Base
        {
            "label": "Conversational Smalltalk - Greetings",
            "query": "Hello Jarvis"
        },
        {
            "label": "Conversational Identity - Who are you?",
            "query": "Who are you?"
        },
        {
            "label": "Conversational Mood - How are you?",
            "query": "How are you doing today?"
        },
        # 2. Dynamic Memory Learning
        {
            "label": "Declarative User Memory Learning",
            "query": "Remember that my favorite game is chess"
        },
        # 3. Dynamic Memory Retrieval (RAG)
        {
            "label": "Retrieval-Augmented Memory Check (RAG Retrieval)",
            "query": "What is my favorite game?"
        },
        # 4. Multi-step Task Planning & Context scopes
        {
            "label": "Multi-step Task Planning & Browser Controls",
            "query": "Open YouTube and search Python tutorial"
        },
        {
            "label": "Relative Context Memory state reference",
            "query": "Search Python tutorial"  # Active website YouTube scope is inherited
        },
        # 5. Clarifying dialog structures
        {
            "label": "Clarifying dialog missing parameter trigger",
            "query": "Open it"
        },
        {
            "label": "Dialog follow-up parameter resolution",
            "query": "Notepad++"
        }
    ]
    
    for idx, test in enumerate(test_queries, 1):
        print(f"\n--- TEST #{idx} - {test['label']} ---")
        print(f"USER SPEECH: \"{test['query']}\"")
        
        # Execute reasoning pipeline
        response = agent.process_query(test["query"])
        
        print(f"JARVIS RESPONSE: \"{response}\"")
        print(f"ACTIVE APP CONTEXT: '{agent.memory.active_application}'")
        print(f"ACTIVE WEB CONTEXT: '{agent.memory.active_website}'")
        print(f"PENDING FOLLOWUP: {agent.memory.pending_followup}")
        print("----------------------------------------------------------------------")
        
    print("\nVerification suite execution completed successfully!")

if __name__ == "__main__":
    run_agent_test()
