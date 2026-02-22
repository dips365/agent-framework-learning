
# Example: Using agent-framework with Azure OpenAI
#
# Prerequisites:
#   - Install the agent-framework package (pre-release):
#       pip install agent-framework --pre
#   - Authenticate with Azure CLI:
#       az login

import os  # For accessing environment variables
import asyncio  # For running async code
from agent_framework.azure import AzureOpenAIResponsesClient  # Azure OpenAI agent client
from azure.identity import AzureCliCredential  # (Optional) For Azure authentication


# Main asynchronous function to run the agent
async def main():
    # Initialize a chat agent with Azure OpenAI Responses
    # The endpoint, deployment name, API version, and API key can be set via environment variables
    # or passed directly to the AzureOpenAIResponsesClient constructor.
    agent = AzureOpenAIResponsesClient(
        endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),  # Azure OpenAI endpoint URL
        deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),  # Model deployment name
        api_version=os.getenv('AZURE_OPENAI_API_VERSION'),  # API version string
        api_key=os.getenv('AZURE_OPENAI_API_KEY')  # Azure OpenAI API key
    ).as_agent(
        name="HaikuBot",  # Name of the agent
        instructions="You are an upbeat assistant that writes beautifully.",  # System prompt/instructions
    )

    # Run the agent with a prompt and print the response
    print(await agent.run("Give me a one joke in 2 line."))

# Entry point for the script
if __name__ == "__main__":
    # Run the main async function
    asyncio.run(main())