from crewai import Agent
from langchain.tools import tool
import pydantic

@tool("test_tool")
def test_tool(query: str):
    """Test tool description"""
    return "test"

print(f"Pydantic version: {pydantic.__version__}")

try:
    agent = Agent(
        role='Test Role',
        goal='Test Goal',
        backstory='Test Backstory',
        tools=[test_tool],
        verbose=True
    )
    print("Agent created successfully!")
except Exception as e:
    print(f"Error creating agent: {e}")
