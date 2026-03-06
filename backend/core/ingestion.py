import os
from core.parsing import HierarchicalPDFParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.documents import Document
import hashlib
from core.llm_config import get_embeddings

# Initialize Embeddings (always OpenAI — see llm_config.py)
embeddings = get_embeddings()

# Initialize Vector DB (Persistent)
PERSIST_DIRECTORY = "./chroma_db"

def ingest_document(file_path: str, strategy: str = "hierarchical"):
    """
    Parses a PDF, chunks it, and stores embeddings in ChromaDB.
    Strategies: 'flat' (simple page-based) or 'hierarchical' (chapter-based).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    filename = os.path.basename(file_path)
    collection_name = f"system_docs_{strategy}"
    
    # 0. Flush the entire vector database collection to ensure only the new document is assessed
    try:
        vs = Chroma(collection_name=collection_name, embedding_function=embeddings, persist_directory=PERSIST_DIRECTORY)
        # We completely delete the collection so old documents are flushed
        vs.delete_collection()
        print(f"Flushed old library for collection: {collection_name}")
    except Exception as e:
        print(f"Pre-ingestion cleanup warning: {e}")
    
    # 1. Load PDF
    if strategy == "hierarchical":
        parser = HierarchicalPDFParser()
        documents = parser.parse(file_path)
    else:
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        for doc in documents:
            doc.metadata["source"] = filename

    # 2. Split Text
    # Hierarchical might benefit from slightly larger context or metadata prepending
    chunk_size = 1500 if strategy == "hierarchical" else 1000
    chunk_overlap = 200 if strategy == "hierarchical" else 150
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    
    # Generate stable IDs for deduplication
    unique_chunks = []
    seen_ids = set()
    unique_ids = []
    
    for chunk in chunks:
        source = chunk.metadata.get("source", "unknown")
        page = chunk.metadata.get("page", 0)
        chapter = chunk.metadata.get("chapter", "")
        
        # ID input includes strategy and chapter to keep collections distinct if mixed
        id_input = f"{chunk.page_content}_{source}_{page}_{chapter}_{strategy}"
        chunk_id = hashlib.md5(id_input.encode('utf-8')).hexdigest()
        
        if chunk_id not in seen_ids:
            seen_ids.add(chunk_id)
            unique_ids.append(chunk_id)
            chunk.metadata["chunk_id"] = chunk_id
            unique_chunks.append(chunk)

    # 3. Store in Vector DB
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )
    
    if unique_chunks:
        vector_store.add_documents(unique_chunks, ids=unique_ids)
    
    return len(unique_chunks)

def get_vector_store(strategy: str = "flat"):
    collection_name = f"system_docs_{strategy}"
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )
