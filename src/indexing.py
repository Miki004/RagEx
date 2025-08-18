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

document_content = ""
class State(TypedDict):
    '''Definizione di uno stato del grafo'''
    messages : Annotated[Sequence[BaseMessage], add_messages]


@tool 
def update(content: str) -> str:
    ''' Aggiorna il documento con il content passato'''
    global document_content 
    document_content = content
    return f"Your document has been updated! The current content is: \n {document_content}"

@tool
def save(filename:str) -> str:
    ''' Save the current document to a text file
    Args: filename: name of the file'''
    global document_content

    if not filename.endswith('.txt'):
        filename = f"{filename}.txt"
    try:
        with open(filename, "w") as file:
            file.write(document_content)
        print(f"The document has been saved to {filename}")
        return f"The document has been saved successfully to {filename}"
    except Exception as e: 
        return f"Error during the saving: {str(e)}"
    
tools = [save, update]

model = init_chat_model(model="gpt-4o").bind_tools(tools)

def our_agent(state:State) -> State:
    system_prompt= SystemMessage(f"""You are a Drafter, a helpful assistant. You are going to save and update documents
    
    -If the user wants to update or modify a document, you need to use the 'update' tool.
    -If the user wants to save and finish, use the 'save' tool.
    -Make sure to always show the current document state after modification
                                 
    The current document content is: {document_content} """)

    #introduction messeges 
    if not state["messages"]:
        user_input = "I'm ready to help you update a document. What would you like to create?"
        user_message = HumanMessage(content=user_input)

    else: 
        user_input = input("\nWhat would you like to do with the document? ")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + list(state["messages"]) + [user_message]
    response = model.invoke(all_messages)

    print(f"Ai: {response.content}")
    if hasattr(response,"tool_calls"):
        print(f"USING TOOLS: {[tc["name"] for tc in response.tool_calls]}")
    
    return {"messages": list(state["messages"]) + [user_message, response]}

def should_continue(state:State) -> State:
    ''' Determina se continua o finire la conversazione'''
    messages = state["messages"]
    if not messages:
        return "continue"
    
    #se utilizza il tool 'save' finisci la conversazione
    last_message = messages[-1]
    if isinstance(last_message, ToolMessage):
        if last_message in ["save"]:
            return "end"
        
    # se devi ancora modificare torna all'agente
    return "continue"

def print_messages(messages):
    ''' Funzione che stampa in formato leggibile'''
    if not messages:
        return
    for message in messages[-3:]:
        if isinstance(message, ToolMessage):
            print(f"Tool result: {message.content}")

graph = StateGraph(State)

graph.add_node("agent", our_agent)
graph.add_node("tools",ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_edge("agent", "tools")
graph.add_conditional_edges(
    "tools",
    should_continue,
    {
        "continue": "agent",
        "end": END,
    }
)

app = graph.compile()

def run_document_agent():
    print("\n ===== DRAFTER =====")
    state = {"messages": []}
    for step in app.stream(state, stream_mode="values"):
        if "messages" in step:
            print_messages(step["messages"])
    
    print("\n ==== DRAFTER FINISHED")

if __name__ == "__main__":
    run_document_agent()