import os
import redis
from pymongo import MongoClient
import json
from sales_data import SalesData

class Publisher:
    """Handles publishing sales data to Redis and storing in MongoDB."""

    def __init__(self, redis_host='localhost', redis_port=6379, mongo_uri='mongodb://localhost:27017/'):

        redis_host = os.getenv("REDIS_HOST", redis_host)
        redis_port = int(os.getenv("REDIS_PORT", redis_port))
        mongo_uri = os.getenv("MONGO_URI", mongo_uri)

        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.mongo_client = MongoClient(mongo_uri)
        self.mongo_db = self.mongo_client['RedisMongoDB']
        self.mongo_collection = self.mongo_db['store_sales']

    def publish_sales(self, sales_file, channel):
        """Publish sales data from a JSON file to Redis and MongoDB."""
        try:
            with open(sales_file, 'r') as file:
                sales_data = json.load(file)
                print(f"Loaded sales data: {sales_data}")
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            return

        store_sales = sales_data.get("store_sales_data", [])
        if not store_sales:
            print("No valid sales data found in the JSON file.")
            return

        for sale in store_sales:
            if not isinstance(sale, dict):
                print(f"Unexpected data format: {sale}. Skipping...")
                continue

            sales_obj = SalesData.from_dict(sale)

            # Publish to Redis
            self.redis_client.publish(channel, json.dumps(sales_obj.to_dict()))
            print(f"Published to Redis: {sales_obj}")

            # Store in MongoDB
            self.mongo_collection.insert_one(sales_obj.to_dict())
            print(f"Stored to MongoDB: {sales_obj}")

        # Notify completion
        self.redis_client.publish("completion_channel", "Processing completed!")
        print("Published completion message to Redis.")

if __name__ == "__main__":
    publisher = Publisher()
    publisher.publish_sales("sales.json", "sales_channel")
