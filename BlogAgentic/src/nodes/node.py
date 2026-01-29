from src.states.blogstate import Blog, BlogState
from langchain_core.messages import HumanMessage, SystemMessage
from src.states.blogstate import Blog

class BlogNode:
    """ A class to represent a blog node. """

    def __init__(self, llm):
        self.llm = llm

    def title_creation(self, state: BlogState) -> dict:
        """Create the title for the blog"""
        
        if "topic" in state and state["topic"]:
            prompt = """You are an expert blog content writer using Markdown formatting. 
            Generate a blog title for the {topic}. The title should be creative and SEO friendly."""
            
            system_message = prompt.format(topic=state["topic"])
            
            response = self.llm.invoke(system_message)

            new_blog = Blog(title=response.content, content="")
            
            return {"blog": new_blog}
        return {}

    def content_generation(self, state: BlogState) -> dict:
        """Generate the content for the blog"""

        if "topic" in state and state["topic"]:
            prompt = """You are an expert blog content writer using Markdown formatting. 
            Generate detailed blog content with a breakdown for the {topic}.""" 
            
            system_message = prompt.format(topic=state["topic"])
            response = self.llm.invoke(system_message)

            # Lấy title từ bước trước
            current_title = state["blog"].title
            
            # Cập nhật object Blog đầy đủ cả title và content
            updated_blog = Blog(title=current_title, content=response.content)

            return {"blog": updated_blog}
        return {}
    
    def translation(self, state: BlogState) -> dict:
        """Translate the content to the specified language"""
        
        current_blog = state["blog"]
        
        # 1. Prompt: Yêu cầu trả về định dạng văn bản dễ tách (Dùng dấu phân cách)
        translate_prompt = """You are a professional translator. 
        Translate the following Blog Title and Content into {current_language}.
        
        IMPORTANT RESPONSE FORMAT:
        1. First line must start with "TITLE:" followed by the translated title.
        2. Then add a separator line "===CONTENT_START==="
        3. Then put the entire translated content below that line.
        
        Do not output JSON. Just plain text with the format above.

        ORIGINAL TITLE:
        {title}
        
        ORIGINAL CONTENT:
        {content}"""
        
        try:
            message = [
                HumanMessage(content=translate_prompt.format(
                    current_language=state["current_language"], 
                    title=current_blog.title, 
                    content=current_blog.content
                ))
            ]
            
            # 2. Bỏ 'with_structured_output', dùng invoke thường
            response = self.llm.invoke(message)
            result_text = response.content

            # 3. Xử lý chuỗi (Parsing thủ công) để lấy Title và Content
            # Tách tiêu đề và nội dung dựa trên dấu phân cách
            if "===CONTENT_START===" in result_text:
                parts = result_text.split("===CONTENT_START===")
                
                # Lấy Title (xóa chữ TITLE: ở đầu nếu có)
                title_part = parts[0].replace("TITLE:", "").strip()
                
                # Lấy Content
                content_part = parts[1].strip()
            else:
                # Fallback: Nếu LLM quên format, coi tất cả là content, giữ nguyên title cũ
                print(f"Warning: Translation format not as expected, using fallback parsing")
                title_part = current_blog.title
                content_part = result_text.strip()

            # 4. Tạo đối tượng Blog
            translated_blog = Blog(title=title_part, content=content_part)
            
            return {"blog": translated_blog}

        except Exception as e:
            # Trường hợp lỗi, trả về blog gốc (English) và log error
            print(f"Error during translation to {state['current_language']}: {e}")
            print(f"Falling back to original English content")
            return {"blog": current_blog}

    def route(self,state:BlogState):
      """A routing node to decide which language translation to use"""
      return {"current_language":state["current_language"]}
    

    def route_decision(self,state:BlogState):
      """Decide which language to translate based on user input"""
      if state["current_language"] == "vietnamese":
        return "vietnamese"
      elif state["current_language"] == "chinese":
        return "chinese"
      else:
         return state["current_language"]  
    def critique_content(self, state: BlogState) -> dict:
        """Critique the blog content and provide feedback"""
        
        current_blog = state["blog"]
        iteration = state.get("iteration_count", 0)
        
        critique_prompt = """You are an expert content critic. Review this blog and provide constructive feedback.

Blog Title: {title}

Blog Content:
{content}

Analyze:
1. Is the content well-structured and clear?
2. Is it engaging and informative?
3. Are there any grammatical or spelling errors?
4. Does it match the topic well?

If the content is GOOD (minor or no issues), start your response with "APPROVED:"
If it NEEDS IMPROVEMENT, start with "NEEDS_WORK:" and list specific issues.

Be concise but specific."""

        message = critique_prompt.format(
            title=current_blog.title,
            content=current_blog.content
        )
        
        response = self.llm.invoke(message)
        critique_text = response.content
        
        # Determine if improvement is needed
        should_improve = critique_text.strip().startswith("NEEDS_WORK:")
        
        # Don't improve if we've already done 2 iterations
        if iteration >= 2:
            should_improve = False
            
        return {
            "critique": critique_text,
            "should_improve": should_improve,
            "iteration_count": iteration
        }
    
    def improve_content(self, state: BlogState) -> dict:
        """Improve the blog content based on critique feedback"""
        
        current_blog = state["blog"]
        critique = state.get("critique", "")
        iteration = state.get("iteration_count", 0)
        
        improve_prompt = """You are an expert content writer. Improve this blog based on the feedback.
                Original Title: {title}
                Original Content:
                {content}
                Feedback:
                {critique}
                Rewrite ONLY THE CONTENT (keep the title same) to address all the issues mentioned. 
                Make it better, clearer, and more engaging. Use Markdown formatting."""

        message = improve_prompt.format(
            title=current_blog.title,
            content=current_blog.content,
            critique=critique
        )
        
        response = self.llm.invoke(message)
        improved_content = response.content
        
        # Create updated blog
        improved_blog = Blog(title=current_blog.title, content=improved_content)
        
        return {
            "blog": improved_blog,
            "iteration_count": iteration + 1
        }
    
    def critique_decision(self, state: BlogState) -> str:
        """Decide whether to improve content or end"""
        if state.get("should_improve", False):
            return "improve"
        else:
            return "end"