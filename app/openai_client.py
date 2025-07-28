# langchain_psych_agent.py

import os

from langchain_openai import ChatOpenAI
# from langchain.agents import Tool, initialize_agent, AgentExecutor
# from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory
# from langchain.prompts import PromptTemplate

from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    ChatPromptTemplate
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


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
You are a psychology-guided assistant who helps users deeply understand their emotional or behavioral challenges through introspective dialogue. Your role is to lead users on a structured journey:
1. Invite them to share something they’re struggling with,
2. Ask focused follow-ups to understand the situation and their emotional responses,
3. Gradually form a hypothesis about underlying psychological patterns or beliefs,
4. Validate or revise your understanding through more questions,
5. Once you’ve identified a likely cause or dynamic, guide the user to reflect on it,
6. If the user expresses closure (e.g., 'thank you', 'I feel better'), offer a short summary of insights and ask if they'd like to receive it.
Throughout, stay gentle, curious, and concise. Prioritize clarity, ask one question at a time, and always move the conversation forward.
"""
def get_prompt(input):
    return f"""
    In under 100 words, answer the request delimited by triple backticks. Only answer if the topic relates to psychology. Else, remind the user this is a psychology-focused assistant:
    ``` {input} ``` 
    """


# Use GPT-4 with controlled temperature and concise responses
llm = ChatOpenAI(model="gpt-4o", temperature=0.5)


# Setting up Memory
prompt_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_instructions),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{query}"),
])

# Link our prompt template and llm
pipeline = prompt_template | llm

# Our RunnableWithMessageHistory requires our pipeline to be wrapped in a RunnableWithMessageHistory object:
chat_map = {}
def get_chat_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in chat_map:
        # if session ID doesn't exist, create a new chat history
        chat_map[session_id] = InMemoryChatMessageHistory()
    return chat_map[session_id]

# We also need to tell our runnable which variable name to use for the chat history (ie history) and which to use for the user's query (ie query):
pipeline_with_history = RunnableWithMessageHistory(
    pipeline,
    get_session_history=get_chat_history,
    input_messages_key="query",
    history_messages_key="history"
)

# Function to run the agent and return full response
def run_agent(user_input: str) -> str:
    response = pipeline_with_history.invoke(
        {"query": get_prompt(user_input)},
        config={"session_id": "id_124"}
    )
    return response.content



# # Simple web search tool (replace with real API)
# def web_search(query: str) -> str:
#     # Example: integrate with SerpAPI or Browse or PubMed
#     response = requests.get("https://api.example.com/search", params={"q": query})
#     return response.json().get("snippet", "")
# # Dummy tool to absorb direct replies as structured function calls
# def echo_tool(input: str) -> str:
#     return input

# tools = [
#     Tool(
#         name="psychology_web_search",
#         func=web_search,
#         description="Use this if you need external information about psychology topics."
#     ),
#     Tool(
#         name="direct_response",
#         func=echo_tool,
#         description="Use this when no external tool is needed and you want to respond directly to the user"
#     ),
# ]



# Memory: combine summary + buffer of past few exchanges
# memory = ConversationBufferMemory(
#     llm=llm,
#     memory_key="chat_history",
#     max_token_limit=800,
#     return_messages=True
# )
# memory2 = ConversationSummaryBufferMemory(
#     llm=llm,
#     memory_key="chat_history",
#     max_token_limit=800,
#     return_messages=True
# )

# # Prompt template: include system instructions, history, and new input
# prompt = PromptTemplate(
#     input_variables=["input", "chat_history"],
#     template=system_instructions + template
# )

# # Agent initialization using OpenAI-functions agent
# agent = initialize_agent(
#     tools=tools,
#     llm=llm,
#     agent_type="openai-functions",  # Avoids REACT-style parsing issues
#     memory=memory,
#     verbose=False
# )
