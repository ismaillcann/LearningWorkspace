import os
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import json

# Load environment variables from docker-compose.yml
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "RedDVCLKEOhTjtYYqTIYaJYgxpPwJwRsRGVqlxe0cdSJVEVDXL4SzGCYRxfgZ6COGVkzWF3EAs8Fxvxt5YBLHw==")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "can.ismail")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "sales_bucket")

# Create InfluxDB Client
client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

def write_sales_data(file_path="sales.json"):
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            print(f"✅ Loaded JSON Data: {data}")  # Debugging line


        store_sales = data.get("store_sales_data", [])
        if not store_sales:
            print("❌ No sales data found in the JSON file.")
            return

        for sale in store_sales:
            point = (
                Point("sales_data")
                .tag("store_id", sale["store_id"])
                .field("total_sales", sale["total_sales"])
                .field("total_revenue", sale["total_revenue"])
                .time(sale["date"], WritePrecision.NS)
            )

            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)
            print(f"✅ Data written: {sale}")

    except Exception as e:
        print(f"❌ Error writing to InfluxDB: {e}")

def read_sales_data():
    """Reads sales data from InfluxDB using Flux."""
    query = f'''
    from(bucket: "{INFLUXDB_BUCKET}")
      |> range(start: -30d)
      |> filter(fn: (r) => r._measurement == "sales_data")
    '''
    try:
        tables = query_api.query(query, org=INFLUXDB_ORG)
        for table in tables:
            for record in table.records:
                print(f"📊 Date: {record.get_time()} | Store: {record.values.get('store_id', 'N/A')} | Value: {record.get_value()}")
    except Exception as e:
        print(f"❌ Error reading from InfluxDB: {e}")


        
if __name__ == "__main__":
    print("🔥 Writing sales data to InfluxDB...")
    write_sales_data()

    print("\n📥 Reading sales data form InfluxDB...")
    read_sales_data()
