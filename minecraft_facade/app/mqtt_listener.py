import logging

logger = logging.getLogger(__name__)


class MQTTListener:

    def __init__(self, ha, facades):

        self.ha = ha
        self.facades = facades

        self.ha.client.on_message = self.on_message

        for slug in facades:
            topic = f"minecraft_facade/{slug}/set"

            self.ha.client.subscribe(topic)

            logger.info("MQTT subscribe %s", topic)

    def on_message(self, client, userdata, msg):

        payload = msg.payload.decode()

        slug = msg.topic.split("/")[1]

        enabled = payload == "ON"

        if slug in self.facades:

            logger.info("Switch %s -> %s", slug, payload)

            self.facades[slug].set_enabled(enabled)

            self.ha.set_switch_state(slug, enabled)
