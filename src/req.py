import requests   
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

wiki_titles = ["Toronto", "Chicago", "Houston", "Boston", "Atlanta"]

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
    wiki_text = page["extract"]

#salva i file che ottieni in una cartella   