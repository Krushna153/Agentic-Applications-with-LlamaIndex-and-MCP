import asyncio
import json
import os
from dotenv import load_dotenv
import weaviate
from weaviate.auth import AuthApiKey
from weaviate.agents.query import QueryAgent
from llama_index.llms.openai import OpenAI
from workflows import Context, Workflow, step
from workflows.events import Event, StartEvent, StopEvent, HumanResponseEvent, InputRequiredEvent


load_dotenv()

class AskEvent(Event):
    query: str

class SearchEvent(Event):
    query: str

class ECommerceAgent(Workflow):
    def __init__(self, client, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = OpenAI(model="gpt-5")
        self.weaviate_agent = QueryAgent(client=client, collections=["ECommerce"])

    @step
    def start(self, ev: StartEvent) -> AskEvent | SearchEvent:
        decision_prompt = f"""
        Given the query '{ev.query}', return the relevant category of the query. 
        If the query is a question that can be answered in natural language, return 'Ask'.
        If the query is a question that can be answered by searching the database and returning a list of objects, return 'Search'.           
        """
        response = self.llm.complete(decision_prompt)
        if response.text == "Ask":
            return AskEvent(query=ev.query)
        elif response.text == "Search":
            return SearchEvent(query=ev.query)

    @step
    def ask(self, ev: AskEvent) -> StopEvent:
        response = self.weaviate_agent.ask(ev.query)
        return StopEvent(response.final_answer)
    
    @step
    def search(self, ev: SearchEvent) -> StopEvent:
        results = self.weaviate_agent.search(ev.query)
        response = self.llm.complete(
            f"""Here's the list of items for the the query '{ev.query}':
            {results.search_results.objects}. Return them as a readable list for the user.
            """
        )
        return StopEvent(response)


async def main():
     with  weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
    ) as client:
        agent = ECommerceAgent(client=client, verbose=True)
        while True:
            user_input = input("Enter your query: ")
            if user_input.lower() == "exit":
                break
            response = await agent.run(query=user_input)
            print(response)

if __name__ == "__main__":
    asyncio.run(main())