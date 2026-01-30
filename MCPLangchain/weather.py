from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get the real weather for a location using wttr.in."""
    url = f"https://wttr.in/{location}?format=3"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.text.strip()
        except Exception as e:
            return f"Error fetching weather: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
