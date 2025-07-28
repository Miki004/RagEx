import faiss
from dotenv import load_dotenv
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAI
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
embedding = OpenAI(model="text-embedding-3-large")

vector_db = FAISS.load_local("rsc",embeddings=embedding,allow_dangerous_deserialization=True)
print("vector loaded")
print(vector_db)