import os
from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

dataset_id = os.environ.get("BQ_DATASET", "experiments-435323.marketing")
table_id = os.environ.get("BQ_TABLE_PROFILES", "user_profiles")

client = bigquery.Client()
table_ref = f"{dataset_id}.{table_id}"

# Define the schema
schema = [
    bigquery.SchemaField("user_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("interests", "STRING", mode="REPEATED"),
    bigquery.SchemaField("preferred_budget", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("accessibility_needs", "STRING", mode="REPEATED"),
    bigquery.SchemaField("dietary_restrictions", "STRING", mode="REPEATED"),
    bigquery.SchemaField("party_size", "INTEGER", mode="REQUIRED"),
]

table = bigquery.Table(table_ref, schema=schema)

print(f"Creating table {table_ref}...")
try:
    table = client.create_table(table)  # Make an API request.
    print(f"Created table {table.project}.{table.dataset_id}.{table.table_id}")
except Exception as e:
    print(f"Table might already exist or error occurred: {e}")

# Insert mock data
rows_to_insert = [
    {
        "user_id": "user_123",
        "interests": ["science", "museums", "vegan food"],
        "preferred_budget": "$$",
        "accessibility_needs": [],
        "dietary_restrictions": ["vegan"],
        "party_size": 4
    },
    {
        "user_id": "user_456",
        "interests": ["nightlife", "luxury dining", "art galleries"],
        "preferred_budget": "$$$$",
        "accessibility_needs": [],
        "dietary_restrictions": [],
        "party_size": 2
    },
    {
        "user_id": "user_789",
        "interests": ["hiking", "parks", "outdoors"],
        "preferred_budget": "$",
        "accessibility_needs": ["wheelchair accessible"],
        "dietary_restrictions": ["gluten-free"],
        "party_size": 3
    }
]

print("Inserting mock data...")
errors = client.insert_rows_json(table_ref, rows_to_insert)
if errors == []:
    print("New rows have been added.")
else:
    print(f"Encountered errors while inserting rows: {errors}")
