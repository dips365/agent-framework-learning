# Sample: Multi-Agent Orchestration
# This script demonstrates a parent agent that delegates tasks to two child agents based on the query description.


import os
import asyncio
from agent_framework import Agent, Message
from agent_framework.azure import AzureOpenAIResponsesClient

# Define the first child agent (Weather Agent)
async def create_weather_agent():
    return Agent(
        client=AzureOpenAIResponsesClient(
            endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY')
        ),
        name="WeatherAgent",
        instructions="You answer only weather-related questions.",
    )

# Define the second child agent (News Agent)
async def create_news_agent():
    return Agent(
        client=AzureOpenAIResponsesClient(
            endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY')
        ),
        name="NewsAgent",
        instructions="You answer only news-related questions.",
    )

# Parent agent is now an actual AI agent that decides which child agent to call
async def parent_agent(query: str):
    async with Agent(
        client=AzureOpenAIResponsesClient(
            endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY')
        ),
        name="ParentAgent",
        instructions=(
            "You are a smart router agent. "
            "Given a user query, decide if it should be answered by the WeatherAgent (for weather questions), "
            "the NewsAgent (for news questions), or neither. "
            "Reply ONLY with one of these exact words: 'weather', 'news', or 'none'. "
            "Do not explain your answer."
        ),
    ) as router:
        decision = await router.run(query)
        decision = str(decision).strip().lower()

    if decision == "weather":
        async with await create_weather_agent() as agent:
            result = await agent.run(query)
            return f"[WeatherAgent]: {result}"
    elif decision == "news":
        async with await create_news_agent() as agent:
            result = await agent.run(query)
            return f"[NewsAgent]: {result}"
    else:
        return "[ParentAgent]: Sorry, I can only answer weather or news questions."

async def main():
    print("=== Multi-Agent Orchestration Sample (AI Parent Agent) ===\n")
    queries = [
        "What is the weather in Paris?",
        "Give me the latest news headlines.",
        "Tell me a joke."
    ]
    for q in queries:
        print(f"User: {q}")
        response = await parent_agent(q)
        print(f"Response: {response}\n")

if __name__ == "__main__":
    asyncio.run(main())
