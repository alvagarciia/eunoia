import os

from langchain_openai import ChatOpenAI

from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    ChatPromptTemplate
)
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from pydantic import BaseModel, Field
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.runnables import ConfigurableFieldSpec


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
llm_sum = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.0)

# Setting up Memory
prompt_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_instructions),
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("{query}"),
])

# Link our prompt template and llm
pipeline = prompt_template | llm


# ConversationSummaryBufferMessage (for summary + window memory)
class ConversationSummaryBufferMessageHistory(BaseChatMessageHistory, BaseModel):
    messages: list[BaseMessage] = Field(default_factory=list)
    llm: ChatOpenAI = Field(default_factory=ChatOpenAI)
    k: int = Field(default_factory=int)

    def __init__(self, llm: ChatOpenAI, k: int):
        super().__init__(llm=llm, k=k)

    def add_messages(self, messages: list[BaseMessage]) -> None:
        """Add messages to the history, removing any messages beyond
        the last `k` messages and summarizing the messages that we
        drop.
        """
        existing_summary: SystemMessage | None = None
        old_messages: list[BaseMessage] | None = None
        # see if we already have a summary message
        if len(self.messages) > 0 and isinstance(self.messages[0], SystemMessage):
            print(">> Found existing summary")
            existing_summary = self.messages.pop(0)
        # add the new messages to the history
        self.messages.extend(messages)
        # check if we have too many messages
        if len(self.messages) > self.k:
            print(
                f">> Found {len(self.messages)} messages, dropping "
                f"oldest {len(self.messages) - self.k} messages.")
            # pull out the oldest messages...
            old_messages = self.messages[:self.k]
            # ...and keep only the most recent messages
            self.messages = self.messages[-self.k:]
        if old_messages is None:
            print(">> No old messages to update summary with")
            # if we have no old_messages, we have nothing to update in summary
            return
        # construct the summary chat messages
        summary_prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "Given the existing conversation summary and the new messages, "
                "generate a new summary of the conversation. Ensuring to maintain "
                "as much relevant information as possible."
            ),
            HumanMessagePromptTemplate.from_template(
                "Existing conversation summary:\n{existing_summary}\n\n"
                "New messages:\n{old_messages}"
            )
        ])
        # format the messages and invoke the LLM
        new_summary = self.llm.invoke(
            summary_prompt.format_messages(
                existing_summary=existing_summary,
                old_messages=old_messages
            )
        )
        print(f">> New summary: {new_summary.content}")
        # prepend the new summary to the history
        self.messages = [SystemMessage(content=new_summary.content)] + self.messages

    def clear(self) -> None:
        """Clear the history."""
        self.messages = []


# Our RunnableWithMessageHistory requires our pipeline to be wrapped in a RunnableWithMessageHistory object:
chat_map = {}
def get_chat_history(session_id: str, llm: ChatOpenAI, k: int) -> ConversationSummaryBufferMessageHistory:
    if session_id not in chat_map:
        # if session ID doesn't exist, create a new chat history
        chat_map[session_id] = ConversationSummaryBufferMessageHistory(llm=llm, k=k)
    # return the chat history
    return chat_map[session_id]


# We also need to tell our runnable which variable name to use for the chat history (ie history) and which to use for the user's query (ie query):
pipeline_with_history = RunnableWithMessageHistory(
    pipeline,
    get_session_history=get_chat_history,
    input_messages_key="query",
    history_messages_key="history",
    history_factory_config=[
        ConfigurableFieldSpec(
            id="session_id",
            annotation=str,
            name="Session ID",
            description="The session ID to use for the chat history",
            default="id_default",
        ),
        ConfigurableFieldSpec(
            id="llm",
            annotation=ChatOpenAI,
            name="LLM",
            description="The LLM to use for the conversation summary",
            default=llm,
        ),
        ConfigurableFieldSpec(
            id="k",
            annotation=int,
            name="k",
            description="The number of messages to keep in the history",
            default=4,
        )
    ]
)

# Function to run the agent and return full response
def run_agent(user_input: str) -> str:
    response = pipeline_with_history.invoke(
        {"query": get_prompt(user_input)},
        config={"session_id": "id_128", "llm": llm_sum, "k": 3}
    )
    return response.content