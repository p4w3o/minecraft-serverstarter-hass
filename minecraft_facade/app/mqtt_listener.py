import logging
from twisted.internet import reactor

logger = logging.getLogger(__name__)

class MQTTListener:
    def __init__(self, ha_client, facades: dict):
        self.facades = facades
        self.ha_client = ha_client

        self.ha_client.client.on_message = self._on_message

        for slug in facades:
            topic = f"minecraft_facade/{slug}/set"
            self.ha_client.client.subscribe(topic)
            logger.info(f"[MQTT] Subscribe: {topic}")

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode()

        # "minecraft_facade/survie/set" → "survie"
        parts = topic.split("/")
        if len(parts) != 3:
            return

        slug = parts[1]
        enabled = payload == "ON"

        if slug in self.facades:
            logger.info(f"[MQTT] Switch {slug} → {payload}")
            # Thread-safe : on appelle Twisted depuis le thread MQTT
            reactor.callFromThread(self.facades[slug].set_enabled, enabled)
            self.ha_client.set_switch_state(slug, enabled)
