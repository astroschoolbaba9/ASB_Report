from pathlib import Path


def load_documents():
    docs = []

    # Project root
    BASE_DIR = Path(__file__).resolve().parents[2]

    knowledge_dirs = [
        BASE_DIR / "chatbot" / "knowledge_base" / "raw",
        BASE_DIR / "chatbot" / "knowledge_base" / "company",
        BASE_DIR / "chatbot" / "knowledge_base" / "reports",
        BASE_DIR / "chatbot" / "knowledge_base" / "faq",
        BASE_DIR / "chatbot" / "knowledge_base" / "policies",
    ]

    for folder in knowledge_dirs:

        print(f"Loading from: {folder}")

        if not folder.exists():
            continue

        for file in folder.glob("*.md"):

            try:

                content = file.read_text(
                    encoding="utf-8",
                    errors="ignore"
                )

                if not content.strip():
                    continue

                docs.append({
                    "source": file.name,
                    "content": content
                })

            except Exception as e:

                print(
                    f"Error reading {file}: {e}"
                )

    return docs


if __name__ == "__main__":

    docs = load_documents()

    print(f"\nLoaded {len(docs)} documents\n")

    for doc in docs:
        print(doc["source"])