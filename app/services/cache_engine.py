from app.services.embedding_service import embed
from redisvl.index import SearchIndex
from app.config import REDIS_URL, SIMILARITY_THRESHOLD
import redis
from redisvl.query import VectorQuery

redis_client = redis.from_url(REDIS_URL)



def create_session_index(session_id):
  try:
    index = SearchIndex.from_dict({
    "index":{
      "name": f"session_{session_id}",
      "prefix": f"cache_{session_id}",
      "storage_type": "hash"
    },
    "fields":[
      {"name":"question", "type":"text"},
      {"name": "answer", "type": "text"},
      {"name": "vector",
      "type": "vector",
      "attrs": {
        "algorithm": "hnsw",
        "dims": 384,
        "distance_metric": "cosine"
      }
      }
    ]
      }, redis_client=redis_client, validate_on_load=True)
    
    index.create(overwrite=False)

    return index
  
  except Exception as e:
    raise RuntimeError(f"failed to create cache index for session {session_id}: {e}")

def delete_session_index(session_id):
  try:
    index = SearchIndex.from_existing(
      f"session_{session_id}",
      redis_url=REDIS_URL
    )
    index.delete(drop=True)

  except Exception as e:
    raise RuntimeError(f"Failed to delete cache index for session {session_id}: {e}")


def search_cache(session_id, question):
  try:
    vector = embed(question)
    index = SearchIndex.from_existing(
      f"session_{session_id}",
      redis_url=REDIS_URL
    )

    query = VectorQuery(
      vector=vector, 
      vector_field_name="vector",
      return_fields=["answer", "vector_distance"],
      num_results=1
    )

    results = index.query(query)

    if results:
      top_result = results[0]
      distance = float(top_result["vector_distance"])
      if distance < (1 - SIMILARITY_THRESHOLD):
        return top_result["answer"]
  except Exception:
    pass

  return None


def store_in_cache(session_id, question , answer):
  try:
    vector = embed(question)
    index = SearchIndex.from_existing(
      f"session_{session_id}",
      redis_url=REDIS_URL
    )

    input_data = {
      "question": question,
      "answer": answer,
      "vector": vector
    }

    index.load([input_data])

  except Exception as e:
    print(f"Cache store failed: {e}")


