import asyncio
import os
import json
import shopify
import time

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

# Shopify API settings
SHOP_URL = os.environ.get("SHOPIFY_SHOP_URL", "")
API_KEY = os.environ.get("SHOPIFY_API_KEY", "")
API_PASSWORD = os.environ.get("SHOPIFY_API_PASSWORD", "")
API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
API_SECRET = os.environ.get("SHOPIFY_API_SECRET", "")
ADMIN_ACCESS_TOKEN = os.environ.get("SHOPIFY_ADMIN_ACCESS_TOKEN", "")


# Initialize Shopify API
def initialize_shopify_api():
    shopify.Session.setup(api_key=API_KEY, secret=API_SECRET)
    shop_url = f"https://{SHOP_URL}"
    session = shopify.Session(shop_url, API_VERSION, ADMIN_ACCESS_TOKEN)
    shopify.ShopifyResource.activate_session(session)


server = Server("shopify-py-mcp")


def get_all_shopify_products(total_limit=None, per_page_limit=250):
    """
    Function to retrieve product listings across multiple pages using the Shopify API library

    Parameters:
    total_limit (int): Total number of products to retrieve (None to retrieve all products)
    per_page_limit (int): Number of products per request (maximum 250)

    Returns:
    list: List of products
    """
    # Limit per page to 250
    per_page_limit = min(per_page_limit, 250)

    all_products = []
    next_page_url = None

    try:
        while True:
            # Check if enough products have already been retrieved
            if total_limit is not None and len(all_products) >= total_limit:
                break

            # Calculate remaining number to retrieve
            current_limit = per_page_limit
            if total_limit is not None:
                current_limit = min(per_page_limit, total_limit - len(all_products))
                if current_limit <= 0:
                    break

            # Retrieve product list
            if next_page_url:
                # Extract page_info from next_page_url
                page_info = extract_page_info(next_page_url)
                products = shopify.Product.find(
                    limit=current_limit, page_info=page_info
                )
            else:
                products = shopify.Product.find(limit=current_limit)

            # End if results are empty
            if not products:
                break

            # Add retrieved products
            all_products.extend(products)

            # Get pagination information from response headers
            response_headers = shopify.ShopifyResource.connection.response.headers
            link_header = response_headers.get("Link", "")

            # Extract next page URL
            next_page_url = extract_next_page_url(link_header)
            if not next_page_url:
                break

            # Wait a bit to avoid rate limits
            time.sleep(0.5)

    except Exception as e:
        print(f"An error occurred: {e}")

    # If total_limit is specified, return only that number
    if total_limit is not None:
        return all_products[:total_limit]

    return all_products


def extract_next_page_url(link_header):
    """
    Extract the URL of the next page from the Link header

    Parameters:
    link_header (str): Link header from the response

    Returns:
    str: URL of the next page (None if it doesn't exist)
    """
    if not link_header:
        return None

    links = link_header.split(",")
    for link in links:
        parts = link.split(";")
        if len(parts) != 2:
            continue

        url = parts[0].strip().strip("<>")
        rel = parts[1].strip()

        if 'rel="next"' in rel:
            return url

    return None


