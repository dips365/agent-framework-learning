import asyncio
import os
import json
from typing import Optional

from pydantic import BaseModel
from agent_framework.azure import AzureOpenAIResponsesClient

# ------------------------------------------------
# Create Responses Client
# ------------------------------------------------

client = AzureOpenAIResponsesClient(
    endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

# ------------------------------------------------
# Pydantic Models (STRUCTURED OUTPUT)
# ------------------------------------------------

class IntakeResponse(BaseModel):
    agent: str
    vehicle_info: str
    job_details: str


class EstimateResponse(BaseModel):
    agent: str
    estimated_cost: str
    currency: str
    notes: Optional[str] = None


class CommunicationResponse(BaseModel):
    agent: str
    message: str
    tone: str


class ETAResponse(BaseModel):
    agent: str
    eta: str
    schedule_notes: Optional[str] = None


# ------------------------------------------------
# Define Specialist Agents (JSON ENFORCED)
# ------------------------------------------------

intake_agent = client.as_agent(
    name="intake_agent",
    instructions="""
Handle customer intake.

Return ONLY JSON:

{
  "agent":"intake_agent",
  "vehicle_info":"...",
  "job_details":"..."
}
""",
)

estimator_agent = client.as_agent(
    name="estimator_agent",
    instructions="""
Provide cost estimation.

Return ONLY JSON:

{
  "agent":"estimator_agent",
  "estimated_cost":"...",
  "currency":"INR",
  "notes":"..."
}
""",
)

communication_agent = client.as_agent(
    name="communication_agent",
    instructions="""
Generate customer-friendly communication.

Return ONLY JSON:

{
  "agent":"communication_agent",
  "message":"...",
  "tone":"professional"
}
""",
)

eta_agent = client.as_agent(
    name="eta_agent",
    instructions="""
Calculate ETA.

Return ONLY JSON:

{
  "agent":"eta_agent",
  "eta":"...",
  "schedule_notes":"..."
}
""",
)

# ------------------------------------------------
# Helper to collect streaming text
# ------------------------------------------------

async def collect_json(agent, user_input: str):
    full = ""
    async for event in agent.run(user_input, stream=True):
        if event.text:
            full += event.text
    return full


# ------------------------------------------------
# Wrap Specialists as TOOLS (Validated)
# ------------------------------------------------

async def intake_tool(input: str) -> str:
    raw = await collect_json(intake_agent, input)
    model = IntakeResponse.model_validate_json(raw)
    return model.model_dump_json()


async def estimator_tool(input: str) -> str:
    raw = await collect_json(estimator_agent, input)
    model = EstimateResponse.model_validate_json(raw)
    return model.model_dump_json()


async def communication_tool(input: str) -> str:
    raw = await collect_json(communication_agent, input)
    model = CommunicationResponse.model_validate_json(raw)
    return model.model_dump_json()


async def eta_tool(input: str) -> str:
    raw = await collect_json(eta_agent, input)
    model = ETAResponse.model_validate_json(raw)
    return model.model_dump_json()


# ------------------------------------------------
# MASTER AGENT (ROUTER + JSON OUTPUT)
# ------------------------------------------------

master_agent = client.as_agent(
    name="master_agent",
    instructions="""
You are a master orchestration agent.

Decide which specialist tool to call.

TOOLS:
- intake_tool
- estimator_tool
- communication_tool
- eta_tool

Return FINAL RESULT ONLY in JSON:

{
  "workflow":"auto_body_shop",
  "result":"<combined structured result>"
}
""",
    tools=[
        intake_tool,
        estimator_tool,
        communication_tool,
        eta_tool,
    ],
)

# ------------------------------------------------
# Simple Runner
# ------------------------------------------------

async def run_poc(user_input: str):

    print("\nUSER:", user_input)
    print("\nMASTER STRUCTURED RESPONSE:\n")

    full = ""

    async for event in master_agent.run(user_input, stream=True):
        if event.text:
            full += event.text

    try:
        parsed = json.loads(full)
        print(json.dumps(parsed, indent=2))
    except Exception:
        print("Invalid JSON returned:\n", full)


# ------------------------------------------------
# TEST END TO END
# ------------------------------------------------

if __name__ == "__main__":
    asyncio.run(
        run_poc(
            "Customer wants estimate for bumper repair and also ETA"
        )
    )