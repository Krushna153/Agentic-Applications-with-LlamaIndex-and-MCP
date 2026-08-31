#!/usr/bin/env python3
import os
import weaviate
from weaviate.agents.query import QueryAgent
from weaviate.agents.classes import QueryAgentCollectionConfig, ProgressMessage, StreamedTokens
from weaviate.classes.query import Filter
from weaviate.auth import AuthApiKey
import dotenv

dotenv.load_dotenv(override=True)

# This script assumes you have a Weaviate instance with an "ECommerce" collection

def main():
    """
    Demonstrates advanced patterns for customizing the Weaviate Query Agent.
    """
    with weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
    ) as client:
        print("✓ Connected to Weaviate")


        # 1. Define the Agent's Persona with a System Prompt
        print("\n--- Pattern 1: System Prompt ---")
        fashion_expert_prompt = """
        You are a friendly and knowledgeable fashion expert specializing in vintage clothing.
        When asked for recommendations, provide a brief, enthusiastic description for each item,
        highlighting its vintage appeal. Your tone should be helpful and stylish.
        """

        qa_with_persona = QueryAgent(
            client=client,
            collections=["ECommerce"],
            system_prompt=fashion_expert_prompt
        )

        response = qa_with_persona.ask("I'm looking for a dress for a summer party.")
        print(f"Agent Persona Response:\n{response.final_answer}\n")


        # 2. Focus the Agent on the Right Data
        print("\n--- Pattern 2: Focusing on the Right Data ---")
        qa_generic = QueryAgent(client=client, collections=["ECommerce"])

        ecommerce_config = QueryAgentCollectionConfig(
            name="ECommerce",
            view_properties=["name", "price", "brand"]      # Limit the context for the LLM
        )

        response = qa_generic.ask(
            "I like vintage clothes. Recommend something.",
            collections=[ecommerce_config]
        )
        print("Focused Agent Response:")
        response.display()


        # 3. Create a Specialized Agent with Persistent Filters
        print("\n--- Pattern 3: Persistent Filters ---")
        luxury_bot = QueryAgent(
            client=client,
            collections=[
                QueryAgentCollectionConfig(
                    name="ECommerce",
                    # This filter is ALWAYS applied for this agent
                    additional_filters=(
                        Filter.by_property("price").greater_than(500) &
                        Filter.by_property("category").equal("Handbags")
                    )
                )
            ]
        )

        response = luxury_bot.ask("Find me an affordable t-shirt.")
        print("Specialized Luxury Bot Response:")
        response.display()


        # 4. Improve User Experience with Streaming
        print("\n--- Pattern 4: Streaming ---")
        # Use our persona agent from the first example
        response_generator = qa_with_persona.ask_stream(
            "Recommend some footwear for me."
        )

        print("Streaming Agent Response:")
        print("Agent: ", end="")
        for output in response_generator:
            if isinstance(output, ProgressMessage):
                # The message is a human-readable string, structured info available in output.details
                print(output.message)
            elif isinstance(output, StreamedTokens):
                # The delta is a string containing the next chunk of the final answer
                print(output.delta, end="", flush=True)
            else:
                # This is the final response, as returned by QueryAgent.ask()
                print("\nFinal response:")
                output.display()
        print("\n")

if __name__ == "__main__":
    main()
