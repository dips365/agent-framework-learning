# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os

from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

"""
Multi-Turn Conversations — Use AgentSession to maintain context

This sample shows how to keep conversation history across multiple calls
by reusing the same session object.

Environment variables:
  AZURE_AI_PROJECT_ENDPOINT        — Your Azure AI Foundry project endpoint
  AZURE_OPENAI_RESPONSES_DEPLOYMENT_NAME — Model deployment name (e.g. gpt-4o)
"""


async def main() -> None:
    # <create_agent>
    # credential = AzureCliCredential()
    client = AzureOpenAIResponsesClient(
        endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),  # Azure OpenAI endpoint URL
        deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),  # Model deployment name
        api_version=os.getenv('AZURE_OPENAI_API_VERSION'),  # API version string
        api_key=os.getenv('AZURE_OPENAI_API_KEY')  # Azure OpenAI API key
    )

    agent = client.as_agent(
        name="ConversationAgent",
        instructions="You are a friendly assistant. Keep your answers brief.",
    )
    # </create_agent>

    # <multi_turn>
    # Create a session to maintain conversation history
    session = agent.create_session()

    # First turn
    result = await agent.run("My name is Alice and I love hiking.", session=session)
    print(f"Agent: {result}\n")

    # Second turn — the agent should remember the user's name and hobby
    result = await agent.run("What do you remember about me?", session=session)
    print(f"Agent: {result}")
    # </multi_turn>


if __name__ == "__main__":
    asyncio.run(main())