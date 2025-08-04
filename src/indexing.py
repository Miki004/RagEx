import os
from dotenv import load_dotenv
from typing import Annotated,List
from typing_extensions import TypedDict
import numpy as np
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
    number : int 
    counter: int  
    won: bool
    player_name : str
    gambling : int


def setup(state:State) -> State:
    state["number"] = np.random.randint(1,20)
    state["counter"] = 0
    state["won"] = False
    return state


def should_continue(state:State) -> State:
    if state["won"]:
        return "end_game"
    if state["counter"] < 7:
        return "retry_gambling"
    else:
        state["won"] = False
        return "end_game"

def suggest_number(state:State) -> State:
    if not state["won"]:
        if state["gambling"] > state["number"]:
            print("Guess something lower!")
        else:
            print("Guess something higher!")
    return state

def guess(state:State) -> State:
    print(f"Gambling attempt: {state["counter"]}\n")
    state["gambling"] = int(input("Guess a number: "))
    state["counter"] += 1
    if state["gambling"] == state["number"]:
        state["won"] = True
    return state

def end_node(state:State) -> State:
    if state["won"]:
        print("You won guessing the " + str(state["number"]))
    else:
        print("You lost the number was " + str(state["number"]))


graph_builder = StateGraph(State)
graph_builder.add_node("setup_node", setup)
graph_builder.add_edge(START, "setup_node")
graph_builder.add_node("guess_node", guess)
graph_builder.add_node("end_node", end_node)
graph_builder.add_node("hint_node", suggest_number)
graph_builder.add_edge("setup_node", "guess_node")
graph_builder.add_edge("guess_node", "hint_node")


graph_builder.add_conditional_edges(
    "hint_node",
    should_continue,
    {
        "retry_gambling": "guess_node",
        "end_game": "end_node"
    }
)
graph_builder.add_edge("end_node", END)

app = graph_builder.compile()
# from PIL import Image
# import io

# img_bytes = app.get_graph().draw_mermaid_png()
# image = Image.open(io.BytesIO(img_bytes))
# image.show() 
app.invoke({"player_name": "Michele "})