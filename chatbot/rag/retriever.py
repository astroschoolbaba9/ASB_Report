from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "chroma_db"

model = None
client = None
collection = None

def _init_rag():
    global model, client, collection
    if collection is not None:
        return
    
    from sentence_transformers import SentenceTransformer
    import chromadb
    
    print("Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    print(f"Using ChromaDB: {DB_PATH}")
    client = chromadb.PersistentClient(path=str(DB_PATH))
    try:
        collection = client.get_collection("asb_knowledge")
        print("Collection loaded successfully")
    except Exception as e:
        print(f"Collection 'asb_knowledge' not found: {e}. Creating a fresh empty collection.")
        collection = client.get_or_create_collection("asb_knowledge")

def retrieve(query, n_results=3):
    _init_rag()
    embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[embedding],
        n_results=n_results
    )

    return results["documents"][0]


if __name__ == "__main__":

    while True:

        query = input("\nQuestion: ")

        if query.lower() == "exit":
            break

        docs = retrieve(query)

        print("\nRESULTS:\n")

        for i, doc in enumerate(docs, 1):
            print(f"\n--- Result {i} ---\n")
            print(doc[:600])