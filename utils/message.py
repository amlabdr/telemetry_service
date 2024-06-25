import hashlib

class Message:
    def __init__(self, message_body) -> None:
        self.message_body = message_body

    def calculate_capability_id(self):
        endpoint = self.message_body["endpoint"]
        capability_name = self.message_body["capabilityName"]
        combined_string = f"{endpoint}{capability_name}"
        capability_id =hashlib.sha256(combined_string.encode()).hexdigest()
        return capability_id