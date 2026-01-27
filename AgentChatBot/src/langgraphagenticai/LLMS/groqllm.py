import os 
import streamlit as st
from langchain_groq import ChatGroq


class GroqLLM:
    def __init__(self,user_controls_input):
        self.user_controls_input = user_controls_input

    def get_llm_model(self):
        try:
            groq_api_key = self.user_controls_input.get("GROQ_API_KEY")
            selected_model = self.user_controls_input.get("selected_groq_model")

            if not groq_api_key:
                st.error("❌ GROQ API key is missing. Please provide a valid API key.")
            
            llm =ChatGroq(api_key=groq_api_key, model=selected_model)

        except Exception as e:
            raise RuntimeError(f"❌ Error initializing GROQ LLM: {str(e)}")
        return llm
    