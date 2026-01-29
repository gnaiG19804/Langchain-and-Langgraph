from typing import TypedDict, Optional
from pydantic import BaseModel, Field


class Blog(BaseModel):
    title:str = Field(..., description="The title of the blog post")
    content:str = Field(..., description="The content of the blog post")

class BlogState(TypedDict):
    topic:str
    blog:Blog
    current_language:str
    critique:Optional[str]  # AI feedback on content quality
    should_improve:Optional[bool]  # Decision to improve or not
    iteration_count:Optional[int]  # Track refinement loops (max 2)