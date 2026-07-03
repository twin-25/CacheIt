from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL as emdb_model

model = SentenceTransformer(emdb_model)


def embed(text):
  embedding = model.encode(text)
  return embedding.tolist()
