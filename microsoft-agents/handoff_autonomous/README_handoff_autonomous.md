# 🚀 handoff_autonomous.py — Multi-Agent Handoff Orchestration (Azure OpenAI)

This project demonstrates a **handoff-based autonomous multi-agent system** built using the Azure OpenAI Responses client and Pydantic structured outputs.

A **Master Agent** dynamically routes user requests to specialized AI agents (Intake, Estimator, Communication, ETA).
Each specialist returns **strict JSON** validated using Pydantic models.

---

#  Overview

This implementation shows a real **multi-agent orchestration pattern**:

```
User Request
     ↓
Master Agent (Router)
     ↓ decides which tool to call
Specialist Agent (Structured JSON Output)
     ↓ validated via Pydantic
Master combines result
     ↓
Final Structured JSON Response
```

## Specialist Agents

| Agent               | Responsibility                   |
| ------------------- | -------------------------------- |
| intake_agent        | Collect vehicle + job details    |
| estimator_agent     | Provide repair cost estimation   |
| communication_agent | Draft customer-friendly messages |
| eta_agent           | Calculate ETA & scheduling       |

---

#  Prerequisites

Make sure the following are installed on your system:

✅ Python 3.10+
✅ Azure OpenAI resource
✅ Model deployment created in Azure
✅ API Key or Azure authentication

---

#  Install Dependencies

Create a virtual environment (recommended):

```bash
python -m venv .venv
```

Activate:

**Windows**

```bash
.venv\Scripts\activate
```

**Mac/Linux**

```bash
source .venv/bin/activate
```

Install required packages:

```bash
pip install pydantic
pip install azure-identity
pip install agent-framework
```

---

#  Environment Variables (MANDATORY)

Create a `.env` file or set environment variables:

```bash
AZURE_OPENAI_ENDPOINT=https://YOUR-RESOURCE.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=YOUR_MODEL_DEPLOYMENT
AZURE_OPENAI_API_VERSION=2024-XX-XX
AZURE_OPENAI_API_KEY=YOUR_API_KEY
```

Windows (PowerShell example):

```powershell
$env:AZURE_OPENAI_ENDPOINT="https://..."
$env:AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4o"
$env:AZURE_OPENAI_API_VERSION="2024-xx-xx"
$env:AZURE_OPENAI_API_KEY="key"
```

---

#  How the Implementation Works

## 1️⃣ Responses Client

Creates connection to Azure OpenAI using:

```
AzureOpenAIResponsesClient(...)
```

---

## 2️⃣ Pydantic Models

Each agent output is validated:

* IntakeResponse
* EstimateResponse
* CommunicationResponse
* ETAResponse

This ensures:

✅ Valid JSON
✅ Strong typing
✅ Production-safe output

---

## 3️⃣ Specialist Agents

Each AI agent is configured with strict JSON instructions.

Example:

```
Return ONLY JSON:
{
  "agent":"estimator_agent",
  "estimated_cost":"...",
  "currency":"INR"
}
```

---

## 4️⃣ Tools (Handoff Mechanism)

Specialists are wrapped as async tools:

```
async def estimator_tool(...)
```

The Master Agent calls these tools automatically.

This is called **Agent Handoff**.

---

## 5️⃣ Master Agent (Autonomous Router)

The Master Agent:

* Reads user intent
* Chooses which specialist to call
* Returns combined JSON response

It never directly answers when tools are available.

---

# ▶️ Running the Project

Execute:

```bash
python handoff_autonomous.py
```

---

#  Example Execution

### Input

```
Customer wants estimate for bumper repair and also ETA
```

---

#  Example Response Output

```json
{
  "workflow": "auto_body_shop",
  "result": {
    "agent": "estimator_agent",
    "estimated_cost": "₹4500",
    "currency": "INR",
    "notes": "Includes labor and paint",
    "eta": "2 working days"
  }
}
```

Actual values depend on the AI model response.

---

#  File Structure

```
handoff_autonomous.py
README.md
.env
```

---

#  Execution Flow (Step-by-Step)

1. User sends input
2. `master_agent.run()` starts streaming
3. Master decides which tool to call
4. Tool invokes specialist agent
5. Specialist returns JSON
6. Pydantic validates output
7. Master merges and returns final structured response

---

#  Why This Pattern Matters

This example demonstrates a **real autonomous multi-agent orchestration**, not manual routing.

Key advantages:

✅ Scalable architecture
✅ Clean separation of agent roles
✅ Structured outputs with validation
✅ Production-ready design

---

#  Important Notes

* Agents MUST return valid JSON or validation will fail.
* Streaming responses are collected before parsing.
* API version must match your Azure deployment.
* Ensure your model supports tool usage.

---

#  Suggested Improvements

* Add unified WorkflowResponse Pydantic model
* Add logging middleware
* Convert runner into FastAPI endpoint
* Add retry logic for JSON validation failures

---

#  Author Notes

This implementation demonstrates **handoff_autonomous orchestration**, where a Master Agent dynamically routes tasks to specialized AI agents using tools and structured JSON contracts.

Perfect for:

* AI workflow automation
* Enterprise multi-agent systems
* Azure OpenAI orchestration patterns

---
