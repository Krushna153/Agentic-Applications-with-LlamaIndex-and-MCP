
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

class AdminEvent(Event):
    index: int

class ECommerceAdminAgent(Workflow):
    def __init__(self, client, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = OpenAI(model="gpt-5")
        self.weaviate_agent = QueryAgent(client=client, collections=["ECommerce"])
        self.collection = client.collections.get("ECommerce")
        # Load JSON file with clothing items
        with open("new_clothing_items.json", "r") as f:
            self.new_items = json.load(f)
        
    @step
    def start(self, ev: StartEvent) -> AskEvent | SearchEvent | AdminEvent:
        decision_prompt = f"""
        Given the query '{ev.query}', return the relevant category of the query. 
        If the query is a question that can be answered in natural language, return 'Ask'.
        If the query is a question that can be answered by searching the database and returning a list of objects, return 'Search'.
        If the query is about adding an item to the collection, return 'Admin'.            
        """
        response = self.llm.complete(decision_prompt)
        if response.text == "Ask":
            return AskEvent(query=ev.query)
        elif response.text == "Search":
            return SearchEvent(query=ev.query)
        elif response.text == "Admin":
            response = self.llm.complete(
            f"""Evaluate the requested index from the query: '{ev.query}', return the number only.""")
            return AdminEvent(index=int(response.text))

    @step
    async def admin(self, ev: HumanResponseEvent | AdminEvent, ctx: Context) -> InputRequiredEvent | StopEvent:
        if isinstance(ev, AdminEvent):
            item = self.new_items[ev.index]
            properties = item.get("properties", item)
            await ctx.store.set("item_index", ev.index)
            return InputRequiredEvent(confirmation=f"Please confirm that this is the item you want to add (answer yes or no) {properties}:")
        elif isinstance(ev, HumanResponseEvent):
            if ev.response.lower() == "yes":
                item = self.new_items[await ctx.store.get("item_index")]
                properties = item.get("properties", item)
                self.collection.data.insert(properties=properties)
                return StopEvent(f"Successfully added item: {properties["name"]} to the collection.")
            else:
                return StopEvent("Aborted adding item to the collection.")
        
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
    with weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
    ) as client:
        agent = ECommerceAdminAgent(client=client, verbose=True)
        while True:
            user_input = input("Enter your query: ")
            if user_input.lower() == "exit":
                break
            handler = agent.run(query=user_input)
            async for event in handler.stream_events():
                if isinstance(event, InputRequiredEvent):
                    response = input(event.confirmation)
                    handler.ctx.send_event(HumanResponseEvent(response=response))

            final_result = await handler
            print(final_result)
if __name__ == "__main__":
    asyncio.run(main())