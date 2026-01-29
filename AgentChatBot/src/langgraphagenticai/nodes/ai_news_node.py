from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate


class AINewsNode:
  def __init__(self,llm):
    """Initialize the AI News Node with the given language model."""

    self.llm = llm
    self.tavily = TavilyClient()

    self.state = {}
  

  def fetch_news(self, state:dict):
    """Fetch the latest AI news based on the specified time frame."""
    frequency = state['messages'][0].content.lower()  # Assuming the time frame is provided in the first message
    self.state['frequency'] = frequency
    time_range_map = { 'daily': 'd', 'weekly': 'w', 'monthly': 'm', 'year':'y'}
    days_map = { 'daily': 1, 'weekly': 7, 'monthly': 30, 'year':366}

    response = self.tavily.search(
       query="Top artificial intelligence technology news Viet Nam and globally",
        topic="news",
        time_range = time_range_map[frequency],
        include_answer = "advanced",
        max_results=20,
        days=days_map[frequency],
      )
    
    state['news_data'] = response.get('results',[])
    self.state['news_data']= state['news_data']
    return state
  
  def summarize_news(self, state:dict)->dict:
    """Summarize the fetched AI news articles."""
    new_items= self.state.get('news_data')
    prompt_template = ChatPromptTemplate.from_messages([
            ("system", """Summarize AI news articles into markdown format. For each item include:
            - Date in **YYYY-MM-DD** format in IST timezone
            - Concise sentences summary from latest news
            - Sort news by date wise (latest first)
            - Source URL as link
            Use format:
            ### [Date]
            - [Summary](URL)"""),
            ("user", "Articles:\n{articles}")
        ])
    articles_str = "\n\n".join([
      f"Content: {item.get('content','')}\nURL: {item.get('url','')} \nDate: {item.get('published_at','')}"
      for item in new_items
    ])

    response = self.llm.invoke(prompt_template.format_messages(articles=articles_str))
    state['summary'] = response.content
    self.state['summary']= state['summary']
    return self.state
  
  def save_result(self, state):
    frequency = self.state['frequency']
    summary = self.state['summary']
    filename = f"./AINews/{frequency}_summary.md"
    with open(filename, "w", encoding="utf-8") as file:
      file.write(f"#{frequency.capitalize()} AI News Summary\n\n")
      file.write(summary)
    self.state["filename"] = filename
    return self.state