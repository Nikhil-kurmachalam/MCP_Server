from mcp.server.fastmcp import FastMCP
import inspect
try:
    print(f"Signature: {inspect.signature(FastMCP.run)}")
except Exception as e:
    print(e)
