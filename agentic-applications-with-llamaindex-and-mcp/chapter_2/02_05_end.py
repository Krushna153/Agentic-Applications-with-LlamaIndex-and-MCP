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
    qa = QueryAgent(
        client=client,
        collections=["ECommerce"]
    )
    print("✓ Query Agent initialized")


    # 1. Use the agent in search mode
    print("\n--- Search results ---")
    search_response = qa.search(
        "Find me some vintage floral dresses under $60",
        limit=3
    )

    # Display results
    print("Search mode query: Find me some vintage floral dresses under $60")
    for obj in search_response.search_results.objects:
        print(f"Name: {obj.properties['name']}")
        print(f"Price: ${obj.properties['price']:.2f}")


    # 2. Use the agent in ask mode
    print("\n--- Ask results ---")
    response = qa.ask(
        "I'm looking for a dress for a summer party. What can you recommend?"
    )

    print("Ask mode query: I'm looking for a dress for a summer party. What can you recommend?")
    print(f"Agent answer: {response.final_answer}")


    # Aggregation queries
    print("\n--- Ask results (aggregation) ---")
    agg_response = qa.ask(
        "How many items do we have in the 'Footwear' category, and what is the average price?"
    )

    print("Ask mode query: How many items do we have in the 'Footwear' category, and what is the average price?")
    print(f"Agent answer: {agg_response.final_answer}")


    # Handling Conversations
    print("\n--- Conversation ---")

    # Initial question
    initial_question = "Recommend some footwear for me."
    initial_response = qa.ask(initial_question)

    print(f"User: {initial_question}")
    print(f"Agent: {initial_response.final_answer}")


    # Build conversation history for the follow-up
    follow_up_question = "Which of those are under $80?"

    conversation = [
        ChatMessage(role="user", content=initial_question),
        ChatMessage(role="assistant", content=initial_response.final_answer),
        ChatMessage(role="user", content=follow_up_question)
    ]
    follow_up = qa.ask(conversation)

    # The agent understands "those" refers to the footwear from the previous turn
    print(f"\nUser: {follow_up_question}")
    print(f"Agent: {follow_up.final_answer}")
