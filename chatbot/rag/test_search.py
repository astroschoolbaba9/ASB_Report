import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(
    path="./chroma_db"
)

collection = client.get_collection(
    "asb_knowledge"
)

query = input("Question: ")

embedding = model.encode(
    query
).tolist()

results = collection.query(
    query_embeddings=[embedding],
    n_results=3
)

print("\nRESULTS:\n")

for doc in results["documents"][0]:
    print("=" * 50)
    print(doc[:500])
    print()