def extract_page_info(next_page_url):
    """
    Extract the page_info parameter from a URL

    Parameters:
    next_page_url (str): URL of the next page

    Returns:
    str: page_info parameter
    """
    import urllib.parse

    parsed_url = urllib.parse.urlparse(next_page_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)

    if "page_info" in query_params:
        return query_params["page_info"][0]

    return None


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    Returns a list of available tools.
    Each tool specifies its arguments using JSON Schema.
    """
    return [
        types.Tool(
            name="list_products",
            description="Get product list",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Number of products to retrieve (maximum 250)",
                        "minimum": 1,
                        "maximum": 250,
                        "default": 50,
                    },
                },
            },
        ),
        types.Tool(
            name="get_product",
            description="Get detailed product information",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "number", "description": "Product ID"}
                },
                "required": ["product_id"],
            },
        ),
        types.Tool(
            name="create_product",
            description="Create a new product",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Product name"},
                    "body_html": {
                        "type": "string",
                        "description": "Product description (HTML format)",
                    },
                    "vendor": {"type": "string", "description": "Vendor name"},
                    "product_type": {"type": "string", "description": "Product type"},
                    "tags": {"type": "string", "description": "Tags (comma-separated)"},
                    "status": {
                        "type": "string",
                        "description": "Status",
                        "enum": ["active", "draft", "archived"],
                        "default": "active",
                    },
                    "variants": {
                        "type": "array",
                        "description": "Variants",
                        "items": {
                            "type": "object",
                            "properties": {
                                "price": {"type": "string", "description": "Price"},
                                "sku": {"type": "string", "description": "SKU"},
                                "inventory_quantity": {
                                    "type": "number",
                                    "description": "Inventory quantity",
                                },
                                "option1": {
                                    "type": "string",
                                    "description": "Option 1 value",
                                },
                                "option2": {
                                    "type": "string",
                                    "description": "Option 2 value",
                                },
                                "option3": {
                                    "type": "string",
                                    "description": "Option 3 value",
                                },
                            },
                            "required": ["price"],
                        },
                    },
                    "options": {
                        "type": "array",
                        "description": "Options",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Option name",
                                },
                                "position": {
                                    "position": "number",
                                    "description": "Option order",
                                },
                                "values": {
                                    "type": "array",
                                    "description": "Option values",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["name", "position", "values"],
                        },
                    },
                    "images": {
                        "type": "array",
                        "description": "Images",
                        "items": {
                            "type": "object",
                            "properties": {
                                "src": {"type": "string", "description": "Image URL"},
                                "alt": {
                                    "type": "string",
                                    "description": "Alternative text",
                                },
                            },
                            "required": ["src"],
                        },
                    },
                },
                "required": ["title"],
            },
        ),
        types.Tool(
            name="update_product",
            description="Update a product",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "number", "description": "Product ID"},
                    "title": {"type": "string", "description": "Product name"},
                    "body_html": {
                        "type": "string",
                        "description": "Product description (HTML format)",
                    },
                    "vendor": {"type": "string", "description": "Vendor name"},
                    "product_type": {"type": "string", "description": "Product type"},
                    "tags": {"type": "string", "description": "Tags (comma-separated)"},
                    "status": {
                        "type": "string",
                        "description": "Status",
                        "enum": ["active", "draft", "archived"],
                    },
                    "variants": {
                        "type": "array",
                        "description": "Variants",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {
                                    "type": "number",
                                    "description": "Variant ID",
                                },
                                "price": {"type": "string", "description": "Price"},
                                "sku": {"type": "string", "description": "SKU"},
                                "inventory_quantity": {
                                    "type": "number",
                                    "description": "Inventory quantity",
                                },
                                "option1": {
                                    "type": "string",
                                    "description": "Option 1 value",
                                },
                                "option2": {
                                    "type": "string",
                                    "description": "Option 2 value",
                                },
                                "option3": {
                                    "type": "string",
                                    "description": "Option 3 value",
                                },
                            },
                        },
                    },
                    "options": {
                        "type": "array",
                        "description": "Options",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "number", "description": "Option ID"},
                                "name": {
                                    "type": "string",
                                    "description": "Option name",
                                },
                                "position": {
                                    "position": "number",
                                    "description": "Option order",
                                },
                                "values": {
                                    "type": "array",
                                    "description": "Option values",
                                    "items": {"type": "string"},
                                },
                            },
                            "required": ["name", "values"],
                        },
                    },
                    "images": {
                        "type": "array",
                        "description": "Images",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "number", "description": "Image ID"},
                                "src": {"type": "string", "description": "Image URL"},
                                "alt": {
                                    "type": "string",
                                    "description": "Alternative text",
                                },
                            },
                            "required": ["src"],
                        },
                    },
                },
                "required": ["product_id"],
            },
        ),
        types.Tool(
            name="delete_product",
            description="Delete a product",
            inputSchema={
                "type": "object",
                "properties": {
                    "product_id": {"type": "number", "description": "Product ID"}
                },
                "required": ["product_id"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Processes tool execution requests.
    """
    try:
        initialize_shopify_api()

        if name == "list_products":
            return await handle_list_products(arguments or {})
        elif name == "get_product":
            return await handle_get_product(arguments or {})
        elif name == "create_product":
            return await handle_create_product(arguments or {})
        elif name == "update_product":
            return await handle_update_product(arguments or {})
        elif name == "delete_product":
            return await handle_delete_product(arguments or {})
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"An error occurred: {str(e)}",
            )
        ]


