from sentence_transformers import SentenceTransformer
import numpy as np
import csv

model = SentenceTransformer("BAAI/bge-small-en-v1.5")

same = []
different = []

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

with open("sts_sample.tsv", "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter="\t")
    for row in reader:
        if len(row) < 3:
          continue
        score, s1, s2 = row[0], row[1], row[2]
        score = float(score)/5
        model_score = cosine_similarity(model.encode(s1), model.encode(s2))

        if score >= 0.8:
            same.append(model_score)

        else:
            different.append(model_score)

print(f"Average similarity for same meaning pairs: {np.mean(same):.4f}")
print(f"Average similarity for different pairs: {np.mean(different):.4f}")
print(f"Suggested threshold: {(np.mean(same) + np.mean(different)) / 2:.4f}")


