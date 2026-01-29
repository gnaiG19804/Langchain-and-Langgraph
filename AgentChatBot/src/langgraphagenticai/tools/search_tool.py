from langchain_tavily import TavilySearch
from langgraph.prebuilt import ToolNode

def get_tools():
  """
  Return the list of tools to be used in the agent
  """
  tools = [TavilySearch(max_results=2)]
  return tools

def create_tool_nodes(tools):
  """
  Create ToolNode instances for each tool
  """
  return  ToolNode(tools=tools)