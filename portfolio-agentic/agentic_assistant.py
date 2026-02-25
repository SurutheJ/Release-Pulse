# ============================
# ReleasePulse — Agentic AI Assistant
# ============================
# Uses an LLM with tool-calling in a decide–act loop:
# observe (user question) → decide (which tools to call) → act (run tools) → repeat until answer.
# ============================

import os
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


TOOLS_OPENAI = [
    {
        "type": "function",
        "function": {
            "name": "get_priority_backlog",
            "description": "Get the prioritized backlog of themes ranked by RICE score. Use when the user asks what to fix first, priority order, or what to work on next.",
            "parameters": {
                "type": "object",
                "properties": {
                    "top_n": {"type": "integer", "description": "Return only the top N themes (default 10).", "default": 10}
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_theme_reviews",
            "description": "Get sample user reviews for a specific theme. Use when the user wants quotes, evidence, or what users said about a theme.",
            "parameters": {
                "type": "object",
                "properties": {
                    "theme": {"type": "string", "description": "Theme name, e.g. 'Playback Reliability', 'Navigation & Home Feed'."},
                    "version": {"type": "string", "description": "Optional app version to filter by."},
                    "limit": {"type": "integer", "description": "Max number of reviews to return (default 5).", "default": 5},
                },
                "required": ["theme"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_regression_themes",
            "description": "Get themes flagged as regressions (pain increased >5% vs previous release). Use when the user asks what broke, what's new, or what regressed.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_persistence_themes",
            "description": "Get themes flagged as persistent (high pain in 3+ releases). Use when the user asks about long-standing issues or tech debt.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_theme_summary_stats",
            "description": "Get summary stats for all themes (pain share, review count, avg rating) for a version. Use for overview or comparison questions.",
            "parameters": {
                "type": "object",
                "properties": {"version": {"type": "string", "description": "Optional app version. If not provided, uses latest."}},
            },
        },
    },
]

SYSTEM_PROMPT = """You are an expert Product Management assistant for ReleasePulse, an AI-powered feedback intelligence dashboard. You help PMs interpret release data, prioritize work, and understand user feedback.

You have access to tools that query:
- Priority backlog (RICE-ranked themes)
- Sample user reviews per theme
- Regression flags (themes that got worse vs previous release)
- Persistence flags (themes that are long-standing issues)
- Theme-level summary stats

Use the tools as needed to answer the user's question. After calling tools, summarize the results in clear, actionable language. If the user asks "why" something is prioritized, use both the backlog and sample reviews to explain. Always cite specific numbers or themes when relevant. If no tool is needed (e.g. general methodology question), answer from your knowledge."""


def _run_tool(name: str, arguments: dict, ctx: dict) -> str:
    """Execute a tool by name with given arguments; ctx holds dataframes."""
    reviews = ctx.get("reviews")
    priority = ctx.get("priority")
    persistence = ctx.get("persistence")
    version_signal = ctx.get("version_signal")

    if name == "get_priority_backlog":
        top_n = int(arguments.get("top_n", 10))
        df = priority.sort_values("Priority_Score", ascending=False).head(top_n)
        rows = df[["theme", "Priority_Score", "Reach", "Impact", "Confidence", "Effort", "Is_Regression", "Is_Persistent"]].to_dict("records")
        return json.dumps(rows, indent=2)

    if name == "get_theme_reviews":
        theme = arguments.get("theme", "").strip()
        version = arguments.get("version")
        limit = int(arguments.get("limit", 5))
        if reviews is None:
            return json.dumps({"error": "No review data", "available_themes": []})
        themes_list = reviews["theme_label"].dropna().unique().tolist()
        if theme not in [str(t) for t in themes_list]:
            for t in themes_list:
                if theme.lower() in str(t).lower():
                    theme = str(t)
                    break
        sub = reviews[reviews["theme_label"].astype(str) == theme]
        if sub.empty:
            return json.dumps({"error": f"No data for theme '{theme}'", "available_themes": [str(t) for t in themes_list]})
        if version:
            sub = sub[sub["RC_ver"].astype(str) == str(version)]
        sub = sub.nlargest(limit, "final_weight")
        out = [{"content": r["content"], "score": float(r["score"]), "final_weight": float(r["final_weight"])} for _, r in sub.iterrows()]
        return json.dumps(out, indent=2)

    if name == "get_regression_themes":
        if version_signal is None:
            return json.dumps([])
        reg = version_signal[version_signal["Is_Regression"] == True]
        latest = version_signal["RC_ver"].max()
        reg = reg[reg["RC_ver"] == latest][["theme", "RC_ver", "Normalized_Signal", "Delta"]]
        return reg.to_json(orient="records", indent=2) if not reg.empty else json.dumps([])

    if name == "get_persistence_themes":
        if persistence is None:
            return json.dumps([])
        pers = persistence[persistence["Is_Persistent"] == True][["theme", "Is_Persistent"]]
        return pers.to_json(orient="records", indent=2) if not pers.empty else json.dumps([])

    if name == "get_theme_summary_stats":
        if reviews is None:
            return json.dumps({"error": "No review data"})
        version = arguments.get("version")
        df = reviews
        if version:
            df = df[df["RC_ver"].astype(str) == str(version)]
        else:
            latest = df["RC_ver"].dropna().max()
            df = df[df["RC_ver"] == latest]
        agg = df.groupby("theme_label").agg(
            total_weight=("final_weight", "sum"),
            review_count=("review_id", "count"),
            avg_rating=("score", "mean"),
        ).reset_index()
        agg["pain_share_pct"] = (100 * agg["total_weight"] / agg["total_weight"].sum()).round(2)
        return agg.to_json(orient="records", indent=2)

    return json.dumps({"error": f"Unknown tool: {name}"})


def run_agent(user_message: str, context: dict, api_key: str = None) -> str:
    """
    Run the agentic loop: LLM can call tools; we execute and feed back until we get a final answer.
    context = {"reviews": df, "priority": df, "persistence": df, "version_signal": df}
    """
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not OPENAI_AVAILABLE or not api_key:
        return (
            "**Agentic AI is not configured.** Set `OPENAI_API_KEY` in your environment and install `openai` to use the assistant. "
            "This dashboard uses an LLM with **tool-calling**: it decides which data to fetch (priority backlog, theme reviews, regressions, etc.) and then answers from that data."
        )

    client = OpenAI(api_key=api_key)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]
    max_turns = 8
    for _ in range(max_turns):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=TOOLS_OPENAI,
            tool_choice="auto",
        )
        choice = response.choices[0]
        if choice.finish_reason == "stop":
            return choice.message.content or ""
        if choice.finish_reason == "tool_calls" and choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = _run_tool(name, args, context)
                messages.append(choice.message)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": result,
                    }
                )
            continue
        return choice.message.content or ""
    return "I hit the turn limit. Please try a shorter or more focused question."
