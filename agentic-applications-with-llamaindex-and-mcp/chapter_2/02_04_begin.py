#!/usr/bin/env python3
import os
from weaviate.classes.query import MetadataQuery, Filter
from weaviate.auth import AuthApiKey
import weaviate
import dotenv

dotenv.load_dotenv(override=True)

# This script contains all the query examples from Lesson 2.4.
# You can run it to see the output from each type of search.


def main():
    if not all(key in os.environ for key in ["WEAVIATE_URL", "WEAVIATE_API_KEY"]):
        raise ValueError(
            "Please set WEAVIATE_URL and WEAVIATE_API_KEY in your .env file"
        )

    with weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY")),
    ) as client:
        if not client.is_ready():
            raise ConnectionError("Could not connect to Weaviate")

        # Connect to the ECommerce collection
        # TODO: Connect to the ECommerce collection
        # Use the `client.collections.use` method to connect to the ECommerce collection
        collection = None

        if collection:
            print(f"✓ Collection '{collection.name}' is ready.")

        # --- Vector Search ---
        # TODO: Implement the vector search query for "smart pants"
        response = None

        if response:
            print("\n--- 1. Vector Search (by meaning) ---")
            for obj in response.objects:
                print(f"  - {obj.properties['name']}")

        # --- Keyword Search (BM25) ---
        # TODO: Implement the keyword search for "breezy bramble"
        response = None

        if response:
            print("\n--- 2. Keyword Search (by exact terms) ---")
            for obj in response.objects:
                print(f"  - {obj.properties['name']}")

        # --- Hybrid Search ---
        # TODO: Implement the hybrid search for "vintage floral dresses"
        response = None  # Replace this code

        if response:
            print("\n--- 3. Hybrid Search (best of both) ---")
            for obj in response.objects:
                print(f"  - {obj.properties['name']} (Score: {obj.metadata.score:.4f})")

        # --- Hybrid Search with Filter ---
        # TODO: Implement the hybrid search for "vintage floral dresses" with price below 60
        response = None  # Replace this code

        if response:
            print("\n--- 4. Hybrid Search with Filter ---")
            for obj in response.objects:
                print(f"  - {obj.properties['name']} (${obj.properties['price']:.2f})")


if __name__ == "__main__":
    main()
