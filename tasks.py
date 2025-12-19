from crewai import Task

class MarketTasks:
    def news_analysis_task(self, agent, company):
        return Task(
            description=f"""Find the 3 most important recent news items for {company} and their sentiment. 
            Be extremely concise, focusing only on high-impact financial events from the last 7 days.""",
            expected_output="A bulleted list of 3 major events with sentiment.",
            agent=agent
        )

    def financial_research_task(self, agent, company):
        return Task(
            description=f"""Extract only the following for {company}: 
            1. Total Revenue (latest Q)
            2. EBITDA
            3. Future Guidance
            Use RAG to find these specific numbers. Be very brief.""",
            expected_output="Key financial table (3 lines).",
            agent=agent
        )

    def quantitative_analysis_task(self, agent, company_symbol):
        return Task(
            description=f"""Calculate {company_symbol}'s 1-month price change and list the latest price target.""",
            expected_output="1-month trend and analyst target.",
            agent=agent
        )

    def investment_strategy_task(self, agent, company):
        return Task(
            description=f"""Based on the news sentiment, financial health, and quantitative trends, 
            provide a comprehensive investment recommendation for {company}. 
            Should the client Buy, Hold, or Sell? Justify your answer with data from the previous tasks.""",
            expected_output="A final investment thesis report (approx. 500 words) with a clear Buy/Hold/Sell recommendation.",
            agent=agent
        )
