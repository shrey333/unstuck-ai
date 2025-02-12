from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import get_settings
from src.api.v1.router import api_router
from src.api.health import health_router

settings = get_settings()


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="""
        Unstuck AI API Documentation
        
        ## Features
        * AI-powered assistance
        * Real-time chat interface
        * Code analysis and suggestions
        
        ## Authentication
        Most endpoints require authentication. Include your API key in the request headers.
        """,
        debug=settings.DEBUG,
        version=settings.API_VERSION,
        docs_url=f"{settings.API_PREFIX}/docs",
        redoc_url=f"{settings.API_PREFIX}/redoc",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        openapi_tags=[
            {
                "name": "health",
                "description": "Health check endpoints to monitor API status",
            },
            {"name": "chat", "description": "Endpoints for chat interaction with AI"},
            {
                "name": "analysis",
                "description": "Code analysis and suggestion endpoints",
            },
        ],
        contact={
            "name": "API Support",
            "email": "support@unstuck-ai.com",
        },
        license_info={
            "name": "Private License",
            "url": "https://unstuck-ai.com/license",
        },
    )

    # Configure CORS with specific origin
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS,  # Get from settings
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Set-Cookie"],
    )

    # Include routers
    app.include_router(health_router, tags=["health"])
    app.include_router(api_router, prefix=settings.API_PREFIX)

    return app


app = create_application()
