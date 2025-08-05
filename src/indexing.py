import os
from dotenv import load_dotenv
from typing import Annotated,List, Union
from typing_extensions import TypedDict
import numpy as np
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage
from langchain_tavily import TavilySearch
import json
from langchain_core.messages import ToolMessage


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


class State(TypedDict):
    messages: List[Union[HumanMessage,AIMessage]]

llm = init_chat_model("openai:gpt-4.1")

def get_response(state:State) -> State:
    response = llm.invoke(state["messages"])
    state["messages"].append(AIMessage(content=response.content))
    print("AI: " + response.content)

graph_builder = StateGraph(State)
graph_builder.add_node("init_node", get_response)
graph_builder.add_edge(START, "init_node")
graph_builder.add_edge("init_node", END)

app = graph_builder.compile()
conversation_history = []
while True:
    user_input = input("User: ")
    conversation_history.append(HumanMessage(content=user_input))
    if user_input in ["exit", "quit", "q"]:
        break
    app.invoke({"messages": conversation_history})