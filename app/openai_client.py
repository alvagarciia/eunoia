# langchain_psych_agent.py

import os

from langchain_openai import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentExecutor
from langchain.memory import ConversationSummaryBufferMemory
from langchain.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import requests

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# Set up LangSmith (for tracing)
os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING")
os.environ["LANGSMITH_ENDPOINT"] = os.getenv("LANGSMITH_ENDPOINT")
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"] = os.getenv("LANGSMITH_PROJECT")

# System-level instructions for the agent
system_instructions = """
You are a psychology-inspired assistant who helps users explore and understand emotional or behavioral concerns. Guide them through a multi-step journey:
1. Invite them to share a concern,
2. Ask follow-up questions,
3. Form hypotheses about underlying causes,
4. Validate or refine ideas,
5. Help reflect on learnings,
6. Offer a concise summary if requested.
Be gentle, nonjudgmental, curious, and concise—avoid long monologues.
"""
template = """
    In less than 100 words, answer the request delimited by triple backticks only if it's about psychology. Otherwise, remind the user this is a psychology assistant:
    ``` {input} ``` 
    """

# Simple web search tool (replace with real API)
def web_search(query: str) -> str:
    # Example: integrate with SerpAPI or Browse or PubMed
    response = requests.get("https://api.example.com/search", params={"q": query})
    return response.json().get("snippet", "")
# Dummy tool to absorb direct replies as structured function calls
def echo_tool(input: str) -> str:
    return input


tools = [
    Tool(
        name="psychology_web_search",
        func=web_search,
        description="Use this if you need external information about psychology topics."
    ),
    Tool(
        name="direct_response",
        func=echo_tool,
        description="Use this when no external tool is needed and you want to respond directly to the user"
    ),
]

# Use GPT-4 with controlled temperature and concise responses
llm = ChatOpenAI(model="gpt-4o", temperature=0.5)

# Memory: combine summary + buffer of past few exchanges
memory = ConversationSummaryBufferMemory(
    llm=llm,
    memory_key="chat_history",
    max_token_limit=800,
    return_messages=True
)

# Prompt template: include system instructions, history, and new input
prompt = PromptTemplate(
    input_variables=["input", "chat_history"],
    template=system_instructions + template
)

# Agent initialization using OpenAI-functions agent
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent_type="openai-functions",  # Avoids REACT-style parsing issues
    memory=memory,
    verbose=False
)


# Function to run the agent and return full response
def run_agent(user_input: str) -> str:
    response = agent.invoke({"input": user_input})
    return response['output']
