import os
import time
from duckduckgo_search import DDGS
import yfinance as yf
from crewai import Agent, LLM
from crewai.tools import tool
from rag_pipeline import rag_instance

# Initialize LLMs with strict token budgets to avoid Groq's 1000 OTPM limit
# We force the first 3 agents to use the short_llm, saving the budget for the final advisor.
short_llm = LLM(
    model="groq/qwen/qwen3.8-27b",
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=120
)

long_llm = LLM(
    model="groq/qwen/qwen3.8-27b",
    api_key=os.getenv("GROQ_API_KEY"),
    max_tokens=600
)

@tool("internet_search")
def ddg_search_func(query: str) -> str:
    """Searches the internet. Input: search string."""
    time.sleep(15) # Stay under free-tier limits
    with DDGS() as ddgs:
        results = [r for r in ddgs.text(query, max_results=3)]
        # Return snippet and URL for citations
        return "\n".join([f"Title: {r['title']}\nSnippet: {r['body'][:200]}\nSource: {r['href']}\n" for r in results])

# Custom RAG tool for uploaded documents
@tool("search_uploaded_documents")
def search_uploaded_documents_tool(query: str) -> str:
    """Searches through user-uploaded local documents using RAG. Input: a specific query string. Returns content and source citations."""
    time.sleep(5) # Less delay needed for local
    try:
        results = rag_instance.vector_store.similarity_search(query, k=4)
        if not results:
            return "No information found in uploaded documents."
        return "\n\n".join([f"[Source: {os.path.basename(doc.metadata.get('source', 'Unknown Document'))}]\n{doc.page_content}" for doc in results])
    except Exception as e:
        return f"Could not search documents. Error: {str(e)}"

# Automated Document Retrieval (Replaces local RAG)
@tool("fetch_fundamental_data")
def fetch_fundamental_data_func(symbol: str) -> str:
    """Fetches real-time fundamental financial documents (Income Statement & Balance Sheet). Input: a stock ticker symbol like 'NVDA'."""
    time.sleep(15)
    try:
        ticker = yf.Ticker(symbol)
        
        # Get the most recent annual income statement and balance sheet
        income_stmt = ticker.financials
        if not income_stmt.empty:
            latest_income = income_stmt.iloc[:, 0] # Most recent year
            revenue = latest_income.get("Total Revenue", "N/A")
            gross_profit = latest_income.get("Gross Profit", "N/A")
            net_income = latest_income.get("Net Income", "N/A")
        else:
            revenue = gross_profit = net_income = "Data not found"
            
        summary = f"""
        Fundamental Financials for {symbol} (Most Recent Year):
        - Total Revenue: {revenue}
        - Gross Profit: {gross_profit}
        - Net Income: {net_income}
        - Forward PE Ratio: {ticker.info.get('forwardPE', 'N/A')}
        - Market Cap: {ticker.info.get('marketCap', 'N/A')}
        - Debt to Equity: {ticker.info.get('debtToEquity', 'N/A')}
        """
        return summary
    except Exception as e:
        return f"Could not retrieve fundamentals for {symbol}. Error: {str(e)}"

# Custom tool for Quant Strategist
@tool("fetch_historical_data")
def fetch_historical_data_func(symbol: str) -> str:
    """Fetches stock price and company info. Input: a stock ticker symbol like 'NVDA'."""
    time.sleep(15)
    ticker = yf.Ticker(symbol)
    info = ticker.info
    history = ticker.history(period="6mo")
    
    # Calculate 50-day moving average
    if len(history) >= 50:
        history['50MA'] = history['Close'].rolling(window=50).mean()
        current_50ma = history['50MA'].iloc[-1]
    else:
        current_50ma = "N/A"
        
    summary = f"""
    Symbol: {symbol}
    Current Price: {info.get('currentPrice', 'N/A')}
    50-Day Moving Average: {current_50ma}
    Recent History (Last 5 days of 6mo trend):
    {history[['Close', 'Volume']].tail(5).to_string()}
    """
    return summary

class MarketAgents:
    def __init__(self):
        self.search_tool = ddg_search_func
        self.fundamental_tool = fetch_fundamental_data_func
        self.rag_tool = search_uploaded_documents_tool
        self.quant_tool = fetch_historical_data_func

    def market_news_analyst(self):
        return Agent(
            role='Market News Analyst',
            goal='Scour the web for recent events for {company}.',
            backstory="""You are an expert news aggregator. You find info in ONE search.""",
            tools=[self.search_tool],
            verbose=True,
            llm=short_llm,
            max_iter=3 # Limit loops
        )

    def financial_report_researcher(self):
        return Agent(
            role='Financial Report Researcher',
            goal='Detailed analysis of corporate fundamentals and uploaded documents.',
            backstory="""You find factual data in ONE search. You check live API data and user-uploaded documents.""",
            tools=[self.fundamental_tool, self.rag_tool],
            verbose=True,
            llm=short_llm,
            max_iter=3
        )

    def quant_strategist(self):
        return Agent(
            role='Quant Strategist',
            goal='Analyze numerical data patterns.',
            backstory="""You provide numbers in ONE search.""",
            tools=[self.quant_tool],
            verbose=True,
            llm=short_llm,
            max_iter=3
        )

    def investment_advisor(self):
        return Agent(
            role='Investment Advisor',
            goal='Synthesize all inputs into a final, coherent investment strategy.',
            backstory="""You are the ultimate decision-maker. You build a persuasive recommendation.""",
            tools=[],
            verbose=True,
            llm=long_llm
        )
