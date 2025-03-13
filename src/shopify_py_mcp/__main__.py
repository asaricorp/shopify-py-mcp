import os
import asyncio

if __name__ == "__main__":
    # Check if we're running in a deployed environment
    if "PORT" in os.environ:
        from shopify_py_mcp.http_server import main
        asyncio.run(main())
    else:
        from shopify_py_mcp.server import main
        asyncio.run(main()) 