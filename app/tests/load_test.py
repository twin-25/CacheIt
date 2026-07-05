import requests
import time

BASE_URL = "http://localhost:8000"
SESSION_ID = "load_test1_session"

questions = [
    "What is recursion?",
    "What is a linked list?",
    "What is a binary tree?",
    "What is dynamic programming?",
    "What is a hash table?",
    "What is object oriented programming?",
    "What is a stack?",
    "What is a queue?",
    "What is a graph?",
    "What is sorting?"
]

paraphrases = [
    "Can you explain recursion to me?",
    "How does a linked list work?",
    "Can you describe a binary tree?",
    "Explain dynamic programming to me.",
    "How does a hash table work?",
    "What do you mean by object oriented programming?",
    "How does a stack data structure work?",
    "Can you explain what a queue is?",
    "What is a graph in computer science?",
    "What are sorting algorithms?"
]

def send_request(question):
    payload = {
        "session_id": SESSION_ID,
        "question": question,
        "messages": [{"role": "user", "content": question}],
        "system": "You are a helpful assistant."
    }
    requests.post(f"{BASE_URL}/v1/messages", json=payload)

# create session
print("Creating session...")
requests.post(f"{BASE_URL}/session/{SESSION_ID}")

# round 1 — misses
print("Round 1 — new questions...")
for q in questions:
    send_request(q)

# round 2 — hits
print("Round 2 — same questions...")
for q in questions:
    send_request(q)

# round 3 — paraphrases
print("Round 3 — paraphrases...")
for q in paraphrases:
    send_request(q)

# cleanup
requests.delete(f"{BASE_URL}/session/{SESSION_ID}")
print("Done — check Prometheus/Grafana for results.")