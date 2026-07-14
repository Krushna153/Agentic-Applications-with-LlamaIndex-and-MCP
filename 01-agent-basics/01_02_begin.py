import os
import asyncio
from typing import Optional
from llama_index.core.tools import FunctionTool
from llama_index.core.agent.workflow import FunctionAgent, AgentWorkflow
from llama_index.llms.openai import OpenAI
from datasets import load_dataset
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.memory import Memory 

from dotenv import load_dotenv

load_dotenv(".env.example")

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
    # Useful to search through clothing items and prices in an e-commerce dataset
    response = query_engine.query(query)
    return response.response

async def main():
    llm = OpenAI(model="gpt-4.1-mini", api_key=OPENAI_API_KEY)
    agent_prompt = """
    You are a helpful e-commerce assistant. You have access to a tool that allows you to search through a dataset of clothing items and their prices. Use this tool to answer user questions or seacrh through clothing items and prices in an e-commerce dataset. If the user asks a question that requires searching through the dataset, use the tool to find the answer. If the user asks a question that does not require searching through the dataset, answer the question directly.
    """

    memory = Memory.from_defaults(token_limit=40000)

    # Define your agent based on the LLM, tools, and system prompt
    agent = FunctionAgent(llm=llm, 
                          tools=[search_e_commerce_dataset], 
                          system_prompt=agent_prompt)
    
    while True:
        user_input = input("Enter your query: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the agent. Goodbye!")
            break
        
        response = await agent.run(user_input, memory=memory)
        print(f"Agent: {response}")

if __name__ == "__main__":
    asyncio.run(main())
