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
        raise ValueError("Please set WEAVIATE_URL and WEAVIATE_API_KEY in your .env file")

    with weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL"),
        auth_credentials=AuthApiKey(os.getenv("WEAVIATE_API_KEY"))
    ) as client:
        if not client.is_ready():
            raise ConnectionError("Could not connect to Weaviate")

        # Connect to the ECommerce collection
        collection = client.collections.use("ECommerce")

        print(f"✓ Collection '{collection.name}' is ready.")


        # --- Vector Search ---
        print("\n--- 1. Vector Search (by meaning) ---")
        response = collection.query.near_text(
            query="smart pants",
            limit=2,
        )

        for obj in response.objects:
            print(f"  - {obj.properties['name']}")


        # --- Keyword Search (BM25) ---
        print("\n--- 2. Keyword Search (by exact terms) ---")
        response = collection.query.bm25(
            query="breezy bramble",
            limit=2
        )

        for obj in response.objects:
            print(f"  - {obj.properties['name']}")


        # --- Hybrid Search ---
        print("\n--- 3. Hybrid Search (best of both) ---")
        response = collection.query.hybrid(
            query="vintage floral dresses",
            alpha=0.5,
            limit=3,
            return_metadata=MetadataQuery(score=True)
        )

        for obj in response.objects:
            print(f"  - {obj.properties['name']} (Score: {obj.metadata.score:.4f})")


        # --- Hybrid Search with Filter ---
        print("\n--- 4. Hybrid Search with Filter ---")
        response = collection.query.hybrid(
            query="vintage floral dresses",
            alpha=0.75,
            filters=Filter.by_property("price").less_than(60),
            limit=3
        )

        for obj in response.objects:
            print(f"  - {obj.properties['name']} (${obj.properties['price']:.2f})")

if __name__ == "__main__":
    main()
