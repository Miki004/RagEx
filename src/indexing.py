import os
from dotenv import load_dotenv
from typing import Annotated
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
    messages: Annotated[list, add_messages] #[{}, {}, {}]

class BasicToolNode:
    def __init__(self, tools: list) -> None:
        self.tools = {tool.name : tool for tool in tools}
    
    def __call__(self, node_state: dict):
        #dallo stato del nodo ottenere l'ultimo messaggio
        if message := node_state.get("messages", []):
            message = message[-1]
            print(message)
        else: 
            raise ValueError("Messages not found")
        
        #itero lungo l'ultimo messaggio e iterando sulle varie chiamate 
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools[tool_call["name"]].invoke(tool_call["args"])
            outputs.append(ToolMessage(
                content=tool_result,
                name = tool_call["name"],
                tool_call_id = tool_call["id"]
            ))
        return {"messages": outputs}


def route_tools(state: State):
    if message := state.get("messages", []):
        message_ai = message[-1]
    else:
        raise ValueError("Nessun Messaggio trovato")
    
    if hasattr(message_ai,"tool_calls") and len(message_ai.tool_calls) > 0:
        return "tools"
    else: raise ValueError("Not MessageAI")
    
tool = TavilySearch(max_results=2)
tools = [tool]
tool_node = BasicToolNode(tools=[tool])
llm_with_tools = llm.bind_tools(tools)

def chat_node(state: State) -> dict:
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

graph_builder = StateGraph(State)

graph_builder.add_conditional_edges(
    "chat_node",
    route_tools,
    # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
    # It defaults to the identity function, but if you
    # want to use a node named something else apart from "tools",
    # You can update the value of the dictionary to something else
    # e.g., "tools": "my_tools"
    {"tools": "tools", END: END},
)
# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_node("chat_node",chat_node)
graph_builder.add_node("tools",tool_node)
graph_builder.set_entry_point("chat_node")

app = graph_builder.compile()


while True:
    user_input = input("User: ")
    if user_input in ["exit", "quit", "q"]:
        break
    for state in app.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in state.values():
            print("Assistant:", value["messages"][-1])
