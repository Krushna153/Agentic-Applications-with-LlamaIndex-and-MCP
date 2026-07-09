import os
import asyncio
from typing import Optional
from llama_index.core.tools import FunctionTool
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI
from datasets import load_dataset
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.memory import Memory

from dotenv import load_dotenv


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

def search_e_commerce_dataset(query: str) -> str:
    """Useful to search cloting items and prices in an e-commerce dataset.""" # call this a docstring
    print(f"Searching e-commerce dataset for: {query}")
    response = query_engine.query(query)
    return response.response


async def main():
    llm = OpenAI(model="gpt-4.1")
    agent_prompt = """
    You are a helpful assistant that can help answer siimple use questions or 
    search through clothing items and prices in an e-commerce dataset.
    """
    memory = Memory.from_defaults(token_limit=40000)

    agent = FunctionAgent(tools=[search_e_commerce_dataset], 
                          llm=llm, 
                          system_prompt=agent_prompt)
    
    while True:
        user_input = input("Enter your query: ")
        if user_input.lower() == "exit":
            break
        response = await agent.run(user_input, memory=memory)
        print(response)


if __name__ == "__main__":
    asyncio.run(main())




