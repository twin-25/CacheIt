from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("BAAI/bge-small-en-v1.5")

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

q1 = "What is recursion?"
q2 = "Can you explain recursion to me?"
q3 = "What is iteration?"
q4 = "How does recursion work in Python?"

e1 = model.encode(q1)
e2 = model.encode(q2)
e3 = model.encode(q3)
e4 = model.encode(q4)

print(f"q1 vs q2 (paraphrase):     {cosine_similarity(e1, e2):.4f}")
print(f"q1 vs q3 (different):      {cosine_similarity(e1, e3):.4f}")
print(f"q1 vs q4 (related):        {cosine_similarity(e1, e4):.4f}")