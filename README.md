
# agent-framework-learning
Microsoft Agent Framework Learning

## Overview
This repository demonstrates how to use Microsoft Agent Framework to build, run, and orchestrate AI agents with Azure OpenAI. It includes samples for single agents, tool integration, approval workflows, and multi-agent orchestration.

## Prerequisites
- Python 3.8+
- Install dependencies:
	```bash
	pip install agent-framework --pre
	```
- Set up Azure OpenAI resource and obtain endpoint, deployment name, API version, and API key.
- Authenticate with Azure CLI:
	```bash
	az login
	```
- Set environment variables:
	- AZURE_OPENAI_ENDPOINT
	- AZURE_OPENAI_DEPLOYMENT_NAME
	- AZURE_OPENAI_API_VERSION
	- AZURE_OPENAI_API_KEY

## Samples

### 1. hello-agent.py
Basic example of running a single agent with Azure OpenAI. The agent responds to a prompt (e.g., generates a joke or haiku).

**How to run:**
```
python microsoft-agents/hello-agent.py
```

### 2. add_tools.py
Demonstrates tool integration and approval workflows. Includes:
- `get_weather`: Returns weather info without approval.
- `get_weather_detail`: Returns detailed weather info, requires user approval.
- Functions to handle approvals (streaming and non-streaming).
- Example of running agent with and without human approval.

**How to run:**
```
python microsoft-agents/add_tools.py
```
Follow prompts to approve or deny tool calls.


### 3. multi_agent_sample.py
Shows multi-agent orchestration:
- Parent agent (AI-powered) receives user queries.
- Decides (using LLM) whether to route to WeatherAgent, NewsAgent, or reject.
- Child agents answer weather or news questions.

**How to run:**
```
python microsoft-agents/multi_agent_sample.py
```
The parent agent uses its own intelligence to select the right child agent.

### 4. memory.py
Demonstrates agent memory using context providers and session state for personalization.
- Implements a `UserMemoryProvider` that remembers the user's name across turns.
- The agent asks for the user's name if it doesn't know it.
- Once the user provides their name, the agent personalizes responses in future turns.
- Session state persists user info, which can be inspected after interactions.

**How to run:**
```
python microsoft-agents/memory.py
```
You will see the agent ask for your name, remember it, and personalize future responses.

### 5. multi_turn_conversation.py
**Purpose:**
(Placeholder: File not found in workspace.)

**Expected content:**
Would demonstrate how to manage multi-turn conversations with agents, maintaining context and history across multiple user-agent exchanges.

## End-to-End Process
1. Set up environment and Azure OpenAI credentials.
2. Run any sample script.
3. The agent(s) process your query, optionally use tools, and may ask for approval.
4. Multi-agent orchestration: Parent agent uses LLM to decide routing, then delegates to child agents.
5. Results are printed in the console.

## Context for Each Sample
- **hello-agent.py**: Simple agent, direct prompt-response.
- **add_tools.py**: Agent with tools, approval workflow, demonstrates human-in-the-loop.
- **multi_agent_sample.py**: AI parent agent orchestrates multiple child agents, true agentic workflow.
- **memory.py**: Agent remembers user info and personalizes responses using session state.
- **multi_turn_conversation.py**: (Not present) Would show multi-turn conversation management.

## License
MIT License. See LICENSE file.
