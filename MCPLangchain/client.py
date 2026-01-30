from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import asyncio
import os
import sys

load_dotenv()

async def main():
    print("Initializing MCP Client...")
    
    # Check API Key
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY not found in .env")
        return

    try:
        client = MultiServerMCPClient(
            {
                "math": {
                    "command": "python",
                    "args": ["mathserver.py"],
                    "transport": "stdio",
                },
                "weather": {
                    "command": "python",
                    "args": ["weather.py"],
                    "transport": "stdio",
                },
                "web": {
                    "command": "python",
                    "args": ["webserver.py"],
                    "transport": "stdio",
                }
            }
        )
    except Exception as e:
        print(f"Failed to initialize client: {e}")
        return

    try:
        # Create Agent
        tools = await client.get_tools()
        model = ChatGroq(model="llama-3.3-70b-versatile")
        agent = create_react_agent(model, tools)
        
        print("\n--- MCP Demo Agent Ready ---")
        print("Type 'quit', 'exit', or 'q' to stop.")
        print("Examples:")
        print("  - q: What is (3 + 5) * 12?")
        print("  - q: What is the weather in Hanoi?")
        print("----------------------------\n")

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            
            if not user_input:
                continue

            print("Agent is thinking...", end="\r")
            try:
                response = await agent.ainvoke(
                    {"messages": [{"role": "user", "content": user_input}]}
                )
                print(" " * 20, end="\r") # Clear "thinking"
                print(f"Agent: {response['messages'][-1].content}\n")
            except Exception as e:
                print(f"\nError processing request: {e}\n")

    except Exception as e:
        print(f"Runtime error: {e}")
    finally:
        # Cleanup if needed
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
