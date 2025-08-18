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
from interface import chat_tutorial

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


class State(TypedDict):
    '''Definizione di uno stato del grafo'''
    role : HumanMessage
    context : HumanMessage
    task: HumanMessage
    messages : Annotated[Sequence[BaseMessage], add_messages]

llm = init_chat_model("gpt-4o")

def process_input(message: HumanMessage) -> str:
    system_prompt = SystemMessage(content=f"""
Sei un controllore di input. Ti verranno forniti diversi input, uno alla volta. Ogni input può rappresentare:
- un NOME (di un agente virtuale o personaggio),
- un RUOLO (ad es. 'consulente finanziario', 'psicologo', 'insegnante di matematica'),
- un CONTESTO (una descrizione della situazione in cui il ruolo opera),
- un COMPITO (la funzione o richiesta specifica da eseguire),
- un FORMATO DI OUTPUT (ad es. 'JSON', 'testo', 'tabella').

Il tuo compito è rispondere **solo** con:
- `valid` se l'input è coerente ed è comprensibile e adeguato;
- `not_valid` se l'input è scorretto, generico, fuori contesto, o composto solo da numeri o simboli.


Valuta il seguente messaggio: `{message.content}`

Esempi:
- Se l'input è **solo numerico** (es. "123456"), rispondi `not_valid`.
- Se il tipo è `NOME`, deve sembrare un nome proprio valido (es. "Luna", "MarcoBot"), non sigle o numeri.
- Se il tipo è `RUOLO`, deve rappresentare una professione o una funzione riconoscibile.
- Se il tipo è `CONTESTO`, deve essere una frase o paragrafo che descrive una situazione realistica.
- Se il tipo è `COMPITO`, deve essere un'azione concreta da svolgere (es. "aiutami a scrivere un curriculum").
- Se il tipo è `FORMATO DI OUTPUT`, deve essere un tipo di formato valido come "JSON", "markdown", "tabella", "testo", ecc.

Dai il tuo giudizio solo in base al tipo fornito.
Rispondi esclusivamente con `valid` o `not_valid`.
""")
    response = llm.invoke([system_prompt])
    return response.content

def get_role(state: State) -> State:
    ''' Funzione che imposta il ruolo che deve assumere il chatbot'''
    messages = state["messages"][-1]
    if isinstance(messages, AIMessage):
        last_messages= messages.content
    else:
        last_messages = messages[0].content
    if last_messages == "valid":

        user_input = input("Inserisci il ruolo che vuoi assegnare a Robbi: ")
        user_message = HumanMessage(content=user_input)

    else: 
        user_input = input("Riprova, forniscimi un ruolo corretto: ")
        user_message = HumanMessage(content=user_input)
    
    system_prompt = SystemMessage(content=f"""
    Sei un controllore di input. Devi valutare se il seguente testo rappresenta un **ruolo valido**, ovvero una **professione** o una **funzione** chiaramente identificabile.

    - **Input da valutare:** {user_message}

    ### Criteri di validità:
    - Il ruolo deve corrispondere a una figura professionale o funzionale reale e riconoscibile (es. "medico", "insegnante", "copywriter", "consulente finanziario").
    - Non sono validi: nomi generici, stringhe prive di significato, descrizioni troppo vaghe, numeri, caratteri casuali o input non correlati a un ruolo lavorativo.
    - L'input deve essere semanticamente coerente, non vuoto, e non deve contenere solo numeri o simboli.

    ### Esempi validi:
    - "psicologo"
    - "insegnante di matematica"
    - "consulente finanziario"
    - "sviluppatore backend"
    - "assistente amministrativo"

    ### Esempi non validi:
    - "123456"
    - "persona"
    - "!!!@@@"
    - "x1yz"
    - ""

    ### Istruzioni finali:
    - Rispondi **esclusivamente** con: `valid` oppure `not_valid`
    - Non fornire spiegazioni o testo aggiuntivo

    Valuta ora.
    """)

    
    response = llm.invoke([system_prompt])
    return {"messages": [response], "role":user_message}

