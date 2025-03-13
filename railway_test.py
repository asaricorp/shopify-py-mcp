#!/usr/bin/env python
"""
Test script to verify the deployment on Railway.
"""

import os
import sys
import importlib.util

def check_environment_variables():
    """Check if all required environment variables are set."""
    required_vars = [
        "SHOPIFY_SHOP_URL",
        "SHOPIFY_API_KEY",
        "SHOPIFY_API_PASSWORD",
        "SHOPIFY_API_VERSION",
        "SHOPIFY_ADMIN_ACCESS_TOKEN",
        "PORT",
    ]
    
    all_set = True
    for var in required_vars:
        if var in os.environ:
            print(f"✅ Environment variable '{var}' is set.")
        else:
            print(f"❌ Environment variable '{var}' is not set.")
            all_set = False
    
    return all_set

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
    """Main function to check the deployment."""
    print("Testing Railway deployment...")
    print("\nChecking environment variables:")
    env_vars_ok = check_environment_variables()
    
    print("\nChecking required modules:")
    modules = [
        "shopify_py_mcp",
        "shopify_py_mcp.server",
        "shopify_py_mcp.http_server",
        "aiohttp",
        "mcp",
        "shopify",
    ]
    
    modules_ok = True
    for module in modules:
        if not check_module(module):
            modules_ok = False
    
    if env_vars_ok and modules_ok:
        print("\nAll checks passed! The deployment should work correctly. 🎉")
        return 0
    else:
        print("\nSome checks failed. Please fix the issues before deploying. 😢")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 