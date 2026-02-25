# ReleasePulse — Portfolio (AI & Agentic)

This folder contains the **portfolio edition** of the ReleasePulse dashboard with **agentic AI**. It does not modify any original project files; you can merge into the main app later if you like the results.

## What's included

- **dashboard-agentic-ai.py** — Full dashboard (same as Dashboard v2) plus:
  - **AI Assistant** page: conversational assistant that uses an LLM with **tool-calling** (decide → act → answer) to query priority backlog, theme reviews, regressions, and persistence.
  - **Built with — AI & ML** section on the Home page for portfolio visibility.
- **agentic_assistant.py** — Agentic AI module: tool definitions, `_run_tool()`, and `run_agent()` loop.
- **requirements.txt** — Extra dependency: `openai` (for the assistant).

## How to run

From the **project root** (parent of `portfolio-agentic`):

```bash
# Install base deps if needed
pip install -r requirements.txt

# Install agentic extra
pip install -r portfolio-agentic/requirements.txt

# Run the portfolio dashboard
streamlit run portfolio-agentic/dashboard-agentic-ai.py
```

Data is loaded from the project’s `data/` folder (e.g. `data/priority_backlog.csv`).

## Enabling the AI Assistant

Set your OpenAI API key in the environment:

```bash
export OPENAI_API_KEY=sk-...
```

Without it, the AI Assistant page still works but will show a short message asking you to set the key and install `openai`.

## Merging into the main app

When you’re satisfied:

1. Copy `agentic_assistant.py` to the project root (or keep it in a subfolder and adjust imports).
2. Add the AI Assistant page and “Built with” section to `Dashboard_v2.py` (or merge `dashboard-agentic-ai.py` into your main dashboard).
3. Add `openai>=1.0.0` to the project root `requirements.txt`.