def get_context(state: State) -> State:
    ''' Funzione che imposta il contesto'''
    messages = state["messages"][-1]
    if isinstance(messages, AIMessage):
        last_messages= messages.content
    else:
        last_messages = messages[0].content
    if last_messages == "valid":

        user_input = input("Dai un contesto a Robbi: ")
        user_message = HumanMessage(content=user_input)

    else: 
        user_input = input("Riprova, forniscimi un contesto coerente: ")
        user_message = HumanMessage(content=user_input)
    
    system_prompt = SystemMessage(content=f"""
        Sei un controllore di input. Devi verificare se il seguente contesto è coerente con il ruolo specificato.

        - **Ruolo:** {state['role']}
        - **Contesto da valutare:** {user_message}

        ### Criteri di validità:
        - Il contesto deve essere **compatibile con il ruolo**, cioè appartenere allo stesso ambito operativo o professionale.
        - Il contesto deve essere **realistico**, **semantico**, e **non generico**.
        - Se il contesto è incoerente, troppo vago, o non ha alcuna connessione logica con il ruolo, è da considerarsi non valido.

        ### Esempi di combinazioni valide:
        - Ruolo: Operaio | Contesto: Fabbrica di automobili
        - Ruolo: Psicologo | Contesto: Studio medico o ospedale
        - Ruolo: Insegnante di matematica | Contesto: Scuola superiore o università
        - Ruolo: Chef | Contesto: Ristorante professionale

        ### Output richiesto:
        - Rispondi **solo** con: `valid` oppure `not_valid`
        - Non fornire spiegazioni o commenti aggiuntivi

        Valuta ora la coerenza tra ruolo e contesto.
        """)

    
    response = llm.invoke([system_prompt])
    return {"messages": [response], "context":user_message}

def get_task(state: State) -> State:
    ''' Funzione che imposta il compito '''
    messages = state["messages"][-1]
    if isinstance(messages, AIMessage):
        last_messages= messages.content
    else:
        last_messages = messages[0].content
    if last_messages == "valid":

        user_input = input("Dai un compito a Robbi: ")
        user_message = HumanMessage(content=user_input)

    else: 
        user_input = input("Riprova, forniscimi un compito adeguato: ")
        user_message = HumanMessage(content=user_input)
    
    system_prompt = SystemMessage(content=f"""
        Sei un controllore di input. Devi verificare se il seguente compito è semanticamente coerente con il ruolo e il contesto forniti.

        - **Ruolo:** {state["role"]}
        - **Contesto:** {state["context"]}
        - **Compito da valutare:** {user_message}

        Il tuo compito è determinare se il compito è realistico, sensato e coerente rispetto al ruolo e al contesto specificati.

        ### Esempi di combinazioni valide:
        - Ruolo: Operaio | Contesto: Fabbrica | Compito: "controllare la linea di produzione"
        - Ruolo: Psicologo | Contesto: Studio medico | Compito: "fornire supporto psicologico ai pazienti"
        - Ruolo: Insegnante di matematica | Contesto: Scuola | Compito: "spiegare le equazioni di secondo grado"

        ### Criteri di validità:
        - Se il compito **non ha senso** rispetto al ruolo o al contesto, rispondi `not_valid`.
        - Se il compito è **coerente** con entrambi, rispondi `valid`.
        - Non aggiungere spiegazioni o commenti.
        - Rispondi **esclusivamente** con: `valid` oppure `not_valid`.

        Valuta ora.""")

    
    response = llm.invoke([system_prompt])
    return {"messages": [response], "task": user_message}

def get_name(state: State) -> State:
    ''' Funzione che imposta il nome del giocatore, se l'input è valido o meno'''
    if not state["messages"]:
        user_input = input("Inserisci il tuo nome: ")
        user_message = HumanMessage(content=user_input)
    else:
        user_input = input("Riprova, forniscimi un nome corretto: ")
        user_message = HumanMessage(content=user_input)
    
    system_prompt = SystemMessage(content=f"""
    Sei un controllore di input. Devi valutare se il seguente testo rappresenta un **nome proprio di persona** valido.

    - **Input da valutare:** {user_message}

    ### Criteri di validità:
    - Il nome deve essere un **nome proprio umano**, realistico e riconoscibile, anche in lingue diverse dall’italiano (es. "Luca", "Giovanna", "Dexter", "Mei", "Carlos").
    - È accettabile l'uso di **nickname o varianti moderne**, che possono includere lettere e numeri (es. "Miki004", "Anna_Lisa", "Dexter1231", "Sara99"), purché la parte iniziale sia riconoscibile come nome.
    - Sono validi nomi con underscore o numeri finali, se il risultato è leggibile e somiglia a un nome proprio.
    - **Non sono validi**:
    - sequenze numeriche pure (es. "123456")
    - simboli o caratteri speciali isolati (es. "@@@")
    - nomi di oggetti, animali o concetti astratti (es. "tavolo", "libertà")
    - parole senza senso o generate casualmente (es. "xj93sd")
    - frasi intere
    - input vuoti o composti solo da spazi

    ### Esempi validi:
    - "Michele"
    - "Giovanna"
    - "Miki004"
    - "Anna_Lisa"
    - "Dexter1231"
    - "Mei88"

    ### Esempi non validi:
    - "123456"
    - "!!!@@@"
    - "tavolo"
    - "xj93sd"
    - ""
    - "     "

    ### Istruzioni finali:
    - Rispondi **esclusivamente** con: `valid` oppure `not_valid`
    - Non fornire spiegazioni o commenti

    Valuta ora.
    """)


    response = llm.invoke([system_prompt])
    return {"messages": [response]}

