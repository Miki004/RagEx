import os
from dotenv import load_dotenv
from typing import Annotated,List
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from langchain_tavily import TavilySearch
import json
from langchain_core.messages import ToolMessage


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
tavly_key = os.getenv("TAVILY_API_KEY")
llm = init_chat_model("openai:gpt-4.1")

class State(TypedDict):
    numeber1 : int
    numeber2 : int 
    operation: str
    numeber3 : int
    intermediate_number: int
    final_number : int
    operation2 : str

def move_by_operation(state: State) -> State:
    if state["operation"] == "+":
        return "add_numbers"
    elif state["operation"]== "-":
        return "subtract_numbers"
    
def move_by_operation2(state: State) -> State:
    if state["operation2"] == "+":
        return "add_numbers"
    elif state["operation2"]== "-":
        return "subtract_numbers"        

def add(state:State) -> State:
    state["numeber3"] = state["numeber1"] + state["numeber2"]
    return state

def subtract(state: State) -> State:
    state["numeber3"] = state["numeber1"] - state["numeber2"]
    return state


def add2(state:State) -> State:
    state["final_number"] = state["numeber3"] + state["intermediate_number"]
    return state

def subtract2(state: State) -> State:
    state["final_number"] = state["numeber3"] - state["intermediate_number"]
    return state

graph_builder = StateGraph(State)
graph_builder.add_node("add_node", add)
graph_builder.add_node("subtract_node", subtract)

graph_builder.add_node("add_node2", add2)
graph_builder.add_node("subtract_node2", subtract2)

graph_builder.add_node("router", lambda state:state) # stiamo dicendo che l'input state sarà l'output state
graph_builder.add_node("router2", lambda state:state)
graph_builder.add_edge(START, "router") # il nodo router è qualcosa che non viene definito esplicitamente

graph_builder.add_conditional_edges(
    "router",
    move_by_operation,
    {
        "add_numbers": "add_node",
        "subtract_numbers": "subtract_node"

    }
)
graph_builder.add_edge("add_node", "router2")
graph_builder.add_edge("subtract_node", "router2")

graph_builder.add_conditional_edges(
    "router2",
    move_by_operation2,
    {
        "add_numbers": "add_node2",
        "subtract_numbers": "subtract_node2"

    }
)
graph_builder.add_edge("add_node2", END)
graph_builder.add_edge("subtract_node2",END)

app = graph_builder.compile()
result = app.invoke({"numeber1": 5, "numeber2": 3, "operation": "+", "intermediate_number": 2, "operation2": "-"})
print(result)