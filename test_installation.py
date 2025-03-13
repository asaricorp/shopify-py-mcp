#!/usr/bin/env python
"""
Test script to verify the installation of the shopify_py_mcp package.
"""

import sys
import importlib.util

def check_module(module_name):
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✅ Module '{module_name}' is installed and can be imported.")
        return True
    except ImportError as e:
        print(f"❌ Module '{module_name}' cannot be imported: {e}")
        return False

def main():
    """Main function to check the installation."""
    print("Testing shopify_py_mcp installation...")
    
    # Check required modules
    modules = [
        "shopify_py_mcp",
        "shopify_py_mcp.server",
        "shopify_py_mcp.http_server",
        "aiohttp",
        "mcp",
        "shopify",
    ]
    
    all_passed = True
    for module in modules:
        if not check_module(module):
            all_passed = False
    
    if all_passed:
        print("\nAll modules are installed correctly! 🎉")
        return 0
    else:
        print("\nSome modules are missing or cannot be imported. 😢")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 