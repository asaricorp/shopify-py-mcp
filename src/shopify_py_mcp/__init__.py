from . import server
import asyncio
import os

def main():
    """Main entry point for the package."""
    # Check if we're running in a deployed environment (like Railway)
    if "PORT" in os.environ:
        from . import http_server
        asyncio.run(http_server.main())
    else:
        # Default to standard stdio server for local development
        asyncio.run(server.main())

# Optionally expose other important items at package level
__all__ = ['main', 'server']