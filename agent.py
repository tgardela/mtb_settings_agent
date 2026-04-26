import anthropic
import os
from tavily import TavilyClient

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

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
    results = tavily.search(query=query, max_results=3)
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
    system = "You are a helpful AI assistant. Use tools when needed to give accurate answers."

    for _ in range(10):
        response = client.messages.create(
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