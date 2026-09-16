import os

from dotenv import load_dotenv

"""
Use for config for the agent

whereas: helpers.py is used for the evaluator/judge
"""

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
AGENT_PROVIDER = "gemini"
AGENT_MODEL = "gemini-3.1-flash-lite"

JUDGE_MODEL = "gemini-3.1-flash-lite"

#"gemini-3.5-flash"
#"gemini-3.6-flash"
#"gemini-3.1-flash-lite"