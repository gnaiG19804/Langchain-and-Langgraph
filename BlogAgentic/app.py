import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from src.nodes.node import BlogNode
from src.graphs.graph_builder import GraphBuilder
from src.llms.groqllm import GroqLLM

import os
from dotenv import load_dotenv
load_dotenv()



app=FastAPI()

os.environ["LANGCHAIN_API_KEY"]= os.getenv("LANGCHAIN_API_KEY")

# Supported languages
SUPPORTED_LANGUAGES = ["vietnamese", "chinese"]

# Initialize LLM once at startup
groq_llm_obj = GroqLLM()
llm = groq_llm_obj.get_llm()



@app.post("/blogs")
async def create_blog(request: Request):
  try:
    data = await request.json()
    topic = data.get("topic", "").strip()
    language = data.get("language", "").strip().lower()

    # Validation
    if not topic:
      raise HTTPException(status_code=400, detail="Topic is required and cannot be empty")
    
    if len(topic) < 3:
      raise HTTPException(status_code=400, detail="Topic must be at least 3 characters long")
    
    if language and language not in SUPPORTED_LANGUAGES:
      raise HTTPException(
        status_code=400, 
        detail=f"Language '{language}' is not supported. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
      )

    # Build and invoke graph
    graph_builder = GraphBuilder(llm)
    if language and topic:
      graph = graph_builder.setup_graph(usecase="language")
      state = graph.invoke({"topic": topic, "current_language": language})
    else:
      # Use critique graph by default for better quality
      graph = graph_builder.setup_graph(usecase="critique")
      state = graph.invoke({"topic": topic, "iteration_count": 0})
    
    # Format response
    blog = state.get("blog")
    if blog:
      return {
        "success": True,
        "blog": {
          "title": blog.title,
          "content": blog.content
        },
        "metadata": {
          "topic": topic,
          "language": language if language else "english"
        }
      }
    else:
      raise HTTPException(status_code=500, detail="Failed to generate blog content")
      
  except HTTPException:
    raise
  except Exception as e:
    return JSONResponse(
      status_code=500,
      content={
        "success": False,
        "error": "Internal server error occurred while generating blog",
        "detail": str(e)
      }
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)