from langgraph.graph import StateGraph, START,END
from src.langgraphagenticai.state.state import State
from src.langgraphagenticai.nodes.basic_chatbot_node import BasicChatBotNode
class GraphBuilder:
    def __init__(self,model):
        self.llm= model
        self.graph_builder = StateGraph(State)

    def basic_chatbot_build_graph(self):
        """Builds a basic chatbot graph structure."""
        
        self.basic_chatbot_node= BasicChatBotNode(self.llm)
 
        self.graph_builder.add_node("chatbot",self.basic_chatbot_node.process)
        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_edge("chatbot",END)

    def setup_graph(self,usecase:str):
        """Sets up the graph based on the selected use case."""
        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
            return self.graph_builder.compile()
        return None