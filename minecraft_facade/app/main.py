import logging
import time

from config import load_config
from facade import FacadeServer
from ha_client import HAClient
from mqtt_listener import MQTTListener

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def main():

    config = load_config()

    ha = HAClient(config)

    facades = {}

    for facade in config["facades"]:

        slug = facade["name"].lower().replace(" ", "_")

        ha.publish_discovery(facade["name"])
        ha.set_switch_state(slug, True)

        server = FacadeServer(facade, ha)

        server.start()

        facades[slug] = server

        logger.info("Started facade %s", facade["name"])

    MQTTListener(ha, facades)

    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
