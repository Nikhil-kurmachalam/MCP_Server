from mcp.server.fastmcp import FastMCP
mcp = FastMCP("test")
app = mcp.sse_app
for route in app.routes:
    print(f"Route: {route.path} {route.name}")
