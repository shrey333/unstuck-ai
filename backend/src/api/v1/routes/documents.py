from fastapi import APIRouter, UploadFile, File, Request, Response, Depends, HTTPException, status
from uuid import uuid4
from typing import List
from pydantic import BaseModel


from src.core.dependencies import get_vectorstore
from src.services.document_loader import process_pdf
from src.core.config import get_settings

settings = get_settings()
router = APIRouter()

SESSION_COOKIE_NAME = "chat_id"
SESSION_TTL_SECONDS = 3 * 60 * 60  # e.g., sessions expire in 1 hour


class UploadResponse(BaseModel):
    """Response model for document upload"""
    chat_id: str
    total_chunks: int
    filenames: List[str]

    class Config:
        model_config = {
            "json_schema_extra": {
                "example": {
                    "chat_id": "550e8400-e29b-41d4-a716-446655440000",
                    "total_chunks": 42,
                    "filenames": ["document1.pdf", "document2.pdf"]
                }
            }
        }


def get_chat_id(request: Request, response: Response) -> str:
    """Get or create a chat session ID"""
    chat_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not chat_id:
        chat_id = str(uuid4())
        response.set_cookie(
            key=SESSION_COOKIE_NAME, value=chat_id, max_age=SESSION_TTL_SECONDS
        )
    return chat_id


@router.post(
    "/upload",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload PDF documents",
    description="""
    Upload one or more PDF documents for processing.
    
    The documents will be:
    * Processed and split into chunks
    * Associated with your chat session
    * Added to the vector store for later retrieval
    
    Returns the chat session ID and processing statistics.
    """,
    responses={
        201: {
            "description": "Documents successfully processed and stored",
            "content": {
                "application/json": {
                    "example": {
                        "chat_id": "550e8400-e29b-41d4-a716-446655440000",
                        "total_chunks": 42,
                        "filenames": ["document1.pdf", "document2.pdf"]
                    }
                }
            }
        },
        400: {
            "description": "Invalid file format or corrupt PDF",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid PDF file format"}
                }
            }
        },
        413: {
            "description": "File too large",
            "content": {
                "application/json": {
                    "example": {"detail": "File size exceeds maximum limit"}
                }
            }
        }
    }
)
async def upload_pdf(
    request: Request,
    response: Response,
    files: list[UploadFile] = File(
        ...,
        description="List of PDF files to upload. Maximum size: 10MB per file.",
    ),
    vectorstore=Depends(get_vectorstore),
) -> UploadResponse:
    chat_id = get_chat_id(request, response)
    all_docs = []
    total_chunks = 0
    filenames = []

    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )
            
        file_bytes = await file.read()
        docs = process_pdf(file_bytes)
        filenames.append(file.filename)

        for doc in docs:
            if not doc.metadata:
                doc.metadata = {}
            doc.metadata.update(
                {
                    "chat_id": chat_id,
                    "source": file.filename,  # Store original filename
                }
            )
            all_docs.append(doc)
            total_chunks += 1

    if all_docs:
        vectorstore.add_documents(all_docs)

    return UploadResponse(
        chat_id=chat_id,
        total_chunks=total_chunks,
        filenames=filenames
    )
