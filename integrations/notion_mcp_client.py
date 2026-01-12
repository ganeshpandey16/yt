import requests
from llm_ai import AINotesService

MCP_SERVER_URL = "http://localhost:8000"


SYSTEM_PROMPT = """
You are an AI assistant with access to Notion tools.

You can:
- create pages
- update pages
- archive pages
- append blocks to pages

When the user asks to store or manage content in Notion,
you MUST call the appropriate tool.

Think step by step and use tools when required.
"""


class NotionMCPClient:
    def __init__(self):
        self.ai = AINotesService()

    def list_tools(self):
        r = requests.get(f"{MCP_SERVER_URL}/tools")
        r.raise_for_status()
        return r.json()["tools"]

    def call_tool(self, tool_name: str, arguments: dict):
        r = requests.post(
            f"{MCP_SERVER_URL}/tools/{tool_name}",
            json=arguments,
        )
        r.raise_for_status()
        return r.json()

    def run(self, user_prompt: str):
        # 1️⃣ Fetch MCP tools
        tools = self.list_tools()

        # 2️⃣ Call LLM with tools
        response = self.ai.generate_notes_with_tools(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
            tools=tools,
        )

        message = response["choices"][0]["message"]

        # 3️⃣ Execute tool calls
        if "tool_calls" in message:
            for call in message["tool_calls"]:
                tool_name = call["function"]["name"]
                args = call["function"]["arguments"]

                print(f"\n🔧 Calling MCP tool: {tool_name}")
                print(f"📦 Args: {args}")

                result = self.call_tool(tool_name, args)
                print(f"✅ Tool result: {result}")

        else:
            print("\n📝 Model output:")
            print(message["content"])
