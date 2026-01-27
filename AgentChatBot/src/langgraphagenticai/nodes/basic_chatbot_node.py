from src.langgraphagenticai.state.state import State

class BasicChatBotNode:
  """Basic chatbot logic implementation."""

  def __init__(self,model):
    self.llm= model

  def process(self, state:State)->dict:
    """Processes the state and generates a chatbot response."""
    messages= state["messages"]
    response= self.llm.invoke(messages)
    return {"messages": response}