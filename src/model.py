from transformers import DPRContextEncoder, DPRContextEncoderTokenizer
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import numpy as np
import faiss

def read_file(filename: str) -> list[str]:
    with open(filename, "r", encoding="utf-8") as file:
        text = file.read()
    paragraphs = text.split("\n")
    paragraphs = [para.strip() for para in paragraphs if len(para.strip())>0]
    return paragraphs

def encode(text_list:list[str], context_encoder:DPRContextEncoder, context_tokenizer:DPRContextEncoderTokenizer) -> np.ndarray :
    embeddings = []
    for text in text_list:
        inputs = context_tokenizer(text=text,return_tensors="pt",padding=True)
        outputs = context_encoder(**inputs)
        embeddings.append(outputs.pooler_output)
    return torch.cat(embeddings).detach().numpy()



paragraphs = read_file("rsc/text.txt")
#carichiamo un modello dal quale estrapolare il suo tokenizzatore 

context_tokenizer = DPRContextEncoderTokenizer.from_pretrained('facebook/dpr-ctx_encoder-single-nq-base')
context_encoder = DPRContextEncoder.from_pretrained('facebook/dpr-ctx_encoder-single-nq-base')

embeddings=encode(paragraphs,context_encoder=context_encoder, context_tokenizer=context_tokenizer)
print(embeddings.shape)

embedding_dim = 768
index = faiss.IndexFlatL2(embedding_dim)
context_embedding_np = np.array(embeddings).astype("float32")

index.add(context_embedding_np)

question = "Tell me about the Roman Empire"

from transformers import DPRQuestionEncoder, DPRQuestionEncoderTokenizer
question_encoder = DPRQuestionEncoder.from_pretrained('facebook/dpr-question_encoder-single-nq-base')
question_tokenizer = DPRQuestionEncoderTokenizer.from_pretrained('facebook/dpr-question_encoder-single-nq-base')


question_inputs = question_tokenizer(question, return_tensors="pt")
question_embeddings = question_encoder(**question_inputs).pooler_output.detach().numpy()

D,I = index.search(question_embeddings, k=3)
min_distance = min(D[0][:])
combined = list(zip(I[0][:],D[0][:]))

for idx, dis in combined:
    if min_distance==dis:
        para_idx = int(idx)


print("Most Similar sentence: "+ paragraphs[para_idx])

from transformers import BartForConditionalGeneration, BartTokenizer
model_name = "facebook/bart-large-cnn"
model = BartForConditionalGeneration.from_pretrained(model_name)
tokenizer = BartTokenizer.from_pretrained(model_name)

quest_embed = tokenizer(question, return_tensors="pt", max_length=1024, truncation = True)
summary_ids = model.generate(quest_embed["input_ids"], max_length=150, length_penalty =2.0, num_beams= 4, early_stopping= True)
answer = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

print("ANSWER: "+ answer)

