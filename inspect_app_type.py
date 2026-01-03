from mcp.server.fastmcp import FastMCP
mcp = FastMCP("test")
print(f"Type: {type(mcp.sse_app)}")
print(f"Dir: {dir(mcp.sse_app)}")
