import streamlit as st
from src.langgraphagenticai.ui.streamliui.loadui import LoadStreamlitUI
from src.langgraphagenticai.LLMS.groqllm import GroqLLM
from src.langgraphagenticai.graph.graph_builder import GraphBuilder
from src.langgraphagenticai.ui.streamliui.display_result import DisplayResultStreamlit


def load_langgraph_agentai_app():
    UI=LoadStreamlitUI()
    user_inputs=UI.load_streamlit_ui()

    if not user_inputs:
        st.error("Error loading UI components.")
        return 
    
    user_messages = st.chat_input("Enter your message here...")

    if user_messages:
        try:
            obj_llm_config = GroqLLM(user_controls_input = user_inputs)
            model = obj_llm_config.get_llm_model()

            if not model:
                st.error("Error initializing the LLM model.")
                return
            
            usecase= user_inputs.get("selected_usecase")

            if not usecase:
                st.error("Please select a use case.")
                return
            
            graph_builder = GraphBuilder(model=model)
            try:
                graph = graph_builder.setup_graph(usecase=usecase)
                DisplayResultStreamlit(usecase, graph, user_messages).display_result_on_ui()
            except Exception as e:
                st.error(f"Error setting up the graph: {e}")
                return
        except Exception as e:
            st.error(f"An error occurred: {e}")
            return