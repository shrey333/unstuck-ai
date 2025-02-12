from fastapi import APIRouter, Request, Response, Depends, HTTPException, status
from pydantic import BaseModel, Field
from uuid import uuid4
from typing import Dict, Any, List

from src.core.config import get_settings
from src.core.dependencies import get_redis_client
from src.services.query_processor import process_query

router = APIRouter()
settings = get_settings()

SESSION_COOKIE_NAME = "chat_id"
SESSION_TTL_SECONDS = 3 * 60 * 60  # sessions expire in 1 hour


def get_chat_id(request: Request, response: Response) -> str:
    """Get or create a chat session ID"""
    chat_id = request.cookies.get(SESSION_COOKIE_NAME)
    if not chat_id:
        chat_id = str(uuid4())
        response.set_cookie(
            key=SESSION_COOKIE_NAME, value=chat_id, max_age=SESSION_TTL_SECONDS
        )
    return chat_id


class AskRequest(BaseModel):
    """Request model for asking questions"""

    question: str = Field(
        ...,
        description="The question to ask about the uploaded documents",
        max_length=1000,
        example="What are the key findings in the research paper?",
    )

    class Config:
        json_schema_extra = {
            "example": {"question": "What are the key findings in the research paper?"}
        }


class SourceMetadata(BaseModel):
    """Model for source document metadata"""

    content: str = Field(..., description="Content snippet from the source document")
    source: str = Field(..., description="Source document identifier")


class AskResponse(BaseModel):
    """Response model for question answers"""

    answer: str = Field(..., description="The AI-generated answer to the question")
    source: List[SourceMetadata] = Field(
        ..., description="List of source documents used"
    )
    chat_id: str = Field(..., description="The session ID for this chat")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The key findings of the research paper include...",
                "source": [
                    {
                        "content": "The study found that...",
                        "source": "research_paper.pdf",
                    }
                ],
                "chat_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }


@router.post(
    "/ask",
    response_model=AskResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question about uploaded documents",
    description="""
    Ask questions about previously uploaded documents and receive AI-generated answers.
    
    The system will:
    * Use your chat session to identify relevant documents
    * Process your question using a graph-based approach
    * Generate a concise, contextual response
    * Include source information for verification
    
    Make sure to upload documents first using the /documents/upload endpoint.
    """,
    responses={
        200: {
            "description": "Successfully generated answer",
            "content": {
                "application/json": {
                    "example": {
                        "answer": "The key findings of the research paper include...",
                        "source": [
                            {
                                "content": "The study found that...",
                                "source": "research_paper.pdf",
                            }
                        ],
                        "chat_id": "550e8400-e29b-41d4-a716-446655440000",
                    }
                }
            },
        },
        400: {
            "description": "Invalid question format",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Question must be between 3 and 1000 characters"
                    }
                }
            },
        },
        404: {
            "description": "No relevant documents found",
            "content": {
                "application/json": {
                    "example": {"detail": "No documents found for this chat session"}
                }
            },
        },
    },
)
async def ask_question(
    request: Request,
    response: Response,
    payload: AskRequest,
) -> AskResponse:
    chat_id = get_chat_id(request, response)

    try:
        result = await process_query(payload.question, chat_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No documents found for this chat session",
        )

    return AskResponse(
        answer=result["content"],
        source=[SourceMetadata(**metadata) for metadata in result["metadata"]],
        chat_id=chat_id,
    )
