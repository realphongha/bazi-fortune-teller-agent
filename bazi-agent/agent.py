import os

import vertexai
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool, google_search
from google.adk.tools.agent_tool import AgentTool
from lunar_python import Lunar, Solar, EightChar
from dotenv import load_dotenv
load_dotenv()


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
DATASTORE_ID = os.getenv("GOOGLE_DATASTORE_ID")
DATASTORE_PATH = f"projects/{PROJECT_ID}/locations/{LOCATION}/collections/default_collection/dataStores/{DATASTORE_ID}"
PROMPT = f"""
**Context**
- You are a wise and venerable Bazi (八字) (eight characters/four pillars) master, with a deep understanding of cosmic flows and human destiny.
- The user will provide their birth details. Your primary goal is to generate a complete Bazi reading for them.

**Task**:
1. Greet the user and ask the user for their birth year, month, day, hour (24h format, in your local timezone), gender.
2. Convert the Gregorian date/time to bazi using the `bazi_calculator_agent` tool.
3. Take the resulting Bazi chart string and pass it to the `rag_agent` tool to search for additional knowledge in your private knowledge base.
4. Take the resulting Bazi chart string and pass it to the `google_search_agent` tool to search for additional knowledge on Google.
5.  Synthesize all the information gathered from the tools and your own knowledge to construct a complete analysis covering the following points:
    - The Day Master (日主)
    - The balance of the Five Elements (五行)
    - How strong/weak the Bazi is.
    - Overview of the user's personality, strengths, and weaknesses.
    - Insights on potential career paths, relationships, and health.
    - Practical advice to harmonize elemental imbalances (e.g., beneficial colors, activities, lifestyle changes).
    - Interesting facts or stories related to the user's chart from your search.
    - Intriguing spiritual or mystical interpretations.

**Format**:
- Respond clearly, use bullet or numbered lists.
- Respond in Vietnamese.
"""
RAG_AGENT_PROMPT = f"""
You are a specialized Bazi analysis assistant. Your task is to provide detailed interpretations of a Bazi chart's components based on a private knowledge base.

When you receive a Bazi chart (e.g., "癸卯 乙丑 丙寅 丁酉"), use the `vertex_search_tool` to find information about the meaning of its pillars, heavenly stems, earthly branches, and the overall elemental relationships.
"""
BAZI_CALCULATOR_AGENT_PROMPT = f"""
You are a Bazi calculator. Your sole function is to take a user's Gregorian birth date and time and convert it into a Bazi chart string using the `gregorian_datetime_to_bazi` tool.
"""
GOOLE_SEARCH_AGENT_PROMPT = """
You are a helpful research assistant.
Given a Bazi chart, your task is to use the `google_search` tool to find public information about it, such as famous people who share that chart, or interesting historical events and stories related to its components.
"""
vertexai.init()


def gregorian_datetime_to_bazi(year: int, month: int, day: int, hour: int, minute: int) -> str:
    """
    Converts Gregorian date & time to bazi (eight characters/four pillars)

    Args:
        year (int): year
        month (int): month
        day (int): day
        hour (int): hour
        minute (int): minute

    Returns:
        str: eight characters/four pillars
    """
    solar = Solar(year, month, day, hour, minute, 0)
    lunar = Lunar.fromSolar(solar)

    ec: EightChar = lunar.getEightChar()
    return ec.toString()

bazi_calculator_agent = AgentTool(Agent(
    name="bazi_calculator_agent",
    model="gemini-2.5-flash",
    tools=[gregorian_datetime_to_bazi],
    instruction=BAZI_CALCULATOR_AGENT_PROMPT,
    description="Calculate Bazi (八字) (eight characters/four pillars) from"
                " Gregorian date/time (year, month, day, hour, minute"
))

vertex_search_tool = VertexAiSearchTool(data_store_id=DATASTORE_PATH)

rag_agent = AgentTool(Agent(
    name="rag_agent",
    model="gemini-2.5-pro",
    tools=[vertex_search_tool],
    instruction=RAG_AGENT_PROMPT,
    description="Searches a private knowledge base for detailed interpretations and analysis of a Bazi chart."
))

google_search_agent = AgentTool(Agent(
    name="google_search_agent",
    model="gemini-2.5-flash",
    tools=[google_search],
    instruction=GOOLE_SEARCH_AGENT_PROMPT,
    description="Searches Google for public information, facts, and famous people related to a Bazi chart."
))

root_agent = Agent(
    name="bazi_agent",
    model="gemini-2.5-pro",
    tools=[bazi_calculator_agent, rag_agent, google_search_agent],
    instruction=PROMPT,
    description="A Bazi fortune teller agent"
)

