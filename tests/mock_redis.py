class MockRedis:
    def __init__(self):
        self.channels = {}

    def publish(self, channel, message):
        if channel in self.channels:
            for callback in self.channels[channel]:
                callback({'type': 'message', 'data': message})

    def pubsub(self):
        return self

    def subscribe(self, **kwargs):
        for channel, callback in kwargs.items():
            if channel not in self.channels:
                self.channels[channel] = []
            self.channels[channel].append(callback)

    def get_message(self, *args, **kwargs):
        return None
