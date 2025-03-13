# Shopify Python MCP Server

An MCP server that integrates with the Shopify API. This server allows you to retrieve and manipulate Shopify product information from Claude Desktop.

## Features

### Tools

This server provides the following tools:

1. **list_products**: Get product list
   - `limit`: Number of products to retrieve (maximum 250, default is 50)

2. **get_product**: Get detailed product information
   - `product_id`: Product ID (required)

3. **create_product**: Create a new product
   - `title`: Product name (required)
   - `body_html`: Product description (HTML format)
   - `vendor`: Vendor name
   - `product_type`: Product type
   - `tags`: Tags (comma-separated)
   - `status`: Status (active/draft/archived)
   - `variants`: Variants
   - `options`: Options
   - `images`: Images

4. **update_product**: Update a product
   - `product_id`: Product ID (required)
   - `title`: Product name
   - `body_html`: Product description (HTML format)
   - `vendor`: Vendor name
   - `product_type`: Product type
   - `tags`: Tags (comma-separated)
   - `status`: Status (active/draft/archived)
   - `variants`: Variants
   - `options`: Options
   - `images`: Images

5. **delete_product**: Delete a product
   - `product_id`: Product ID (required)

## Configuration

### Required Environment Variables

To use this server, you need to set the following environment variables:

- `SHOPIFY_SHOP_URL`: Shopify store URL (e.g., mystore.myshopify.com)
- `SHOPIFY_API_KEY`: Shopify Admin API key
- `SHOPIFY_API_PASSWORD`: Shopify Admin API password (Secret)
- `SHOPIFY_API_VERSION`: Shopify API version (default: 2025-01)
- `SHOPIFY_ADMIN_ACCESS_TOKEN`: Shopify Admin API access token

### Claude Desktop Configuration

To use with Claude Desktop, add the following configuration to claude_desktop_config.json:

#### macOS
Configuration file location: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
"mcpServers": {
  "shopify-py-mcp": {
    "command": "uv",
    "args": [
      "--directory",
      "/your_path/shopify-py-mcp",
      "run",
      "shopify-py-mcp"
    ],
    "env": {
      "SHOPIFY_SHOP_URL": "your-store.myshopify.com",
      "SHOPIFY_API_KEY": "your-api-key",
      "SHOPIFY_API_PASSWORD": "your-api-password",
      "SHOPIFY_API_VERSION": "2025-01",
      "SHOPIFY_ADMIN_ACCESS_TOKEN": "admin-api-access-token"
    }
  }
}
```

## Railway Deployment

To deploy this server to Railway for use with web-based MCP clients:

1. Fork or clone this repository to your GitHub account
2. Sign up for a [Railway account](https://railway.app/)
3. Create a new project in Railway from your GitHub repository
4. Add the required environment variables in the Railway dashboard:
   - `SHOPIFY_SHOP_URL`
   - `SHOPIFY_API_KEY`
   - `SHOPIFY_API_PASSWORD`
   - `SHOPIFY_API_VERSION`
   - `SHOPIFY_ADMIN_ACCESS_TOKEN`
5. Deploy your application

The repository includes the following files for Railway deployment:
- `Procfile`: Tells Railway how to run the application
- `setup.py`: Ensures the package is installed properly
- `requirements.txt`: Lists all dependencies
- `runtime.txt`: Specifies the Python version

Once deployed, Railway will provide you with a URL for your service. Use this URL to configure your web-based MCP clients:

- MCP List Tools Endpoint: `https://your-railway-app-url.railway.app/mcp/list_tools`
- MCP Call Tool Endpoint: `https://your-railway-app-url.railway.app/mcp/call_tool`

### Testing Your Deployment

To verify your deployment is working:

```bash
# Test the root endpoint
curl https://your-railway-app-url.railway.app/

# Test the list_tools endpoint
curl -X POST https://your-railway-app-url.railway.app/mcp/list_tools
```

### Troubleshooting Railway Deployment

If you encounter issues with the deployment:

1. Check the Railway logs for error messages
2. Ensure all environment variables are set correctly
3. Verify that the package is being installed properly by checking the build logs
4. Try redeploying the application

## Usage

To use this server with Claude Desktop, call the tools as follows:

### Get Product List

```
Please get the product list.
```

### Get Detailed Product Information

```
Please get the detailed information for product ID 1234567890.
```

### Create a New Product

```
Please create a new product with the following information:
- Product name: Sample Product
- Description: This is a sample product.
- Price: $1000
```

### Update a Product

```
Please update product ID 1234567890 with the following information:
- Product name: Updated Product Name
- Price: $2000
```

### Delete a Product

```
Please delete product ID 1234567890.
```

## Development

### Install Dependencies

```bash
cd shopify-py-mcp
uv sync --dev --all-extras
```

### Debugging

You can debug using MCP Inspector:

```bash
npx @modelcontextprotocol/inspector uv --directory /your_path/shopify-py-mcp run shopify-py-mcp
```

### Build and Publish

To prepare the package for distribution:

1. Synchronize dependencies and update the lock file:
```bash
uv sync
```

2. Build the package:
```bash
uv build
```

3. Publish to PyPI:
```bash
uv publish
```

Note: You need to set PyPI authentication credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`