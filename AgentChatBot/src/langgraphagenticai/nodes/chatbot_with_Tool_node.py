from src.langgraphagenticai.state.state import State

class ChatbotWithToolNode:
    """Chatbot login enhanced with tool integration."""

    def __init__(self, model):
        self.llm = model

    def process(self, state: State) -> State:
        """Process the state with chatbot and tool integration."""
        
        user_message = state["messages"][-1]
        user_input = user_message.content if hasattr(user_message, 'content') else str(user_message)
        
        # Invoke LLM
        llm_response = self.llm.invoke(state["messages"])
        
        return {"messages": [llm_response]}

    # --- HÀM QUAN TRỌNG ĐỂ DÙNG TRONG LANGGRAPH ---
    def create_chatbot(self, tools):
        """Return a chatbot instance with tool integration.""" 
        

        llm_with_tools = self.llm.bind_tools(tools)

        # 2. Định nghĩa hàm xử lý của Node
        def chatbot_node(state: State):
            """Chatbot logic for processing state with tools."""
            return {"messages": [llm_with_tools.invoke(state["messages"])]}
        
        return chatbot_node