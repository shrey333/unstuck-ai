import time
from functools import lru_cache
from typing import AsyncGenerator
from fastapi import Depends
from src.core.config import get_settings, Settings


import redis
from pinecone import Pinecone, ServerlessSpec
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.cache import RedisCache
from langchain.embeddings import CacheBackedEmbeddings
from langchain_community.storage import RedisStore


@lru_cache()
def get_vectorstore(settings: Settings | None = None) -> PineconeVectorStore:
    if settings is None:
        settings = get_settings()

    pc = Pinecone(api_key=settings.PINECONE_API_KEY.get_secret_value())
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
    if settings.PINECONE_INDEX_NAME not in existing_indexes:
        pc.create_index(
            name=settings.PINECONE_INDEX_NAME,
            dimension=3072,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(settings.PINECONE_INDEX_NAME).status["ready"]:
            time.sleep(1)
    index = pc.Index(settings.PINECONE_INDEX_NAME)

    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY.get_secret_value(),
    )

    redis_client = get_redis_client(settings, for_cache=True)

    cached_embedder = CacheBackedEmbeddings.from_bytes_store(
        embeddings, RedisStore(client=redis_client), namespace=embeddings.model
    )

    vector_store = PineconeVectorStore(index, cached_embedder)
    return vector_store


@lru_cache()
def get_redis_client(
    settings: Settings | None = None,
    for_cache: bool = False,
) -> redis.Redis:
    """Get Redis client.

    Args:
        settings: Application settings
        for_cache: If True, returns a client configured for LangChain caching
    """
    if settings is None:
        settings = get_settings()

    if for_cache:
        # Client for LangChain cache (expects bytes)
        return redis.Redis(
            host=str(settings.UPSTASH_REDIS_URL),
            port=6379,
            password=settings.UPSTASH_REDIS_TOKEN.get_secret_value(),
            ssl=True,
            encoding="utf-8",  # Keep encoding but disable auto-decode
            decode_responses=False,
        )
    else:
        # Client for general use (returns strings)
        return redis.Redis(
            host=str(settings.UPSTASH_REDIS_URL),
            port=6379,
            password=settings.UPSTASH_REDIS_TOKEN.get_secret_value(),
            ssl=True,
            encoding="utf-8",
            decode_responses=True,
        )


@lru_cache()
def get_llm_client(
    settings: Settings | None = None,
) -> ChatGoogleGenerativeAI:
    """Initialize Google GenerativeAI client."""
    if settings is None:
        settings = get_settings()

    redis_client = get_redis_client(settings, for_cache=True)

    llm_cache = RedisCache(redis_client)

    llm = ChatGoogleGenerativeAI(
        model=settings.CHAT_MODEL,
        google_api_key=settings.GOOGLE_API_KEY.get_secret_value(),
    )
    return llm
