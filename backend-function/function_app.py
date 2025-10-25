import logging
import json
import os
import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError

# --- Configuration ---
# Name of the Connection String stored in Azure Function App Settings
COSMOS_CONNECTION_STRING_NAME = "CosmosDbConnectionString"
DATABASE_NAME = "ResumeDB" 
CONTAINER_NAME = "Counter"
COUNTER_ID = "1"
# ---------------------

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    # 1. CORS Headers Setup
    # These headers are crucial for your Flask app (running on a different domain) 
    # to be able to call this API.
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",  # Allows any domain to call the API
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    
    # Handle OPTIONS pre-flight request (for CORS)
    if req.method == 'OPTIONS':
        return func.HttpResponse(
            "",
            status_code=204,
            headers=headers
        )
        
    try:
        # 2. Initialize Cosmos Client
        conn_str = os.environ.get(COSMOS_CONNECTION_STRING_NAME)
        if not conn_str:
            raise ValueError("CosmosDbConnectionString not found in environment variables.")

        cosmos_client = CosmosClient.from_connection_string(conn_str=conn_str)
        database = cosmos_client.get_database_client(DATABASE_NAME)
        container = database.get_container_client(CONTAINER_NAME)
    
    except Exception as e:
        logging.error(f"Error initializing Cosmos DB connection: {e}")
        return func.HttpResponse(
             json.dumps({"error": "Database connection failed"}),
             status_code=500,
             headers=headers
        )

    try:
        # 3. Read, Increment, and Update the Counter Document
        
        # Read the existing counter document using its ID and Partition Key
        item_to_read = container.read_item(item=COUNTER_ID, partition_key=COUNTER_ID)
        current_count = item_to_read.get('count', 0) # Use .get with default for safety
        
        # Increment the count
        new_count = current_count + 1
        item_to_read['count'] = new_count
        
        # Update the document in Cosmos DB
        container.replace_item(item=item_to_read, body=item_to_read)
        
        # 4. Return the new count
        return func.HttpResponse(
            json.dumps({"count": new_count}),
            mimetype="application/json",
            status_code=200,
            headers=headers
        )

    except CosmosResourceNotFoundError:
        # Handle case where the initial document ('id: "1"') was not found
        logging.error(f"Counter document with id '{COUNTER_ID}' not found.")
        return func.HttpResponse(
             json.dumps({"error": f"Counter document ID '{COUNTER_ID}' not found in the container."}),
             status_code=404,
             headers=headers
        )
        
    except Exception as e:
        logging.error(f"Unhandled error processing counter: {e}")
        return func.HttpResponse(
             json.dumps({"error": f"Error during counter processing: {e}"}),
             status_code=500,
             headers=headers
        )