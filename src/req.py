import requests   
from dotenv import load_dotenv
import os
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

wiki_titles = ["Toronto", "Chicago", "Houston", "Boston", "Atlanta"]
wiki_texts = []
for title in wiki_titles:
    response = requests.get(
            "https://en.wikipedia.org/w/api.php",
        params={
                "action": "query",
                "format": "json",
                "titles": title,
                "prop": "extracts",
                # 'exintro': True,
                "explaintext": True,
        },
    ).json()
    page = next(iter(response["query"]["pages"].values()))
    wiki_texts.append(page["extract"])

#salva i file che ottieni in una cartella   

#avvisa che l'indice creato dovrà contenere vettori della lunghezza stabilita dal modello
index = faiss.IndexFlatL2(len(embeddings.embed_query("hello world")))

vector_store = FAISS(
    embedding_function=embeddings,
    index=index,
    docstore=InMemoryDocstore(),
    index_to_docstore_id={},
)

documents = []
for wiki_text in wiki_texts:
    documents.append(Document(page_content=wiki_text))

print("Adding Documents...")
vector_store.add_documents(documents=documents)
print("Saving the vector store")
vector_store.save_local("rsc")
