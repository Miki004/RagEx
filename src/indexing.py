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
    name : str
    age: str
    skills : list[str]
    final_result: str

def greeting_node(state:State)-> State:
    state["final_result"] = state['name'] + " welcome to the system "
    return state

def user_age(state:State) ->State:
    state["final_result"] += "You are " + state["age"] + " years old "
    return state

def list_skills(state:State) -> State:
    state["final_result"] += " You have skills in "+ " ".join(state["skills"])
    return state

graph_builder = StateGraph(State)
graph_builder.add_node("greeting_node",greeting_node)
graph_builder.add_node("user_age", user_age)
graph_builder.add_node("list_skills",list_skills)

graph_builder.add_edge("greeting_node", "user_age")
graph_builder.add_edge("user_age", "list_skills")

graph_builder.set_entry_point("greeting_node")
graph_builder.set_finish_point("list_skills")

app = graph_builder.compile()

result = app.invoke({"name": "Michele", "age": "21", "skills": ["Deep Learning", "AI", "Machine Learning "]})
print(result["final_result"])

