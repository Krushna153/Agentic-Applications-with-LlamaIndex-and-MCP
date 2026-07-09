import os, json
import asyncio
from pydantic import BaseModel
from workflows import Workflow, Context,step
from workflows.events import Event, StartEvent, StopEvent
from datasets import load_dataset
from llama_index.core import Document, VectorStoreIndex
from llama_index.llms.openai import OpenAI
from dotenv import load_dotenv
from llama_index.utils.workflow import draw_all_possible_flows

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def create_query_engine():
    ecommerce_dataset = load_dataset(
        "weaviate/agents", "query-agent-ecommerce", split="train", streaming=True
    )
    documents = [Document(text=row["properties"]["description"], 
                          metadata={"name": row["properties"]["name"], "price": row["properties"]["price"], "category": row["properties"]["category"]}) 
                          for row in ecommerce_dataset]
    index = VectorStoreIndex.from_documents(documents[:100])
    engine = index.as_query_engine(similarity_top_k=10)
    return engine

query_engine = create_query_engine()

async def main():
    pass


if __name__ == "__main__":
    asyncio.run(main())