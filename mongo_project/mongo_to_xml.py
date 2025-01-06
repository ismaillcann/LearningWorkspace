import redis
from pymongo import MongoClient
import xml.etree.ElementTree as ET

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
mongo_client = MongoClient('mongodb://localhost:27017/')
mongo_db = mongo_client['RedisMongoDB']
mongo_collection = mongo_db['store_sales']

pubsub = redis_client.pubsub()
completion_channel = "completion_channel"
pubsub.subscribe(completion_channel)

print(f"Listening for messages on channel: {completion_channel}")

def fetch_data_from_mongo():
    """Fetch all data from the MongoDB collection."""
    return list(mongo_collection.find())

def convert_to_xml(data):
    """Convert MongoDB data to XML format."""
    root = ET.Element("store_sales_data")

    for entry in data:
        store = ET.SubElement(root, "store")
        for key, value in entry.items():
            # Skip the MongoDB-specific '_id' field
            if key == "_id":
                continue
            field = ET.SubElement(store, key)
            field.text = str(value)

    return ET.ElementTree(root)

def save_to_file(tree, filename):
    """Save the XML tree to a file."""
    tree.write(filename, encoding="utf-8", xml_declaration=True)
    print(f"Data saved to {filename}")

for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"Received message: {message['data']}")
        if message['data'] == "Processing completed!":
            # Fetch data from MongoDB
            data = fetch_data_from_mongo()
            print("Fetched data from MongoDB:", data)

            # Convert data to XML
            xml_tree = convert_to_xml(data)

            # Save XML to file
            save_to_file(xml_tree, "output.xml")

            print("Process completed.")
            break