async def handle_list_products(arguments: dict) -> list[types.TextContent]:
    """Get product list"""
    limit = int(arguments.get("limit", 50))
    products = get_all_shopify_products(
        total_limit=limit, per_page_limit=250  # Retrieve up to 250 products per request
    )

    result = []
    for product in products:
        result.append(
            {
                "id": product.id,
                "title": product.title,
                "vendor": product.vendor,
                "product_type": product.product_type,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                "status": product.status,
                "variants_count": len(product.variants),
                "images_count": len(product.images),
            }
        )

    return [
        types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False),
        )
    ]


async def handle_get_product(arguments: dict) -> list[types.TextContent]:
    """Get detailed product information"""
    product_id = arguments.get("product_id")
    if not product_id:
        raise ValueError("product_id is required")

    product = shopify.Product.find(product_id)

    # Format product information
    result = {
        "id": product.id,
        "title": product.title,
        "body_html": product.body_html,
        "vendor": product.vendor,
        "product_type": product.product_type,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "status": product.status,
        "tags": product.tags,
        "variants": [],
        "options": [],
        "images": [],
    }

    # Variant information
    for variant in product.variants:
        result["variants"].append(
            {
                "id": variant.id,
                "title": variant.title,
                "price": variant.price,
                "sku": variant.sku,
                "inventory_quantity": variant.inventory_quantity,
                "option1": variant.option1,
                "option2": variant.option2,
                "option3": variant.option3,
            }
        )

    # Option information
    for option in product.options:
        result["options"].append(
            {"id": option.id, "name": option.name, "values": option.values}
        )

    # Image information
    for image in product.images:
        result["images"].append({"id": image.id, "src": image.src, "alt": image.alt})

    return [
        types.TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False),
        )
    ]


async def handle_create_product(arguments: dict) -> list[types.TextContent]:
    """Create a new product"""
    # Check required parameters
    title = arguments.get("title")
    if not title:
        raise ValueError("title is required")

    # Create product object
    product = shopify.Product()
    product.title = title

    # Set optional parameters
    if "body_html" in arguments:
        product.body_html = arguments["body_html"]
    if "vendor" in arguments:
        product.vendor = arguments["vendor"]
    if "product_type" in arguments:
        product.product_type = arguments["product_type"]
    if "tags" in arguments:
        product.tags = arguments["tags"]
    if "status" in arguments:
        product.status = arguments["status"]

    # Set options
    if "options" in arguments and arguments["options"]:
        options = []
        for option_data in arguments["options"]:
            option = shopify.Option()
            option.name = option_data["name"]
            option.position = option_data["position"]
            option.values = option_data["values"]
            options.append(option)
        product.options = options

    # Set variants
    if "variants" in arguments and arguments["variants"]:
        variants = []
        for variant_data in arguments["variants"]:
            variant = shopify.Variant()
            if "price" in variant_data:
                variant.price = variant_data["price"]
            if "sku" in variant_data:
                variant.sku = variant_data["sku"]
            if "inventory_quantity" in variant_data:
                variant.inventory_quantity = variant_data["inventory_quantity"]
            if "option1" in variant_data:
                variant.option1 = variant_data["option1"]
            if "option2" in variant_data:
                variant.option2 = variant_data["option2"]
            if "option3" in variant_data:
                variant.option3 = variant_data["option3"]
            variants.append(variant)
        product.variants = variants

    # Set images
    if "images" in arguments and arguments["images"]:
        for image_data in arguments["images"]:
            image = shopify.Image()
            image.src = image_data["src"]
            if "alt" in image_data:
                image.alt = image_data["alt"]
            product.images.append(image)

    # Save product
    product.save()

    return [
        types.TextContent(
            type="text",
            text=json.dumps(
                {
                    "success": True,
                    "product_id": product.id,
                    "message": f"Product '{product.title}' has been created",
                },
                indent=2,
                ensure_ascii=False,
            ),
        )
    ]


