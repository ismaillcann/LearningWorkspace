import redis
import json
from pymongo import MongoClient
import time

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Connect to MongoDB
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['RedisMongoDB']
mongo_collection = mongo_db['store_sales']

# Load sales data from JSON file
with open("sales.json", "r") as file:
    sales_data = json.load(file)["store_sales_data"]

# Define Redis channels
cache_channel = "sales_channel"
completion_channel = "completion_channel"

# Process and store data
for sale in sales_data:
    # Convert data to JSON format
    sale_message = json.dumps(sale)

    # Write to Redis cache
    redis_client.hset("store_totals", sale["store_id"], sale["total_sales"])
    print(f"Cached to Redis: {sale}")

    # Write to MongoDB
    mongo_collection.insert_one(sale)
    print(f"Stored to MongoDB: {sale}")

    # Publish message to Redis channel
    redis_client.publish(cache_channel, sale_message)
    print(f"Published to Redis channel: {cache_channel}")

    # Simulate processing delay
    time.sleep(1)

# Send completion message
redis_client.publish(completion_channel, "Processing completed!")
print(f"Published 'Processing completed!' to {completion_channel}")
