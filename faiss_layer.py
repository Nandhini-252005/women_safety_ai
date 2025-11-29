import numpy as np
import faiss
import os

INDEX = "data/faiss_index.bin"
memory = []

if os.path.exists(INDEX):
    index = faiss.read_index(INDEX)
else:
    index = faiss.IndexFlatL2(384)


def faiss_add(vec, text):
    memory.append(text)
    index.add(np.array([vec]).astype("float32"))
    faiss.write_index(index, INDEX)


def faiss_search(vec):
    if index.ntotal == 0:
        return []
    D, I = index.search(np.array([vec]).astype("float32"), 3)
    return [memory[i] for i in I[0] if i < len(memory)]
