import asyncio, time
import threading
from proton import Message
from proton.handlers import MessagingHandler
from proton.reactor import Container
import json
from utils.message import Message
import logging
from protocols.amqp.receive import Receiver
from protocols.amqp.send import Sender


# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the desired logging level

from config.config import BROKER_URL, CAPABILITY_TIMEOUT, CLEANUP_INTERVAL

class CapabilitiesManager:
    def __init__(self, timeout, cleanup_interval):
        self.capabilities = {}
        self.last_update = {}
        self.timeout = timeout
        self.cleanup_interval = cleanup_interval
        self.lock = threading.Lock()
        
        # Start the thread to periodically remove stale capabilities
        self.cleanup_thread = threading.Thread(target=self._run_cleanup, daemon=True)
        self.cleanup_thread.start()

    def add_capability(self, capability_id, capability_msg):        
        with self.lock:
            if capability_id not in self.capabilities:
                self.capabilities[capability_id] = {}

            # Add the capability to the dictionary using its ID
            self.capabilities[capability_id] = capability_msg
            
            # Update the last update time
            self.last_update[capability_id] = time.time()

    def remove_stale_capabilities(self):
        current_time = time.time()
        ids_to_remove = []
        
        with self.lock:
            for endpoint, last_time in self.last_update.items():
                if current_time - last_time > self.timeout:
                    ids_to_remove.append(endpoint)
            
            for endpoint in ids_to_remove:
                del self.capabilities[endpoint]
                del self.last_update[endpoint]

    def _run_cleanup(self):
        while True:
            self.remove_stale_capabilities()
            time.sleep(self.cleanup_interval)


    def get_capability(self, capability_id):
        return self.capabilities.get(capability_id)



class Broker(MessagingHandler):
    def __init__(self, url):
        super(Broker, self).__init__()
        self.url = url
        self.capability_manager = CapabilitiesManager(CAPABILITY_TIMEOUT, CLEANUP_INTERVAL)
        self.sender = Sender()
    def on_start(self, event):
        conn = event.container.connect(self.url)
        self.receiver_capabilities = event.container.create_receiver(conn, "topic:///capabilities")
        self.receiver_specifications = event.container.create_receiver(conn, "topic:///specifications")
        self.receiver_get_capabilities = event.container.create_receiver(conn, "topic:///get_capabilities")
    
    def on_message(self, event):
        try:
            reply_to = event.message.reply_to
            message =Message(json.loads(event.message.body))
            print("got msg " , message)
            
            if event.receiver == self.receiver_capabilities:
                capability_id = message.calculate_capability_id()
                capability = message.message_body
                logging.info(f"recived capability: {capability}")
                self.capability_manager.add_capability(capability_id, capability)
            elif event.receiver == self.receiver_specifications:
                spec_endpoint = message.message_body["endpoint"]
                target_topic = f'topic://{spec_endpoint}/specifications'
                print(message.message_body)
                self.sender.send(self.url, topic = target_topic, messages= message.message_body, reply_to=reply_to)
                logging.info(f"Redirected specification to {target_topic}: {message.message_body}")
            elif event.receiver == self.receiver_get_capabilities:
                target_topic = event.message.reply_to
                self.sender.send(self.url, topic = target_topic, messages= self.capability_manager.capabilities)
        except Exception as e:
            logging.error(f"Error processing message: {e}")
    def send_message(self, data, topic):
        class Sender(MessagingHandler):
            def __init__(self, url, topic, message):
                super(Sender, self).__init__()
                self.url = url
                self.message = message
                self.target_topic = topic

            def on_start(self, event):
                self.conn = event.container.connect(self.url)
                self.sender = event.container.create_sender(self.conn, self.target_topic)

            def on_sendable(self, event):
                if event.sender.credit:
                    event.sender.send(self.message)
                    event.sender.close()
                    event.connection.close()

            def on_transport_error(self, event):
                print("Transport error: ", event.transport.condition)
                event.connection.close()

            def on_connection_error(self, event):
                print("Connection error: ", event.connection.condition)
                event.connection.close()

            def on_session_error(self, event):
                print("Session error: ", event.session.condition)
                event.connection.close()

            def on_link_error(self, event):
                print("Link error: ", event.link.condition)
                event.connection.close()
        Container(Sender(self.url, topic, data)).run()
        
    


def start_amqp_broker():
    Container(Broker(BROKER_URL)).run()

if __name__ == '__main__':
    start_amqp_broker()
    print("Done")
