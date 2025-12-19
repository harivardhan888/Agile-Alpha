from graph_workflow import ResearchWorkflow
from dotenv import load_dotenv
import os

load_dotenv()

def main():
    print("Welcome to Agile Alpha: AI-Driven Market Intelligence Crew")
    company = os.getenv("RESEARCH_COMPANY")
    symbol = os.getenv("RESEARCH_SYMBOL")
    
    if not company:
        company = input("Enter the company name to research (e.g., Nvidia): ")
    if not symbol:
        symbol = input("Enter its stock symbol (e.g., NVDA): ")

    workflow_manager = ResearchWorkflow(company, symbol)
    app = workflow_manager.build_graph()

    initial_state = {
        "company": company,
        "symbol": symbol,
        "news_report": "",
        "financial_report": "",
        "quant_report": "",
        "final_strategy": "",
        "iterations": 0
    }

    try:
        final_state = app.invoke(initial_state)

        print("\n" + "="*50)
        print(f"FINAL INVESTMENT STRATEGY FOR {company} ({symbol})")
        print("="*50)
        print(final_state["final_strategy"])
        
        # Save to file
        with open("final_report.txt", "w", encoding="utf-8") as f:
            f.write(f"INVESTMENT STRATEGY FOR {company} ({symbol})\n")
            f.write("="*50 + "\n")
            f.write(final_state["final_strategy"])
        print(f"\nReport saved to final_report.txt")
    except Exception as e:
        print(f"\nCRITICAL ERROR during workflow execution: {e}")
        with open("error_log.txt", "w") as f:
            import traceback
            f.write(traceback.format_exc())
        print("Error details saved to error_log.txt")

if __name__ == "__main__":
    main()
