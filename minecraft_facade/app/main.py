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
    for idx, facade_config in enumerate(config.get("facades", [])):
        slug = facade_config["name"].lower().replace(" ", "_")
        ha_client.publish_discovery(facade_config["name"])
        ha_client.set_switch_state(slug, True)

        server = FacadeServer(facade_config, ha_client)
        server.start()
        facades[slug] = server
        logger.info(f"[Main] Facade '{facade_config['name']}' started with session {idx}")


    # Écoute les toggles de switch via MQTT
    MQTTListener(ha_client, facades)

    reactor.run()

if __name__ == "__main__":
    main()
