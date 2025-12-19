from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from crewai import Crew, Process
from agents import MarketAgents
from tasks import MarketTasks

class AgentState(TypedDict):
    company: str
    symbol: str
    news_report: str
    financial_report: str
    quant_report: str
    final_strategy: str
    iterations: int

class ResearchWorkflow:
    def __init__(self, company, symbol):
        self.company = company
        self.symbol = symbol
        self.agents = MarketAgents()
        self.tasks = MarketTasks()

    def run_crew(self, state: AgentState):
        """Node to execute the CrewAI research."""
        print(f"--- Executing CrewAI Research for {state['company']} ---")
        
        analyst = self.agents.market_news_analyst()
        researcher = self.agents.financial_report_researcher()
        strategist = self.agents.quant_strategist()
        advisor = self.agents.investment_advisor()

        task1 = self.tasks.news_analysis_task(analyst, state['company'])
        task2 = self.tasks.financial_research_task(researcher, state['company'])
        task3 = self.tasks.quantitative_analysis_task(strategist, state['symbol'])
        task4 = self.tasks.investment_strategy_task(advisor, state['company'])

        crew = Crew(
            agents=[analyst, researcher, strategist, advisor],
            tasks=[task1, task2, task3, task4],
            process=Process.sequential,
            verbose=True,
            max_rpm=1 # Extreme caution for free tier
        )

        result = crew.kickoff()
        
        # Updating state
        state["final_strategy"] = str(result)
        state["iterations"] += 1
        return state

    def check_quality(self, state: AgentState):
        """Decision node to check if the report is sufficient."""
        # Simple logic: if 'Pending' or empty, we need refinement. 
        # In a real scenario, this would involve an LLM check.
        if "Insufficient data" in state["final_strategy"] and state["iterations"] < 2:
            return "refine"
        return "complete"

    def build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("research", self.run_crew)

        workflow.set_entry_point("research")
        
        workflow.add_conditional_edges(
            "research",
            self.check_quality,
            {
                "refine": "research",
                "complete": END
            }
        )

        return workflow.compile()
