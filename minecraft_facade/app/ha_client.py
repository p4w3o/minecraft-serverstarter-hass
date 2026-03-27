import os
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
        logger.info("[HAClient] Connecté à Mosquitto")

    def publish_discovery(self, facade_name):
        slug = facade_name.lower().replace(" ", "_")
        topic = f"homeassistant/switch/minecraft_facade_{slug}/config"
        payload = {
            "name": f"Minecraft Facade {facade_name}",
            "unique_id": f"minecraft_facade_{slug}",
            "command_topic": f"minecraft_facade/{slug}/set",
            "state_topic": f"minecraft_facade/{slug}/state",
            "payload_on": "ON",
            "payload_off": "OFF",
            "retain": True,
            "icon": "mdi:minecraft",
            "device": {
                "identifiers": [f"minecraft_facade_{slug}"],
                "name": f"Minecraft Facade {facade_name}",
                "model": "Minecraft Facade",
                "manufacturer": "minecraft-facade-addon"
            }
        }
        self.client.publish(topic, json.dumps(payload), retain=True)
        logger.info(f"[HAClient] Discovery publiée pour {facade_name}")

    def set_switch_state(self, slug, enabled):
        topic = f"minecraft_facade/{slug}/state"
        self.client.publish(topic, "ON" if enabled else "OFF", retain=True)

    def fire_event(self, facade_name, username):
        slug = facade_name.lower().replace(" ", "_")
        topic = f"minecraft_facade/{slug}/join_attempt"
        payload = json.dumps({"username": username, "facade": facade_name})
        self.client.publish(topic, payload)
        logger.info(f"[HAClient] Join attempt fired: {facade_name} by {username}")

    def get_icon_b64(self, path):
        if not path:
            return None
        try:
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode()
                return f"data:image/png;base64,{data}"
        except Exception as e:
            logger.warning(f"[HAClient] Icône introuvable: {path} ({e})")
            return None