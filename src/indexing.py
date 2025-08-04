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
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    data : List[int]
    name : str
    operation: str

def init_list(state: State) -> State:
    if state["operation"] == "+":
        state["data"] = sum(state["data"])
    elif state["operation"] == "*":
        prod = 1
        for el in state["data"]:
            prod *= el
        state["data"] = prod
    return state

graph_builder = StateGraph(State)
graph_builder.add_node("init_list", init_list)
graph_builder.set_entry_point("init_list")
graph_builder.set_finish_point("init_list")
app = graph_builder.compile()

result = app.invoke({"data":[1,2,4,5,5], "name": "Michele", "operation": "+"})
print(f"Hi {result["name"]}, your answer is: {result["data"]} ")
