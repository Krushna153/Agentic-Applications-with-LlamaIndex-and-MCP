#!/usr/bin/env python3
import os
import weaviate
from weaviate.agents.query import QueryAgent
from weaviate.agents.classes import ChatMessage
from weaviate.auth import AuthApiKey
import dotenv

dotenv.load_dotenv(override=True)

# Connect to Weaviate Cloud
with weaviate.connect_to_weaviate_cloud(
    cluster_url=os.getenv("WEAVIATE_URL"),
    auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
) as client:
    # TODO: Instantiate the agent
    qa = None
    print("✓ Query Agent initialized")

    # TODO: 1. Use the agent in search mode
    # Follow the lesson to use the QueryAgent in `search` mode to find
    # "vintage floral dresses under $60".
    print("\n--- Search results ---")
    search_response = None  # Replace this code

    # Display results
    if search_response:
        for obj in search_response.search_results.objects:
            print(f"Name: {obj.properties['name']}")
            print(f"Price: ${obj.properties['price']:.2f}")

    print("\n--- Ask results ---")
    # TODO: 2. Use the agent in ask mode
    # Follow the lesson to use the QueryAgent in `ask` mode to recommend
    # a "dress for a summer party".
    response = None  # Replace this code

    if response:
        print(response.final_answer)

    # TODO: 3. Use the agent in a conversation
    print("\n--- Conversation ---")

    # Follow the lesson to have a two-step conversation with the agent.
    # First, ask for footwear recommendation
    initial_question = "Recommend some footwear for me."
    initial_response = None  # Replace this code

    if initial_response:
        print(f"User: {initial_question}")
        print(f"Agent: {initial_response.final_answer}")

    # TODO: Then, ask which of those are under $80
    follow_up_question = "Which of those are under $80?"

    follow_up = None  # Replace this code

    if follow_up:
        print(f"\nUser: {follow_up_question}")
        print(f"Agent: {follow_up.final_answer}")
