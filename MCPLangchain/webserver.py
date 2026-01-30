from mcp.server.fastmcp import FastMCP
import httpx
from bs4 import BeautifulSoup

mcp = FastMCP("WebFetcher")

@mcp.tool()
async def fetch_url(url: str) -> str:
    """
    Fetch the content of a URL and return a summary of the text.
    Useful for reading articles, documentation, or any website content.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers, timeout=10.0)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()
            
            # Get text
            text = soup.get_text()
            
            # Break into lines and remove leading and trailing space on each
            lines = (line.strip() for line in text.splitlines())
            # Break multi-headlines into a line each
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            # Drop blank lines
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit length to avoid context window issues
            return text[:5000] + ("..." if len(text) > 5000 else "")
            
        except Exception as e:
            return f"Error fetching URL: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
