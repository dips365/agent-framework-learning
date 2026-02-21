# FastAPI endpoint to call agent and return response

import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from agent_framework.azure import AzureOpenAIResponsesClient
import asyncio

app = FastAPI()

class AgentRequest(BaseModel):
    prompt: str

# Async agent call function
async def call_agent(prompt: str):
    agent = AzureOpenAIResponsesClient(
        endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
        deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
        api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
        api_key=os.getenv('AZURE_OPENAI_API_KEY')
    ).as_agent(
        name="APIResponder",
        instructions="You are a helpful assistant. Answer the user's prompt clearly.",
    )
    return await agent.run(prompt)

@app.post("/agent")
async def agent_endpoint(request: AgentRequest):
    response = await call_agent(request.prompt)
    return {"response": str(response)}

# For local testing with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agent_api.agent_server:app", host="0.0.0.0", port=8000, reload=True)
