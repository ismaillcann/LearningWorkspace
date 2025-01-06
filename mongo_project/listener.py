import redis

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Subscribe to the completion channel
pubsub = redis_client.pubsub()
completion_channel = "completion_channel"
pubsub.subscribe(completion_channel)

print(f"Listening for messages on channel: {completion_channel}")

# Listen for messages
for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"Received message: {message['data']}")
