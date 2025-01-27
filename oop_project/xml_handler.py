import os
import redis
from pymongo import MongoClient
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from itertools import groupby
from sales_data import SalesData

class XMLHandler:
    """Handles MongoDB data fetching and PDF report creation."""

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

    def generate_pdf_report(self, data, output_file="report.pdf"):
        """Generate a PDF report with sales data and charts."""
        pdf = SimpleDocTemplate(output_file, pagesize=letter)
        elements = []

        # Add title
        styles = getSampleStyleSheet()
        elements.append(Paragraph("Store Sales Report", styles['Title']))

        # Prepare data summary for tables
        summary_data = [("Store ID", "Min Sales", "Max Sales", "Total Revenue")]
        grouped_data = sorted(data, key=lambda x: x.store_id)
        for store_id, group in groupby(grouped_data, key=lambda x: x.store_id):
            group_list = list(group)
            sales = [d.total_sales for d in group_list]
            revenue = sum([d.total_revenue for d in group_list])
            summary_data.append([store_id, min(sales), max(sales), revenue])

        # Add table to PDF
        table = Table(summary_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)

        # Generate and embed chart
        chart_file = "sales_chart.png"
        self.create_chart(data, chart_file)
        elements.append(Image(chart_file, width=400, height=300))

        # Build the PDF
        pdf.build(elements)
        print(f"PDF report saved as {output_file}")

    def create_chart(self, data, chart_file):
        """Create a bar chart for total revenue over time."""
        dates = sorted(list(set([d.date for d in data])))
        total_revenue = [sum([d.total_revenue for d in data if d.date == date]) for date in dates]

        plt.figure(figsize=(10, 6))
        plt.bar(dates, total_revenue, color='blue')
        plt.title("Total Revenue Over Time")
        plt.xlabel("Date")
        plt.ylabel("Total Revenue")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(chart_file)
        plt.close()
        print(f"Chart saved as {chart_file}")

if __name__ == "__main__":
    handler = XMLHandler()
    if handler.listen_for_completion("completion_channel"):
        data = handler.fetch_data()
        if data:
            handler.generate_pdf_report(data, "sales_report.pdf")
        else:
            print("No data found in MongoDB.")
