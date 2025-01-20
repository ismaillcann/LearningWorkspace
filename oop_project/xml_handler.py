import os
import redis
from pymongo import MongoClient
import xml.etree.ElementTree as ET
from sales_data import SalesData

class XMLHandler:
    """Handles MongoDB data fetching and XML file creation."""

    def __init__(self, redis_host='localhost', redis_port=6379, mongo_uri='mongodb://localhost:27017/'):
        redis_host = os.getenv("REDIS_HOST", redis_host)
        redis_port = int(os.getenv("REDIS_PORT", redis_port))
        mongo_uri = os.getenv("MONGO_URI", mongo_uri)
        
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.mongo_client = MongoClient(mongo_uri)
        self.mongo_db = self.mongo_client['RedisMongoDB']
        self.mongo_collection = self.mongo_db['store_sales']
        self.pubsub = self.redis_client.pubsub()

    def listen_for_completion(self, channel):
        """Listen for the completion message."""
        self.pubsub.subscribe(channel)
        print(f"Listening for messages on channel: {channel}")
        for message in self.pubsub.listen():
            if message['type'] == 'message' and message['data'] == "Processing completed!":
                print("Received completion message. Fetching data from MongoDB.")
                return True

    def fetch_data(self):
        """Fetch all data from MongoDB."""
        data = list(self.mongo_collection.find())
        return [SalesData.from_dict(d) for d in data]

    def convert_to_xml(self, sales_data):
        """Convert sales data to XML."""
        root = ET.Element("store_sales_data")
        for sale in sales_data:
            store = ET.SubElement(root, "store")
            for key, value in sale.to_dict().items():
                if key == "_id":
                    continue
                field = ET.SubElement(store, key)
                field.text = str(value)
        return ET.ElementTree(root)

    def save_to_file(self, xml_tree, filename):
        """Save XML tree to file."""
        xml_tree.write(filename, encoding="utf-8", xml_declaration=True)
        print(f"XML data saved to {filename}")

if __name__ == "__main__":
    handler = XMLHandler()
    if handler.listen_for_completion("completion_channel"):
        data = handler.fetch_data()
        if data:
            xml_tree = handler.convert_to_xml(data)
            handler.save_to_file(xml_tree, "output.xml")
        else:
            print("No data found in MongoDB.")
