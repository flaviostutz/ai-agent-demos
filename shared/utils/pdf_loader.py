"""PDF document loader for policy documents."""

from pathlib import Path
from typing import List
import PyPDF2
from shared.monitoring.logger import get_logger

logger = get_logger(__name__)


class PDFLoader:
    """Load and extract text from PDF documents."""

    @staticmethod
    def load_pdf(file_path: str) -> str:
        """
        Load text content from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a valid PDF
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        if path.suffix.lower() != ".pdf":
            raise ValueError(f"File is not a PDF: {file_path}")

        try:
            with open(file_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []

                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num}: {e}")

                result = "\n\n".join(text_content)
                logger.info(f"Loaded PDF: {file_path} ({len(pdf_reader.pages)} pages)")
                return result

        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {e}")
            raise

    @staticmethod
    def load_multiple_pdfs(file_paths: List[str]) -> str:
        """
        Load text content from multiple PDF files.

        Args:
            file_paths: List of paths to PDF files

        Returns:
            Combined text content from all PDFs
        """
        all_content = []
        for file_path in file_paths:
            try:
                content = PDFLoader.load_pdf(file_path)
                all_content.append(f"=== Document: {Path(file_path).name} ===\n\n{content}")
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")

        return "\n\n" + "=" * 80 + "\n\n".join(all_content)

    @staticmethod
    def load_directory(directory_path: str, pattern: str = "*.pdf") -> str:
        """
        Load all PDF files from a directory.

        Args:
            directory_path: Path to directory containing PDFs
            pattern: File pattern to match (default: *.pdf)

        Returns:
            Combined text content from all matching PDFs
        """
        dir_path = Path(directory_path)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")

        pdf_files = list(dir_path.glob(pattern))
        if not pdf_files:
            logger.warning(f"No PDF files found in {directory_path} matching {pattern}")
            return ""

        logger.info(f"Found {len(pdf_files)} PDF files in {directory_path}")
        file_paths = [str(f) for f in pdf_files]
        return PDFLoader.load_multiple_pdfs(file_paths)