async def handle_update_product(arguments: dict) -> list[types.TextContent]:
    """Update a product"""
    # Check required parameters
    product_id = arguments.get("product_id")
    if not product_id:
        raise ValueError("product_id is required")

    # Get product
    product = shopify.Product.find(product_id)

    # Update product information
    if "title" in arguments:
        product.title = arguments["title"]
    if "body_html" in arguments:
        product.body_html = arguments["body_html"]
    if "vendor" in arguments:
        product.vendor = arguments["vendor"]
    if "product_type" in arguments:
        product.product_type = arguments["product_type"]
    if "tags" in arguments:
        product.tags = arguments["tags"]
    if "status" in arguments:
        product.status = arguments["status"]

    # Update variants
    if "variants" in arguments and arguments["variants"]:
        for variant_data in arguments["variants"]:
            # Update existing variant if variant ID exists
            if "id" in variant_data:
                for variant in product.variants:
                    if variant.id == variant_data["id"]:
                        if "price" in variant_data:
                            variant.price = variant_data["price"]
                        if "sku" in variant_data:
                            variant.sku = variant_data["sku"]
                        if "inventory_quantity" in variant_data:
                            variant.inventory_quantity = variant_data[
                                "inventory_quantity"
                            ]
                        if "option1" in variant_data:
                            variant.option1 = variant_data["option1"]
                        if "option2" in variant_data:
                            variant.option2 = variant_data["option2"]
                        if "option3" in variant_data:
                            variant.option3 = variant_data["option3"]
            # Add new variant if variant ID doesn't exist
            else:
                variant = shopify.Variant()
                variant.product_id = product.id
                if "price" in variant_data:
                    variant.price = variant_data["price"]
                if "sku" in variant_data:
                    variant.sku = variant_data["sku"]
                if "inventory_quantity" in variant_data:
                    variant.inventory_quantity = variant_data["inventory_quantity"]
                if "option1" in variant_data:
                    variant.option1 = variant_data["option1"]
                if "option2" in variant_data:
                    variant.option2 = variant_data["option2"]
                if "option3" in variant_data:
                    variant.option3 = variant_data["option3"]
                product.variants.append(variant)

    # Update options
    if "options" in arguments and arguments["options"]:
        for option_data in arguments["options"]:
            # Update existing option if option ID exists
            if "id" in option_data:
                for option in product.options:
                    if option.id == option_data["id"]:
                        option.name = option_data["name"]
                        option.values = option_data["values"]
            # Add new option if option ID doesn't exist
            else:
                option = shopify.Option()
                option.product_id = product.id
                option.name = option_data["name"]
                option.values = option_data["values"]
                product.options.append(option)

    # Update images
    if "images" in arguments and arguments["images"]:
        for image_data in arguments["images"]:
            # Update existing image if image ID exists
            if "id" in image_data:
                for image in product.images:
                    if image.id == image_data["id"]:
                        image.src = image_data["src"]
                        if "alt" in image_data:
                            image.alt = image_data["alt"]
            # Add new image if image ID doesn't exist
            else:
                image = shopify.Image()
                image.product_id = product.id
                image.src = image_data["src"]
                if "alt" in image_data:
                    image.alt = image_data["alt"]
                product.images.append(image)

    # Save product
    product.save()

    return [
        types.TextContent(
            type="text",
            text=json.dumps(
                {
                    "success": True,
                    "product_id": product.id,
                    "message": f"Product '{product.title}' has been updated",
                },
                indent=2,
                ensure_ascii=False,
            ),
        )
    ]


async def handle_delete_product(arguments: dict) -> list[types.TextContent]:
    """Delete a product"""
    # Check required parameters
    product_id = arguments.get("product_id")
    if not product_id:
        raise ValueError("product_id is required")

    # Get product
    product = shopify.Product.find(product_id)

    # Save product name
    product_title = product.title

    # Delete product
    product.destroy()

    return [
        types.TextContent(
            type="text",
            text=json.dumps(
                {
                    "success": True,
                    "message": f"Product '{product_title}' has been deleted",
                },
                indent=2,
                ensure_ascii=False,
            ),
        )
    ]


async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="shopify-py-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
