import asyncio
import os
from dotenv import load_dotenv
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams

load_dotenv()

async def test():
    try:
        key = os.getenv("STITCH_API_KEY")
        print(f"Connecting to Stitch MCP with key: {key[:4]}...{key[-4:] if key else 'None'}")
        
        stitch_toolset = McpToolset(
            connection_params=StreamableHTTPConnectionParams(
                url="https://stitch.googleapis.com/mcp",
                headers={"X-Goog-Api-Key": key}
            )
        )
        
        print("Connecting to Stitch MCP...")
        tools = await stitch_toolset.get_tools()
        print(f"Successfully loaded {len(tools)} tools from Stitch MCP")
        for t in tools:
            print(f"- {t.name}")
    except Exception as e:
        print(f"Error connecting to Stitch MCP: {e}")

if __name__ == "__main__":
    asyncio.run(test())
