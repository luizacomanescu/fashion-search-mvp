import faiss
import numpy as np

print("FAISS import OK")

d = 512
index = faiss.IndexFlatIP(d)

print("Index created")

x = np.random.random((10, d)).astype("float32")
faiss.normalize_L2(x)

index.add(x)

print("Add OK")

q = np.random.random((1, d)).astype("float32")
faiss.normalize_L2(q)

D, I = index.search(q, 3)

print("Search OK", I)