import streamlit as st
import os
from src.langgraphagenticai.ui.uiconfigfile import Config

class LoadStreamlitUI:
    def __init__(self):
        self.config = Config()
        self.user_controls = {}

    def load_streamlit_ui(self):
        st.set_page_config(page_title="🤖 " + self.config.get_page_title(), layout="wide")
        st.header("🤖 " + self.config.get_page_title())
        st.session_state.timeframe = ''
        st.session_state.IsFetchNewsClicked = False

        with st.sidebar:
            # Get options from config
            llm_options = self.config.get_llm_options()
            usecase_options = self.config.get_usecase_options()

            # LLM selection
            self.user_controls["selected_llm"] = st.selectbox("Select LLM", llm_options)

            if self.user_controls["selected_llm"] == 'Groq':
                # Model selection
                model_options = self.config.get_groq_model_options()
                self.user_controls["selected_groq_model"] = st.selectbox("Select Model", model_options)
                
                # API Key Input (Dùng tham số key để tự lưu vào session_state)
                self.user_controls["GROQ_API_KEY"] = st.text_input("API Key", type="password", key="GROQ_API_KEY")

                # Validate API key
                if not self.user_controls["GROQ_API_KEY"]:
                    st.warning("⚠️ Please enter your GROQ API key to proceed. Don't have? refer : https://console.groq.com/keys ")
            
            # Usecase selection
            self.user_controls["selected_usecase"] = st.selectbox("Select Usecases", usecase_options)

            if self.user_controls["selected_usecase"] == "Chatbot with Web" or self.user_controls["selected_usecase"] == "AI News":
                # Tavily Key Input
                os.environ["TAVILY_API_KEY"]=self.user_controls["TAVILY_API_KEY"] = st.text_input("Tavily API Key", type="password", key="TAVILY_API_KEY")
                
                if not self.user_controls["TAVILY_API_KEY"]:
                    st.warning("⚠️ Please enter your TAVILY API key to proceed. Don't have? refer : https://tavily.com/ ")
            if self.user_controls["selected_usecase"] == "AI News":
                st.write("### AI News Explorer Options")
                with st.sidebar:
                    time_frame = st.selectbox(
                        "Select time Frame",
                        ["Daily", "Weekly", "Monthly"],
                        index=0
                    )
                if st.button("Fetch Latest AI News", use_container_width=True):
                    st.session_state.IsFetchNewsClicked = True
                    st.session_state.TimeFrame = time_frame


        return self.user_controls