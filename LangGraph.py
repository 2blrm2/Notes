from langgraph.graph import StateGraph, START, END, MessagesState
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages

from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.messages.utils import trim_messages,count_tokens_approximately
from langchain.messages import RemoveMessage


class JokeState(TypedDict):
    topic: str
    joke: str
    explanation: str


# state
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# Make tool list
tools = [get_stock_price, search_tool, calculator]

llm_with_tools = llm.bind_tools(tools)


# graph nodes
def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

#            OR 
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": [response]}


tool_node = ToolNode(tools)  # Executes tool calls

# graph structure
graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)


graph.add_edge(START, "chat_node")
graph.add_conditional_edges(
    "chat_node", tools_condition
)  # If the LLM asked for a tool, go to ToolNode; else finish
graph.add_edge("tools", "chat_node")

## BM: No need to add end node.


chatbot = graph.compile()

# Regular chat
out = chatbot.invoke({"messages": [HumanMessage(content="What is 2*3?")]})
print(out["messages"][-1].content)  ## The result of 2 multiplied by 3 is 6.

chatbot.invoke({"messages": [{"role": "user", "content": "Hi! My name is Balram."}]})


#################################################################################################################
#################################################################################################################
#################################################################################################################

graph = StateGraph(JokeState)

graph.add_node("generate_joke", generate_joke)
graph.add_node("generate_explanation", generate_explanation)

graph.add_edge(START, "generate_joke")
graph.add_edge("generate_joke", "generate_explanation")
graph.add_edge("generate_explanation", END)

checkpointer = InMemorySaver()

workflow = graph.compile(checkpointer=checkpointer)


config1 = {"configurable": {"thread_id": "1"}}
workflow.invoke({"topic": "pizza"}, config=config1)

workflow.get_state(config1)

list(workflow.get_state_history(config1))


################################ Running PostGrace with docker

## Create  docker-compose.yml

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: postgres
    ports:
      - "5442:5432"


##  docker compose up -d 
##  docker ps

!pip install -U \
  langgraph-checkpoint-postgres \
  psycopg[binary,pool] 

##
DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres"

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    # Run ONCE (creates tables)
    checkpointer.setup()

    graph = builder.compile(checkpointer=checkpointer)

    t1 = {"configurable": {"thread_id": "thread-1"}}
    out1 = graph.invoke({"messages": [{"role": "user", "content": "What is my name?"}]}, t1)
    print("Thread-1:", out1["messages"][-1].content)

#################################################################


################## Trimmig ##################################

def call_model(state: MessagesState):
    
    MAX_TOKENS = 150
    # Trim conversation history -> last N messages that fit within the token budget
    messages = trim_messages(
        state["messages"],
        strategy="last",                      
        token_counter=count_tokens_approximately,
        max_tokens=MAX_TOKENS
    )

    print('Current Token Count ->', count_tokens_approximately(messages=messages))

    for message in messages:
        print(message.content)

    response = model.invoke(messages)

    return {"messages": [response]}


builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_edge(START, "call_model")


checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "chat-1"}}
result = graph.invoke(
    {"messages": [{"role": "user", "content": "Hi, my name is Nitish."}]},
    config)

result["messages"][-1].content

######################################################################################################################################################################################



############ Deletion #############################

def delete_old_messages_node(state: MessagesState):
    msgs = state["messages"]

    # if more than 10 messages, delete the earliest 6
    if len(msgs) > 10:
        to_remove = msgs[:6]
        return {"messages": [RemoveMessage(id=m.id) for m in to_remove]}

    return {}


############################ Summerization + Deletion ###################################


class ChatState(MessagesState):
    summary: str

def summarize_and_delete_conversation(state: ChatState):

    existing_summary = state["summary"]

    # Build summarization prompt
    if existing_summary:
        prompt = (
            f"Existing summary:\n{existing_summary}\n\n"
            "Extend the summary using the new conversation above."
        )
    else:
        prompt = "Summarize the conversation above."

    messages_for_summary = state["messages"] + [
        HumanMessage(content=prompt)
    ]

    response = model.invoke(messages_for_summary)

    # Keep only last 2 messages verbatim
    messages_to_delete = state["messages"][:-2]

    return {
        "summary": response.content,
        "messages": [RemoveMessage(id=m.id) for m in messages_to_delete],
    }


def chat_node(state: ChatState):
    updatd_messages = []

    if state["summary"]:
        updatd_messages.append({
            "role": "system",
            "content": f"Conversation summary:\n{state['summary']}"
        })

    updatd_messages.extend(state["messages"])

    print(updatd_messages)

    response = model.invoke(updatd_messages)
    return {"messages": [response]}

def should_summarize(state: ChatState):
    return len(state["messages"]) > 6


builder = StateGraph(ChatState)
builder.add_node("chat", chat_node)
builder.add_node("summarize", summarize_conversation)

builder.add_edge(START, "chat")

builder.add_conditional_edges(
    "chat",
    should_summarize,
    {
        True: "summarize",
        False: "__end__",
    }
)

builder.add_edge("summarize", "__end__")

checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)


config = {"configurable": {"thread_id": "t1"}}
out = graph.invoke({"messages": [HumanMessage(content=text)], "summary": ""}, config=config)



