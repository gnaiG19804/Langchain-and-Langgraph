from langgraph.graph import StateGraph, START,END
from src.langgraphagenticai.state.state import State
from src.langgraphagenticai.nodes.basic_chatbot_node import BasicChatBotNode
from src.langgraphagenticai.tools.search_tool import get_tools, create_tool_nodes
from langgraph.prebuilt import tools_condition,ToolNode
from src.langgraphagenticai.nodes.chatbot_with_Tool_node import ChatbotWithToolNode
from src.langgraphagenticai.nodes.ai_news_node import AINewsNode



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

    def chatbot_with_tools_build_graph(self):
        """Builds a chatbot with tools graph structure."""
        tools = get_tools()
        tool_node = create_tool_nodes(tools)

        llm=self.llm

        obj_chatbot_with_tool_node= ChatbotWithToolNode(llm)
        chatbot_node = obj_chatbot_with_tool_node.create_chatbot(tools)
        # add nodes and edges
        self.graph_builder.add_node("chatbot", chatbot_node)
        self.graph_builder.add_node("tools",tool_node)

        self.graph_builder.add_edge(START,"chatbot")
        self.graph_builder.add_conditional_edges("chatbot",tools_condition)
        self.graph_builder.add_edge("tools","chatbot")
        self.graph_builder.add_edge("chatbot",END)


    def ai_news_build_graph(self):
        """Builds an AI News graph structure."""
        # Implementation for AI News graph can be added here

        ai_news_node= AINewsNode(self.llm)

        self.graph_builder.add_node("fetch_news",ai_news_node.fetch_news)
        self.graph_builder.add_node("summarize_news",ai_news_node.summarize_news)
        self.graph_builder.add_node("save_result",ai_news_node.save_result)

        self.graph_builder.set_entry_point("fetch_news")
        self.graph_builder.add_edge("fetch_news","summarize_news")
        self.graph_builder.add_edge("summarize_news","save_result")
        self.graph_builder.add_edge("save_result",END)

    def setup_graph(self,usecase:str):
        """Sets up the graph based on the selected use case."""
        if usecase == "Basic Chatbot":
            self.basic_chatbot_build_graph()
            return self.graph_builder.compile()
        elif usecase == "Chatbot with Web":
            self.chatbot_with_tools_build_graph()
            return self.graph_builder.compile()
        if usecase == "AI News":
            self.ai_news_build_graph()
            return self.graph_builder.compile()
        return None