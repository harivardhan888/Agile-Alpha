from crewai import Task

class MarketTasks:
    def news_analysis_task(self, agent, company):
        return Task(
            description=f"""Find the 3 most important recent news items for {company} and their sentiment. 
            Be extremely concise, focusing only on high-impact financial events from the last 7 days.""",
            expected_output="A bulleted list of 3 major events with sentiment.",
            agent=agent
        )

    def financial_research_task(self, agent, company_symbol):
        return Task(
            description=f"""Use the fundamental data tool to fetch the latest income statement for {company_symbol}. 
            ALSO use the 'search_uploaded_documents' tool to search for {company_symbol} in any user-uploaded files.
            Extract: 
            1. Total Revenue
            2. Net Income
            3. Any critical insights found in the uploaded documents.
            Format this clearly for the advisor.""",
            expected_output="Key financial table and document insights (if any).",
            agent=agent
        )

    def quantitative_analysis_task(self, agent, company_symbol):
        return Task(
            description=f"""Calculate {company_symbol}'s 6-month price trend, 50-day moving average, and list the latest price target.""",
            expected_output="6-month trend, moving average, and analyst target.",
            agent=agent
        )

    def investment_strategy_task(self, agent, company):
        return Task(
            description=f"""Based on the news sentiment, financial health, and quantitative trends, 
            provide a concise investment recommendation for {company}. 
            
            STRICT FORMATTING REQUIRED. You MUST start your entire response with exactly one of these phrases at the very top:
            **Investment Advice: BUY**
            **Investment Advice: SELL**
            **Investment Advice: HOLD**
            
            Then, provide a brief, punchy analysis using ONLY these 3 Markdown headers:
            # Executive Summary
            # Fundamental Analysis
            # Technical & Sentiment Analysis
            
            Keep your paragraphs very short and punchy. You must finish your thought within 400 words.""",
            expected_output="A concise professional thesis starting with the Investment Advice and matching the exact 3 headers requested.",
            agent=agent
        )
