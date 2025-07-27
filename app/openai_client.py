import openai
from agents import Agent, Runner
from openai.types.responses import ResponseTextDeltaEvent
import os
import asyncio

openai.api_key = os.getenv("OPENAI_API_KEY")

# Agent Instructions
systemInstructions = "You are an expert psychologist. Help users unpack thoughts and emotions using grounded, introspective reasoning and evidence-based psychology. Support the user positively and be curious to help the user self-reflect. If user doesn't add details, ask for more context, one or two questions at a time. Reply as if you are talking to someone, no markdown."

# Set up our agent
agent = Agent(
    name="Psychologist",
    instructions=systemInstructions,
    model="gpt-4o"
)


def run_agent(user_input):
    return asyncio.run(_run_agent_async(user_input))

async def _run_agent_async(user_input):
    response = Runner.run_streamed(
        starting_agent=agent,
        input=f"""
        In less than 100 words, answer the request delimited by triple backticks only if it's about psychology. Otherwise, remind the user this is a psychology assistant:
        ``` {user_input} ``` 
        """
    )

    final_output = ""
    async for event in response.stream_events():
        if event.type == "raw_response_event" and \
        isinstance(event.data, ResponseTextDeltaEvent):
            final_output += event.data.delta
            # print(event.data.delta, end="", flush=True)

    return final_output

def get_openai_response(user_input):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": user_input}]
    )
    return response.choices[0].message.content.strip()
