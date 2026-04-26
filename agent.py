import anthropic
import os
from tavily import TavilyClient

client = None
tavily = None

def get_client():
    global client
    if client is None:
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return client

def get_tavily():
    global tavily
    if tavily is None:
        tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
    return tavily

TOOLS = [
    {
        "name": "web_search",
        "description": "Search the web for current information.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "calculate",
        "description": "Evaluate a mathematical expression.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {"type": "string"}
            },
            "required": ["expression"]
        }
    }
]

def web_search(query: str) -> str:
    results = get_tavily().search(query=query, max_results=3)
    return "\n".join([r["content"] for r in results["results"]])

def calculate(expression: str) -> str:
    try:
        return str(eval(expression, {"__builtins__": {}}))
    except Exception as e:
        return f"Error: {e}"

def run_tool(name: str, inputs: dict) -> str:
    if name == "web_search":
        return web_search(inputs["query"])
    elif name == "calculate":
        return calculate(inputs["expression"])
    return "Unknown tool"

def run_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    system = """You are an expert MTB (mountain bike) and eMTB (electric mountain bike) assistant specializing in bike setup, suspension tuning, geometry, components, and trail recommendations.

STRICT RULES:
- Only answer questions related to mountain biking and cycling.
- If asked about anything unrelated, politely decline and remind the user you are an MTB specialist.
- Use web search when you need current or specific information.
- Always give practical, specific advice.

RESPONSE STYLE - THIS IS CRITICAL:
- Be concise and direct. Answer the question asked, nothing more.
- Do NOT use emojis unless the user uses them first.
- Do NOT use markdown tables unless explicitly asked for a comparison.
- Do NOT use headers (##, ###) in responses.
- Do NOT add follow-up questions like "Are you trying to decide?" unless the user's question is genuinely ambiguous.
- Do NOT add commentary, jokes, or filler text.
- If the user asks for a single value (e.g. wheelbase), give that value and one sentence of context maximum.

Example of BAD response to "wheelbase of Intense Tracer 29 XL 2023":
  "Ha, I feel you! 😄 The 2023 Intense Tracer 29 in XL has a seriously long wheelbase. Here's the breakdown: [giant table with everything]"

Example of GOOD response to "wheelbase of Intense Tracer 29 XL 2023":
  "The 2023 Intense Tracer 29 XL has a wheelbase of 1,296mm in low position and 1,265mm in high position."
"""

    for _ in range(10):
        response = get_client().messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            system=system,
            tools=TOOLS,
            messages=messages
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return "Done."

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    result = run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })

            messages.append({"role": "user", "content": tool_results})

    return "Agent reached maximum iterations."