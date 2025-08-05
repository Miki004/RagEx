import os
from dotenv import load_dotenv
from typing import Annotated,List, Union, Sequence
from typing_extensions import TypedDict
import numpy as np
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, BaseMessage
from langchain_tavily import TavilySearch
import json
from langchain_core.messages import ToolMessage


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


class State(TypedDict):
    '''Definizione di uno stato del grafo'''
    name : str
    messages : Annotated[Sequence[BaseMessage], add_messages]

llm = init_chat_model("gpt-4o")

def set_name(state: State) -> State:
    user_input = input("Inserisci il nome: ")
    system_prompt = SystemMessage(content=f"Controlla se questo {user_input} è valido come nome. Rispondi solamente 'valid' o 'not_valid' ")
    response = llm.invoke([system_prompt])
    return {"messages": response}


def should_continue(state:State) -> State:
    messages = state["messages"]
    last_messages = messages
    if last_messages == "valid":
        return END
    if last_messages != "valid":
        return "loop"

grap = StateGraph(State)

grap.add_node("set_name", set_name)
grap.add_edge(START, "set_name")

grap.add_conditional_edges(
    "set_name",
    should_continue,
    {
        "continue" : END,
        "loop": "set_name"
    }
)

app = grap.compile()


app.invoke({"messages": []})


