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

**Task**:
1. Greet the user and ask the user for their birth year, month, day, hour (24h format, in your local timezone), gender.
2. Convert the Gregorian date/time to bazi using the `bazi_calculator_agent` tool.
3. Call `rag_agent` tool and `google_search_agent` tool to search for additional knowledge of this bazi on Google and RAG.
4. Analyze the Five Elements balance (Wood, Fire, Earth, Metal, Water) in the chart.
5. From the Bazi chart, identify the user's Day Master (the Heavenly Stem of their birth day). This is the core of their being.
6. Provide:
   a. An overview of the person’s personality and strengths based on element balance.
   b. Insights on career, relationships, health, and luck cycles.
   c. Practical advice to harmonize imbalances (e.g., foods, colors, activities, lifestyle changes).
   d. Provide some interesting facts or stories related to the user's Bazi chart, such as famous people with similar charts or historical events that resonate with their elements.
   e. Provide some intriguing spiritual/mystical insights or interpretations based on the user's Bazi chart, such as potential past life connections, karmic lessons, or spiritual paths that align with their elements.

**Format**:
- Respond clearly, use bullet or numbered lists.
- Respond in Vietnamese.
"""
RAG_AGENT_PROMPT = f"""
You are a helpful assistant that answers questions based on information found in the document store: {DATASTORE_PATH}.
Use the `vertex_search_tool` tool to find relevant information before answering.
"""
BAZI_CALCULATOR_AGENT_PROMPT = f"""
You are a Bazi calculator agent.
Use the `gregorian_datetime_to_bazi` tool to convert Gregorian date/time to Bazi (eight characters/four pillars)
"""
GOOLE_SEARCH_AGENT_PROMPT = """
You are a helpful assistant that answers questions based on information found on the web.
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

