import faiss
from dotenv import load_dotenv
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAI
from pydantic import BaseModel, create_model, Field
from enum import Enum
import os

# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY")
# embedding = OpenAI(model="gpt-3.5-turbo-instruct")

# vector_db = FAISS.load_local("rsc",embeddings=embedding,allow_dangerous_deserialization=True)
# print("vector loaded")


# results = vector_db.similarity_search(
#     "Atlanta is a beautyful city",
#     k=2
# )
# for res in results:
#     print(f"* {res.page_content} [{res.metadata}]")

# retriever = vector_db.as_retriever()
# retriever.invoke("Stealing from the bank is a crime")