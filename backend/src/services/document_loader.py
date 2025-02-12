# services/document_loader.py
from io import BytesIO
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from pypdf import PdfReader
import logging

logger = logging.getLogger(__name__)

def process_pdf(file_bytes: bytes) -> List[Document]:
    """
    Process a PDF file and return a list of documents.
    Args:
        file_bytes: Raw bytes of the PDF file
    Returns:
        List of Document objects with text content and metadata
    """
    try:
        # Create a BytesIO object from the file bytes
        pdf_file = BytesIO(file_bytes)
        
        # First check if the PDF is valid and get total pages
        pdf = PdfReader(pdf_file)
        total_pages = len(pdf.pages)
        
        if total_pages == 0:
            raise ValueError("PDF file appears to be empty")

        # Reset file pointer for the loader
        pdf_file.seek(0)
        
        # Create documents with proper metadata
        documents = []
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()
            if text.strip():  # Only add pages with content
                documents.append(
                    Document(
                        page_content=text,
                        metadata={
                            "source": "uploaded_pdf",
                            "page": page_num,
                            "total_pages": total_pages,
                        }
                    )
                )

        if not documents:
            raise ValueError("No text content found in the PDF")

        logger.info(f"Successfully processed PDF with {len(documents)} pages")
        return documents

    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process PDF: {str(e)}")
