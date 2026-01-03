from mcp.server.fastmcp import FastMCP
import inspect
mcp = FastMCP("test")
print(inspect.signature(mcp.sse_app))
