#!/usr/bin/env python3
"""
Lesson 2.3: Set up Weaviate & add data
Complete script combining all code examples from the lesson text.

Prerequisites:
1. Create a Weaviate Cloud sandbox cluster at console.weaviate.cloud
2. Copy .env.example to .env and fill in your credentials:
   - WEAVIATE_URL=https://your-cluster-name.weaviate.cloud
   - WEAVIATE_API_KEY=your-admin-api-key-here
3. Install dependencies:
   pip install -U weaviate-client datasets
"""

import os
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery
from datasets import load_dataset
from weaviate.collections.collection import Collection
import dotenv

dotenv.load_dotenv(override=True)

# Best practice:
# This check prevents accidental credential exposure.
if not all(key in os.environ for key in ["WEAVIATE_URL", "WEAVIATE_API_KEY"]):
    raise ValueError(
        "Missing WEAVIATE_URL or WEAVIATE_API_KEY environment variables."
        "Please create a .env file with your Weaviate Cloud credentials."
    )


def connect_to_weaviate() -> weaviate.WeaviateClient:
    """Connect to Weaviate Cloud using environment variables."""
    client = weaviate.connect_to_weaviate_cloud(
        cluster_url=os.getenv("WEAVIATE_URL", ""),
        auth_credentials=os.getenv("WEAVIATE_API_KEY", "")
    )

    if not client.is_ready():
        raise ConnectionError("Failed to connect to Weaviate Cloud")
    print("✓ Connected to Weaviate Cloud!")
    return client


def create_ecommerce_collection(client: weaviate.WeaviateClient) -> Collection:
    """
    Create the ECommerce collection with the full schema from the lesson.
    Deletes the collection if it already exists for a clean run.
    """
    collection_name = "ECommerce"
    if client.collections.exists(collection_name):
        client.collections.delete(collection_name)
        print(f"ℹ Deleted existing '{collection_name}' collection.")

    collection = client.collections.create(
        name=collection_name,
        description="A dataset of clothing items.",
        properties=[
            Property(name="category", data_type=DataType.TEXT),
            Property(name="name", data_type=DataType.TEXT),
            Property(name="description", data_type=DataType.TEXT),
            Property(name="brand", data_type=DataType.TEXT),
            Property(name="colors", data_type=DataType.TEXT_ARRAY),
            Property(name="price", data_type=DataType.NUMBER, description="The price of the clothing item in USD"),
            Property(name="tags", data_type=DataType.TEXT_ARRAY),
        ],
        vector_config=[
            Configure.Vectors.text2vec_weaviate(
                name="default",
                source_properties=["name", "description", "brand"],
            ),
        ]
    )

    print(f"✓ Collection '{collection.name}' created successfully!")
    return collection


def import_data(collection: Collection):
    """
    Load the e-commerce dataset from Hugging Face and import it
    into the specified Weaviate collection using batching.
    """
    print("\n[Step 2/3] Importing data from Hugging Face...")
    ecommerce_dataset = load_dataset(
        "weaviate/agents", "query-agent-ecommerce", split="train"
    )

    with collection.batch.fixed_size(100) as batch:
        for item in ecommerce_dataset:
            batch.add_object(properties=item["properties"])

    if collection.batch.failed_objects:
        print(f"⚠ Failed to import {len(collection.batch.failed_objects)} objects.")
        for failure in collection.batch.failed_objects[:3]:
            print(f"  - Error for object UUID {failure.original_uuid}: {failure.message}")
    else:
        print("✓ Data imported successfully!")


def verify_data(collection: Collection):
    """
    Verify the imported data with three checks:
    1. Count objects
    2. Inspect a sample object
    3. Test vector search
    """
    print("\n[Step 3/3] Verifying data...")

    # 1. Count the total number of objects.
    total_count = len(collection.query.fetch_objects().objects)

    print(f"✓ 1. Total objects in collection: {total_count}")
    assert total_count > 0


    # 2. Fetch and inspect a sample object.
    response = collection.query.fetch_objects(limit=1)
    sample = response.objects[0]
    print(f"✓ 2. Sample object: {sample.properties['name']} by {sample.properties['brand']}")
    assert "brand" in sample.properties and "name" in sample.properties


    # 3. Test vector search
    response = collection.query.near_text(
        query="vintage shoes",
        limit=1,
        return_metadata=MetadataQuery(distance=True)
    )

    search_result = response.objects[0]
    distance = search_result.metadata.distance
    print(f"✓ 3. Vector search for 'vintage shoes' returned '{search_result.properties['name']}' (distance: {distance:.4f})")
    assert distance < 0.5

    print("\n✓ All verifications passed!")


def main():
    """Main execution flow."""
    print("=" * 60)
    print("Lesson 2.3: Set up Weaviate & add data")
    print("=" * 60)

    try:
        with connect_to_weaviate() as client:
            print("\n[Step 1/3] Creating ECommerce collection...")
            collection = create_ecommerce_collection(client)
            import_data(collection)
            verify_data(collection)

        print("\n🎉 You now have a working Weaviate instance with the e-commerce dataset.")
    except (ValueError, ConnectionError, weaviate.exceptions.WeaviateQueryError) as e:
        print(f"\nAn error occurred:\n{e}")
    finally:
        print("=" * 60)


if __name__ == "__main__":
    main()
