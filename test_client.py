import asyncio
import httpx
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

SERVER_URL = "https://mcp-server-32772794748.us-south1.run.app/sse"

async def run_agent_client():
    # Force a fresh client with specific timeouts and NO HTTP/2
    timeout = httpx.Timeout(60.0, connect=30.0)
    
    # We use a standard client but ensure we don't allow HTTP/2
    async with httpx.AsyncClient(http2=False, timeout=timeout) as client:
        print(f"Connecting to MCP Server at: {SERVER_URL}...")
        
        # Use the sse_client with our pre-configured httpx client
        async with sse_client(SERVER_URL) as streams:
            async with ClientSession(streams.read, streams.write) as session:
                await session.initialize()
                
                # Verify connection
                tools_response = await session.list_tools()
                print(f"✅ Success! Tools found: {[t.name for t in tools_response.tools]}")
                
                # Call your tool
                result = await session.call_tool("fetch_gt_list", arguments={"disease_id": "EFO_0000249"})
                print(f"Data received: {result.content[0].text[:500]}...")

if __name__ == "__main__":
    asyncio.run(run_agent_client())