from setuptools import setup, find_packages

setup(
    name="shopify-py-mcp",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "mcp>=1.3.0",
        "ShopifyAPI>=1.0.0",
        "aiohttp>=3.8.0",
    ],
    entry_points={
        "console_scripts": [
            "shopify-py-mcp=shopify_py_mcp:main",
        ],
    },
) 