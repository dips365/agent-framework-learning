# handoff_autonomous.py

## Overview

`handoff_autonomous.py` demonstrates an autonomous agent handoff workflow using Microsoft Agent Framework. This script coordinates multiple agents to solve tasks collaboratively, enabling seamless handoff between agents for complex scenarios.

## Features
- Autonomous agent orchestration
- Multi-agent collaboration and handoff
- Task delegation and response aggregation
- Example of agent workflow using Microsoft Agent Framework

## Usage

1. Ensure you have installed all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the script:
   ```bash
   python microsoft-agents/handoff_autonomous.py
   ```

## Sample Response

A typical output from running the script might look like:

```
Agent 1: Received task 'Analyze customer query'.
Agent 1: Delegating to Agent 2 for detailed analysis.
Agent 2: Analyzing query and generating response.
Agent 2: Response ready, handing back to Agent 1.
Agent 1: Aggregating results and finalizing output.
Final Output: Customer query analyzed and response generated successfully.
```

## Customization
- Modify agent logic in `handoff_autonomous.py` to suit your workflow.
- Add more agents or change handoff criteria as needed.

## Requirements
- Python 3.8+
- Microsoft Agent Framework (see `requirements.txt`)

## License
See [LICENSE](../LICENSE) for details.
