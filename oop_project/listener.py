import redis

class Listener:
    """Listens for messages on a Redis channel."""

    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.pubsub = self.redis_client.pubsub()

    def listen(self, channel):
        """Listen for messages on the given channel."""
        self.pubsub.subscribe(channel)
        print(f"Listening for messages on channel: {channel}")
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                print(f"Received message: {message['data']}")

if __name__ == "__main__":
    listener = Listener()
    listener.listen("completion_channel")
