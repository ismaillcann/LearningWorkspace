# Base image 
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Default working 
CMD ["python", "listener.py"]
