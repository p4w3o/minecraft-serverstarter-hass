import json
import base64
import logging
import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class HAClient:

    def __init__(self, config):
        self.client = mqtt.Client()

        self.client.username_pw_set(
            config["mqtt_user"],
            config["mqtt_password"]
        )

        self.client.connect("core-mosquitto", 1883, 60)
        self.client.loop_start()

        logger.info("[HA] Connected to Mosquitto")

    def publish_discovery(self, name):
        slug = name.lower().replace(" ", "_")

        topic = f"homeassistant/switch/minecraft_facade_{slug}/config"

        payload = {
            "name": f"Minecraft Facade {name}",
            "unique_id": f"minecraft_facade_{slug}",
            "command_topic": f"minecraft_facade/{slug}/set",
            "state_topic": f"minecraft_facade/{slug}/state",
            "payload_on": "ON",
            "payload_off": "OFF",
            "icon": "mdi:minecraft"
        }

        self.client.publish(topic, json.dumps(payload), retain=True)

    def set_switch_state(self, slug, state):
        topic = f"minecraft_facade/{slug}/state"
        self.client.publish(topic, "ON" if state else "OFF", retain=True)

    def fire_join_event(self, facade, username, ip):
        slug = facade.lower().replace(" ", "_")

        topic = f"minecraft_facade/{slug}/join_attempt"

        payload = {
            "username": username,
            "ip": ip,
            "facade": facade
        }

        self.client.publish(topic, json.dumps(payload))
        logger.info(f"[MQTT] Published join event: {topic} {payload}")

    def get_icon_b64(self, path):
        if not path:
            return None

        try:
            with open(path, "rb") as f:
                return "data:image/png;base64," + base64.b64encode(f.read()).decode()

        except Exception:
            logger.warning("Icon not found: %s", path)
            return None
