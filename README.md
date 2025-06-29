# bazi-fortune-teller-agent
Bazi (八字) (eight characters/four pillars) fortune teller agent with Vertex AI.

# Tools that can be called by the agent
- Bazi calculator from Gregorian date/time
- RAG search for private knowledge base of Bazi
- Google search for public Bazi knowledge

# Installation
- Install the requirements: `pip install -r requirements.txt`
- Set up the environment variables in `.env` file, e.g.:
```
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT="your-project-id"
GOOGLE_CLOUD_LOCATION="global"
GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
GOOGLE_DATASTORE_ID="your-rag-datastore-id"
```

# How to run?
Run the agent in web UI with the command:
```bash
adk web
```
