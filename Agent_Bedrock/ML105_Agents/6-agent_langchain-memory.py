import os
import re
from datetime import datetime
from langchain_aws import ChatBedrock
from langchain.tools import tool
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

# Set Parameters
model_id = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"

# Initialize Bedrock LLM
llm = ChatBedrock(
    model_id=model_id,
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

# Define Tools
@tool
def calculate_expression(expression: str) -> str:
    """Calculator: Evaluate a mathematical expression"""
    safe_expr = re.sub(r'[^0-9+\-*/(). ]', '', expression)
    if safe_expr.strip() == "":
        return "I couldn't compute that."
    try:
        result = eval(safe_expr)
        print("🔧 ... ...Tool: calculator")
        return f"The result is: {result}"
    except:
        return "I couldn't compute that."

@tool
def get_weather(location: str) -> str:
    """Weather: Get weather information for a location"""
    weather_data = {
        "new york": "Sunny, 72°F",
        "london": "Cloudy, 58°F",
        "tokyo": "Rainy, 65°F",
        "paris": "Partly cloudy, 68°F"
    }
    location_lower = location.lower()
    for city, weather in weather_data.items():
        if city in location_lower:
            print("🔧 ... ...Tool: get_weather")
            return f"Weather in {city.title()}: {weather}"
    return f"Weather information for {location} is not available in simulation."

@tool
def get_date() -> str:
    """Get Date: Get the current date"""
    now = datetime.now()
    date_str = now.strftime("%A, %B %d, %Y")
    print("🔧 ... ...Tool: get_date")
    return f"Today's date is: {date_str}"

@tool
def get_time() -> str:
    """Get Time: Get the current time"""
    now = datetime.now()
    time_str = now.strftime("%I:%M:%S %p")
    print("🔧 ... ...Tool: get_time")
    return f"The current time is: {time_str}"

# Create agent with tools
tools = [calculate_expression, get_weather, get_date, get_time]
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful personal assistant. I can tell you the current date, time, and weather. I can also calculate mathematical expressions.",
    checkpointer=InMemorySaver()
)

print("Welcome! I'm your personal assistant. I can tell you the current date, time, and weather. I can also calculate mathematical expressions. Type 'quit' to stop.")
while True:
    user_input = input("👤 You: ")
    if user_input.lower() == "quit":
        print("Agent: Goodbye!")
        break
    print("🤖 System call")
    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        {"configurable": {"thread_id": "1"}}
    )
    print("Agent:", response["messages"][-1].content)
