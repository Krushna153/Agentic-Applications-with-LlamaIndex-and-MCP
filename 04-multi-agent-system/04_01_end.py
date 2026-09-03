# Run this first: pip install llama-index-tools-mcp

from llama_index.tools.mcp.utils import workflow_as_mcp
import asyncio
import inspect
import os

asyncio.iscoroutinefunction = inspect.iscoroutinefunction

from dotenv import load_dotenv
from pydantic import BaseModel
import weaviate
from weaviate.auth import AuthApiKey
from weaviate.agents.query import QueryAgent
from llama_index.core.memory import Memory
from llama_index.llms.openai import OpenAI
from workflows import Context, Workflow, step
from workflows.events import Event, StartEvent, StopEvent

load_dotenv()

class QueryEvent(StartEvent):
    query: str

class AskEvent(Event):
    query: str

class SearchEvent(Event):
    query: str

class ECommerceAgent(Workflow):
    def __init__(self, client, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.llm = OpenAI(model="gpt-4.1-mini")
        self.weaviate_agent = QueryAgent(client=client, collections=["ECommerce"])

    @step
    def start(self, ev: QueryEvent) -> AskEvent | SearchEvent:
        response = self.llm.complete(
            f"""Given the query '{ev.query}', return the relevant category of the query. 
            If the query is a question that can be answered in natural language, return 'Ask'.
            If the query is a question that can be answered by searching the database and retyrning a list of objects, return 'Search'.            """
        )
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

# Create MCP server as a global variable
client = weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_URL"),
    auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")))

agent = ECommerceAgent(client=client)

mcp = workflow_as_mcp(agent, 
                      start_event_model=QueryEvent, 
                      workflow_name="e-commerce-tool", 
                      workflow_description="Useful to answer questions about e-commerce products (clothing items, prices etc).")

if __name__ == "__main__":
    mcp.run(transport="streamable-http")


'''
Steps how to run the MCP server and connect it to the Claude client:

1. type "claude" in the terminal to start the claude client. Authenticate with your API key.

2. Run the existing python file as you would do normally in the same terminal. This will start the MCP server on "http://localhost:8000".

3. Open another terminal. Paste the following command to add the MCP server to the claude client:
--> claude mcp add --transport http clothing http://127.0.0.1:8000/mcp
If this goes well, you will see this: Added HTTP MCP server clothing with URL: http://127.0.0.1:8000/mcp to local config

4. Type "claue" again the terminal to start the claude code.
You can use this MCP server with any MCP Clients such as Claude Code or Claude Desktop if you like.

5. type /mcp to list the servers you have added. You should see the clothing server listed. You can also press enter to see what tools are here. Under tools, you can see the name of the workflow as "e-commerce-tool".

6. You can also use Claude Code as a chat assistant that is able to access our e-commerce agent. For example, you can type: what skirts are below $50? and the agent will return a list of skirts that are below $50.

MCP client, here it is Claude Code, it will ask for the confirmation to run our MCP server. You can type "yes" to confirm.

'''