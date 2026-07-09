import asyncio
import os
from dotenv import load_dotenv
import weaviate
from weaviate.auth import AuthApiKey
from weaviate.agents.query import QueryAgent
from llama_index.llms.openai import OpenAI
from workflows import Workflow, step
from workflows.events import Event, StartEvent, StopEvent

load_dotenv()

async def main():
    with  weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
    ) as client:
        pass

if __name__ == "__main__":
    asyncio.run(main())