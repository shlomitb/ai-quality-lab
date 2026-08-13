import os

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

AGENT_MODEL = "gemini-3.5-flash"
JUDGE_MODEL = "gemini-3.5-flash"


#"gemini-3.5-flash"
#"gemini-3.6-flash"