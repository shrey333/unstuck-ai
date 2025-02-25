from typing_extensions import Annotated, List
import logging
from fastapi import HTTPException

from langgraph.graph import MessagesState, StateGraph, END
from langchain_core.tools import tool
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import InjectedStore
from langgraph.store.memory import InMemoryStore
from typing import List

from src.core.dependencies import get_llm_client, get_vectorstore, get_redis_client

# Configure logging
logger = logging.getLogger(__name__)

llm = get_llm_client()
vector_store = get_vectorstore()
redis_client = get_redis_client()


class State(MessagesState):
    context: List[Document]


@tool(response_format="content_and_artifact")
def retrieve(
    query: str,
    config: RunnableConfig,
    store: Annotated[BaseStore, InjectedStore()],
    filenames: List[str] = None,  # Optional list of filenames to filter by
):
    """Retrieve information related to a query, filenames and chat_id. You have access to documents
    related to the question.

    Args:
        query: The search query
        config: Configuration containing chat_id
        store: Document store
        filenames: Optional list of filenames to filter results by specific documents
    """
    chat_id = config.get("configurable", {}).get("thread_id")
    filter_dict = {"chat_id": chat_id}

    # Add filenames filter if provided
    if filenames:
        if len(filenames) == 1:
            filter_dict["source"] = filenames[0]
        else:
            # For multiple files, use $in operator to match any of the files
            filter_dict["source"] = {"$in": filenames}

    retrieved_docs = vector_store.similarity_search(query, k=5, filter=filter_dict)
    serialized = "\n\n".join(
        (f"Source: {doc.metadata}\n" f"Content: {doc.page_content}")
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs


def get_available_documents(chat_id: str) -> list[str]:
    """Get list of available documents for a chat session from Redis."""
    files_key = f"files:{chat_id}"
    files = redis_client.smembers(files_key)
    # Decode bytes to strings
    return sorted(file.decode("utf-8") for file in files) if files else []


def query_or_respond(state: State):
    """Generate tool call for retrieval or respond."""
    llm_with_tools = llm.bind_tools([retrieve])
    response = llm_with_tools.invoke(state["messages"])
    # MessagesState appends messages to state instead of overwriting
    return {"messages": [response], "context": []}


tools = ToolNode([retrieve])


def generate(state: State):
    """Generate answer."""
    # Get generated ToolMessages
    recent_tool_messages = []
    for message in reversed(state["messages"]):
        if message.type == "tool":
            recent_tool_messages.append(message)
        else:
            break
    tool_messages = recent_tool_messages[::-1]

    # Format into prompt
    docs_content = "\n\n".join(doc.content for doc in tool_messages)
    system_message_content = f"""
        You are an assistant for question-answering tasks. 
        If you don't know the answer, say that you don't know. 
        You have access to documents related to the question. \n\n
        Instructions for formatting the response:
            1. Use markdown formatting to make the answer more readable:
                - Use **bold** for key terms and important concepts
                - Use bullet points (`*`) for listing items or features
                - Use `code blocks` for technical terms, parameters, or steps
                - Use > for quoting directly from the documents
                - Use ### for section headings if needed
            2. Structure the response with clear paragraphs and headings
            3. If mentioning multiple points, use numbered lists
            4. If explaining a process, break it down into steps
            5. When referencing content from the following chunks, add a reference like <span id='1'></span>, <span id='2'></span>, <span id='3'></span>... etc.
            These will be used to link back to the source chunk.
            6. If you don't reference a chunk, just do not mention it at all.
        Use the following pieces of retrieved context to answer 
        the question.
        \n\n
        "{docs_content}"
    """
    conversation_messages = [
        message
        for message in state["messages"]
        if message.type in ("human", "system")
        or (message.type == "ai" and not message.tool_calls)
    ]
    prompt = [SystemMessage(system_message_content)] + conversation_messages

    # Run
    response = llm.invoke(prompt)
    context = []
    for tool_message in tool_messages:
        context.extend(tool_message.artifact)
    return {"messages": [response], "context": context}


def create_query_graph():
    graph_builder = StateGraph(State)

    graph_builder.add_node("query_or_respond", query_or_respond)
    graph_builder.add_node("tools", tools)
    graph_builder.add_node("generate", generate)

    graph_builder.set_entry_point("query_or_respond")
    graph_builder.add_conditional_edges(
        "query_or_respond",
        tools_condition,
        {END: END, "tools": "tools"},
    )
    graph_builder.add_edge("tools", "generate")
    graph_builder.add_edge("generate", END)

    memory = MemorySaver()
    docstore = InMemoryStore()

    return graph_builder.compile(checkpointer=memory, store=docstore)


graph = create_query_graph()


async def process_query(query: str, chat_id: str):
    """Process a query using the graph-based approach."""
    try:
        config = RunnableConfig(
            {"configurable": {"chat_id": chat_id, "thread_id": chat_id}}
        )

        # Get available documents from Redis
        available_docs = get_available_documents(chat_id)
        files_context = (
            "Available documents: " + ", ".join(available_docs)
            if available_docs
            else "No documents available"
        )

        final_step = graph.invoke(
            {
                "messages": [{"role": "user", "content": query + "\n" + files_context}],
                "config": {"thread_id": chat_id},
            },
            config=config,
        )

        return {
            "content": final_step["messages"][-1].content,
            "metadata": [
                {"content": doc.page_content, "source": doc.metadata["source"]}
                for doc in final_step.get("context", [])
            ],
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your query. Please try again later.",
        )
