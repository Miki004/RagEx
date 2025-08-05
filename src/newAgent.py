from typing import TypedDict, List
from langgraph.graph import StateGraph 
import math

class AgentState(TypedDict):
    name: str 
    values: List[int]
    operation: str
    result: str 

def process_values(state: AgentState) -> AgentState:
    """This function handles multiple different inputs"""
    if state["operation"] == "+":
        state["result"] = f"Hi {state['name']}, your answer is: {sum(state['values'])}"
    elif state["operation"] == "*":
        state["result"] = f"Hi {state['name']}, your answer is: {math.prod(state['values'])}"
    else:
        state["result"] = "Invalid!"

    return state

graph = StateGraph(AgentState)

graph.add_node("processor", process_values)
graph.set_entry_point("processor") 
graph.set_finish_point("processor") 

app = graph.compile() 

answers = app.invoke({"name": "Jack Sparrow","values": [1,2,3,4] , "operation": "*"})
print(answers["result"])