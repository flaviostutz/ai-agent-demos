"""Script to load documents into vector store."""

import sys
from pathlib import Path

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from shared.config import get_config
from shared.logging_utils import get_logger

logger = get_logger(__name__)


def load_documents_to_vectorstore():
    """Load PDF documents into Chroma vector store."""
    logger.info("Loading documents into vector store...")

    # Get configuration
    config = get_config().get_agent_config("loan_approval")

    # Initialize embeddings
    embeddings = OpenAIEmbeddings()

    # Document paths
    docs_dir = project_root / "data" / "documents"
    pdf_files = list(docs_dir.glob("*.pdf"))

    if not pdf_files:
        logger.error(f"No PDF files found in {docs_dir}")
        logger.info("Please run 'make generate-docs' first to create the loan rule documents")
        return

    logger.info(f"Found {len(pdf_files)} PDF files")

    # Load and split documents
    all_documents = []
    for pdf_file in pdf_files:
        logger.info(f"Loading {pdf_file.name}...")
        loader = PyPDFLoader(str(pdf_file))
        documents = loader.load()

        # Add metadata
        for doc in documents:
            doc.metadata["source"] = pdf_file.name
            doc.metadata["domain"] = "public"

        all_documents.extend(documents)

    logger.info(f"Loaded {len(all_documents)} pages total")

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    splits = text_splitter.split_documents(all_documents)
    logger.info(f"Split into {len(splits)} chunks")

    # Create vector store
    persist_directory = str(project_root / config.vector_store.persist_directory)
    Path(persist_directory).mkdir(parents=True, exist_ok=True)

    logger.info(f"Creating vector store in {persist_directory}...")
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        collection_name=config.vector_store.collection_name,
        persist_directory=persist_directory,
    )

    logger.info(f"Successfully loaded {len(splits)} chunks into vector store")
    logger.info("Vector store is ready for use!")


if __name__ == "__main__":
    load_documents_to_vectorstore()
