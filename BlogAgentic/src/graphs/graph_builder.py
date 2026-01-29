from langgraph.graph import StateGraph, START,END
from src.llms.groqllm import GroqLLM
from src.states.blogstate import BlogState
from src.nodes.node import BlogNode


class GraphBuilder:
  def __init__(self,llm):
    self.llm = llm
    self.graph= StateGraph(BlogState)

  def build_critique_with_translation_graph(self):
    """Build a graph with critique, refinement AND translation"""
    
    self.blog_node_obj = BlogNode(self.llm)
    
    # Nodes
    self.graph.add_node("title_creation", self.blog_node_obj.title_creation)
    self.graph.add_node("content_generation", self.blog_node_obj.content_generation)
    self.graph.add_node("critique", self.blog_node_obj.critique_content)
    self.graph.add_node("improve", self.blog_node_obj.improve_content)
    self.graph.add_node("route", self.blog_node_obj.route)
    self.graph.add_node("vietnamese_translation", lambda state: self.blog_node_obj.translation({**state, "current_language": "vietnamese"}))
    self.graph.add_node("chinese_translation", lambda state: self.blog_node_obj.translation({**state, "current_language": "chinese"}))
    
    # Edges
    self.graph.add_edge(START, "title_creation")
    self.graph.add_edge("title_creation", "content_generation")
    self.graph.add_edge("content_generation", "critique")
    
    # Critique loop
    self.graph.add_conditional_edges(
      "critique",
      self.blog_node_obj.critique_decision,
      {
        "improve": "improve",
        "end": "route"  # Khi đã OK, đi đến route để dịch
      }
    )
    self.graph.add_edge("improve", "critique")
    
    # Translation routing
    self.graph.add_conditional_edges(
      "route",
      self.blog_node_obj.route_decision,
      {
        "vietnamese": "vietnamese_translation",
        "chinese": "chinese_translation",
      }
    )
    
    self.graph.add_edge("vietnamese_translation", END)
    self.graph.add_edge("chinese_translation", END)
    
    return self.graph
  def setup_graph(self,usecase):
    if usecase =="topic":
      self.build_topic_graph()
    elif usecase =="language":
      self.build_language_graph()
    elif usecase == "critique":
      self.build_critique_graph()
    elif usecase == "critique_with_translation":
      self.build_critique_with_translation_graph()

    return self.graph.compile()
    

#Below code is for langgraph studio

llm= GroqLLM().get_llm()

graph_builder= GraphBuilder(llm)
graph= graph_builder.build_critique_with_translation_graph().compile()

