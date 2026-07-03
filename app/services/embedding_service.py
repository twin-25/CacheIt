from sentence_transformers import SentenceTransformer
from app.config import EMBEDDING_MODEL as emdb_model
import numpy as np

model = SentenceTransformer(emdb_model)


def embed(text):
  embedding = model.encode(text)
  return np.array(embedding, dtype=np.float32).tobytes()
