import asyncio
import os
import json
from aiohttp import web
from shopify_py_mcp.server import server, initialize_shopify_api, handle_list_tools, handle_call_tool

# Initialize Shopify API
initialize_shopify_api()

# Get port from environment variable (Railway sets this)
PORT = int(os.environ.get("PORT", 8000))

# Create routes for the HTTP server
routes = web.RouteTableDef()

@routes.post("/mcp/list_tools")
async def http_handle_list_tools(request):
    """Handle list_tools request"""
    tools = await handle_list_tools()
    return web.json_response({"tools": [tool.model_dump() for tool in tools]})

@routes.post("/mcp/call_tool")
async def http_handle_call_tool(request):
    """Handle call_tool request"""
    data = await request.json()
    name = data.get("name")
    arguments = data.get("arguments")
    
    if not name:
        return web.json_response({"error": "Tool name is required"}, status=400)
    
    result = await handle_call_tool(name, arguments)
    return web.json_response({"result": [item.model_dump() for item in result]})

@routes.get("/")
async def handle_root(request):
    """Handle root request"""
    return web.json_response({
        "name": "Shopify Python MCP Server",
        "version": "0.1.0",
        "description": "An MCP server that integrates with the Shopify API"
    })

async def main():
    # Create the web application
    app = web.Application()
    app.add_routes(routes)
    
    # Start the web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    
    print(f"Server started on port {PORT}")
    print(f"MCP endpoint available at: http://localhost:{PORT}/mcp")
    
    # Keep the server running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())