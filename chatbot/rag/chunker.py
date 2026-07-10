from chatbot.rag.loader import load_documents

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50


def chunk_text(text):
    chunks = []

    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        chunks.append(text[start:end])

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


def create_chunks():
    documents = load_documents()

    all_chunks = []

    for doc in documents:

        chunks = chunk_text(doc["content"])

        for i, chunk in enumerate(chunks):

            all_chunks.append({
                "source": doc["source"],
                "chunk_id": i,
                "content": chunk
            })

    return all_chunks


if __name__ == "__main__":

    chunks = create_chunks()

    print(f"Total chunks: {len(chunks)}")

    print("\nSample:\n")

    print(chunks[0]["content"][:500])