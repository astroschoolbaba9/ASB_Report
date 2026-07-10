from sentence_transformers import SentenceTransformer
from chatbot.rag.chunker import create_chunks
import chromadb
from pathlib import Path

# Load embedding model
print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create ChromaDB client relative to this file
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(
    path=str(DB_PATH)
)

# Delete old collection to avoid duplicate embeddings
try:
    client.delete_collection("asb_knowledge")
    print("Deleted old collection")
except Exception:
    print("No existing collection found")

# Create fresh collection
collection = client.get_or_create_collection(
    name="asb_knowledge"
)


def build_vector_store():

    chunks = create_chunks()

    print(f"\nProcessing {len(chunks)} chunks...\n")

    for idx, chunk in enumerate(chunks):

        try:

            embedding = model.encode(
                chunk["content"]
            ).tolist()

            collection.add(
                ids=[str(idx)],
                embeddings=[embedding],
                documents=[chunk["content"]],
                metadatas=[
                    {
                        "source": chunk["source"],
                        "chunk_id": chunk["chunk_id"]
                    }
                ]
            )

            if idx % 5 == 0:
                print(
                    f"Processed {idx + 1}/{len(chunks)} chunks"
                )

        except Exception as e:

            print(
                f"Error processing chunk {idx}: {e}"
            )

    print(
        f"\nStored {len(chunks)} chunks successfully"
    )


if __name__ == "__main__":
    build_vector_store()