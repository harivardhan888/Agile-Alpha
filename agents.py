import os
import time
from duckduckgo_search import DDGS
import yfinance as yf
from crewai import Agent, LLM
from crewai.tools import tool
from rag_pipeline import rag_instance

# Initialize Groq LLM using CrewAI's native LLM wrapper
groq_llm = LLM(
    model="groq/llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

@tool("internet_search")
def ddg_search_func(query: str) -> str:
    """Searches the internet. Input: search string."""
    time.sleep(15) # Stay under free-tier limits
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=3)]
        # Return only a small portion of the snippet to save tokens
        return "\n".join([f"T: {r['title']}\nS: {r['body'][:200]}\n" for r in results])

# Custom RAG tool
@tool("search_financial_reports")
def search_financial_reports_tool(query: str) -> str:
    """Searches through local financial documents using RAG. Input: a specific query string."""
    time.sleep(15)
    results = rag_instance.vector_store.similarity_search(query, k=4)
    return "\n\n".join([doc.page_content for doc in results])

# Custom tool for Quant Strategist
@tool("fetch_historical_data")
def fetch_historical_data_func(symbol: str) -> str:
    """Fetches stock price and company info. Input: a stock ticker symbol like 'NVDA'."""
    time.sleep(15)
    ticker = yf.Ticker(symbol)
    info = ticker.info
    history = ticker.history(period="1mo")
    
    summary = f"""
    Symbol: {symbol}
    Current Price: {info.get('currentPrice', 'N/A')}
    Recent History (1 month):
    {history.tail(5).to_string()}
    """
    return summary

class MarketAgents:
    def __init__(self):
        self.search_tool = ddg_search_func
        self.rag_tool = search_financial_reports_tool
        self.quant_tool = fetch_historical_data_func

    def market_news_analyst(self):
        return Agent(
            role='Market News Analyst',
            goal='Scour the web for recent events for {company}.',
            backstory="""You are an expert news aggregator. You find info in ONE search.""",
            tools=[self.search_tool],
            verbose=True,
            llm=groq_llm,
            max_iter=3 # Limit loops
        )

    def financial_report_researcher(self):
        return Agent(
            role='Financial Report Researcher',
            goal='Detailed analysis of corporate transcripts.',
            backstory="""You find factual data in ONE search.""",
            tools=[self.rag_tool],
            verbose=True,
            llm=groq_llm,
            max_iter=3
        )

    def quant_strategist(self):
        return Agent(
            role='Quant Strategist',
            goal='Analyze numerical data patterns.',
            backstory="""You provide numbers in ONE search.""",
            tools=[self.quant_tool],
            verbose=True,
            llm=groq_llm,
            max_iter=3
        )

    def investment_advisor(self):
        return Agent(
            role='Investment Advisor',
            goal='Synthesize all inputs into a final, coherent investment strategy.',
            backstory="""You are the ultimate decision-maker. You build a persuasive recommendation.""",
            tools=[],
            verbose=True,
            llm=groq_llm
        )
