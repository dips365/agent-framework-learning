# FastAPI endpoint to call agent and return response

import os
from fastapi import FastAPI
from pydantic import BaseModel
from agent_framework.azure import AzureOpenAIResponsesClient

app = FastAPI()

class AgentPromptRequest(BaseModel):
    prompt: str

# Async agent call function
async def run_prompt_responder_agent(user_prompt: str):
    prompt_responder_agent = AzureOpenAIResponsesClient(
        endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
        deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME'),
        api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
        api_key=os.getenv('AZURE_OPENAI_API_KEY')
    ).as_agent(
        name="APIResponder",
        instructions="You are a helpful assistant. Answer the user's prompt clearly.",
    )
    return await prompt_responder_agent.run(user_prompt)

@app.post("/agent")
async def run_agent_endpoint(request_payload: AgentPromptRequest):
    agent_response = await run_prompt_responder_agent(request_payload.prompt)
    return {"response": str(agent_response)}

# For local testing with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("agent_api.agent_server:app", host="0.0.0.0", port=8000, reload=True)
