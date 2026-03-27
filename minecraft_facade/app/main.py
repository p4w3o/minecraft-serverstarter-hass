import logging
from twisted.internet import reactor
from facade import FacadeServer
from ha_client import HAClient
from mqtt_listener import MQTTListener
from config import load_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    config = load_config("/data/options.json")
    ha_client = HAClient(config)

    facades = {}
    for facade_config in config.get("facades", []):
        slug = facade_config["name"].lower().replace(" ", "_")

        # Créer le switch dans HA via MQTT discovery
        ha_client.publish_discovery(facade_config["name"])
        # État initial ON
        ha_client.set_switch_state(slug, True)

        server = FacadeServer(facade_config, ha_client)
        server.start()
        facades[slug] = server

        logger.info(f"[Main] Facade '{facade_config['name']}' démarrée sur port {facade_config['port']}")

    # Écoute les toggles de switch via MQTT
    MQTTListener(ha_client, facades)

    reactor.run()

if __name__ == "__main__":
    main()