def get_format(state: State) -> State:
    ''' Funzione che imposta il formato dell'output '''
    messages = state["messages"][-1]
    if isinstance(messages, AIMessage):
        last_messages= messages.content
    else:
        last_messages = messages[0].content
    if last_messages == "valid":

        user_input = input("Descrivi il formato dell'output: ")
        user_message = HumanMessage(content=user_input)

    else: 
        user_input = input("Riprova, dai un formato corretto: ")
        user_message = HumanMessage(content=user_input)
    
    system_prompt = SystemMessage(content=f"""
    Sei un controllore di input. Devi valutare se il seguente testo rappresenta un **formato di output valido**.

    - **Input da valutare:** {user_message}

    ### Criteri di validità:
    - Il formato deve indicare **chiaramente** come dovrà essere strutturato l’output prodotto da un’intelligenza artificiale.
    - Deve essere un tipo di **struttura testuale, visiva o tecnica** comprensibile, ad esempio:
    - Tipi testuali: "lista puntata", "email formale", "paragrafo descrittivo"
    - Tipi strutturati: "tabella", "JSON", "output Markdown", "HTML", "YAML"
    - Non sono validi: frasi generiche, parole prive di senso, numeri, o contenuti che non rappresentano un formato (es. "ciao", "1234", "sì", "boh").
    - L’input non deve essere vuoto né composto solo da spazi o simboli.

    ### Istruzioni finali:
    - Rispondi **esclusivamente** con: `valid` oppure `not_valid`
    - Non aggiungere spiegazioni, commenti o testo extra

    Valuta ora.""")

    response = llm.invoke([system_prompt])
    return {"messages": [response]}

def evaluate_prompt(state: State) -> State:
    '''Funzione finale che da una valutazione al prompt'''
    system_prompt = SystemMessage(content=f"""Sei un valutatore di prompt valuta il seguente prompt composto da:
                                 RUOLO: {state['role']}, CONTESTO: {state['context']} e com COMPITO: {state['task']}. Dai un valutazione di come poteva essere migliorato o se è perfetto cosi com'è.""")

    response = llm.invoke([system_prompt])
    print(f"Robbi dice che il prompt: {response.content} ")
    return {"messages":[response]}

def should_continue(state:State) -> State:
    messages = state["messages"][-1]
    if isinstance(messages, AIMessage):
        last_messages= messages.content
    else:
        last_messages = messages[0].content
    if last_messages == "valid":
        return "continue"
    else:
        return "loop"

grap = StateGraph(State)

grap.add_node("get_name", get_name)
grap.add_node("get_role", get_role)
grap.add_node("get_context", get_context)
grap.add_node("get_task",get_task)
grap.add_node("get_format", get_format)
grap.add_node("evaluate_prompt",evaluate_prompt)
grap.add_edge(START, "get_name")

grap.add_conditional_edges(
    "get_name",
    should_continue,
    {
        "continue" : "get_role",
        "loop": "get_name"
    }
)

grap.add_conditional_edges(
    "get_role",
    should_continue,
    {
        "continue" : "get_context",
        "loop": "get_role"
    }
)

grap.add_conditional_edges(
    "get_context",
    should_continue,
    {
        "continue" : "get_task",
        "loop": "get_context"
    }
)

grap.add_conditional_edges(
    "get_task",
    should_continue,
    {
        "continue" : "get_format",
        "loop": "get_task"
    }
)

grap.add_conditional_edges(
    "get_format",
    should_continue,
    {
        "continue" : "evaluate_prompt",
        "loop": "get_format"
    }
)
grap.add_conditional_edges(
    "evaluate_prompt",
    should_continue,
    {
        "continue" : END,
        "loop": END
    }
)

app = grap.compile()
from PIL import Image
import io

img_bytes = app.get_graph().draw_mermaid_png()
image = Image.open(io.BytesIO(img_bytes))
image.show() 
# app.invoke({"messages": []})


chat_page_tutorial = ChatTutorial(self.master) # ChatTutorial(self.master)
chat_page_tutorial.pack(fill="both", expand=True)
