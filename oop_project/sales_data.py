class SalesData:
    """Class representing a single sales entry."""

    def __init__(self, store_id, date, total_sales, total_revenue):
        self.store_id = store_id
        self.date = date
        self.total_sales = total_sales
        self.total_revenue = total_revenue

    @classmethod
    def from_dict(cls, data):
        """Create a SalesData object from a dictionary."""
        if not isinstance(data, dict):
            raise ValueError(f"Invalid data type for SalesData: {data}. Expected a dictionary.")
    
        return cls(
            store_id=data.get("store_id"),
            date=data.get("date"),
            total_sales=data.get("total_sales"),
            total_revenue=data.get("total_revenue")
        )

    def to_dict(self):
        """Convert the SalesData object to a dictionary."""
        return {
            "store_id": self.store_id,
            "date": self.date,
            "total_sales": self.total_sales,
            "total_revenue": self.total_revenue
        }

    def __str__(self):
        return f"SalesData(store_id={self.store_id}, date={self.date}, total_sales={self.total_sales}, total_revenue={self.total_revenue})"
