import logging
from mc_protocol import FacadeFactory
from twisted.internet import reactor

logger = logging.getLogger(__name__)

class FacadeServer:
    def __init__(self, config, ha_client):
        self.config = config
        self.ha_client = ha_client
        self.factory = FacadeFactory(config, ha_client)
        self.port_listener = None

    def start(self):
        self._listen()

    def _listen(self):
        port = self.config["port"]
        self.port_listener = reactor.listenTCP(port, self.factory)
        logger.info(f"[Facade] '{self.config['name']}' écoute sur port {port}")

    def set_enabled(self, enabled):
        if enabled and self.port_listener is None:
            self._listen()
        elif not enabled and self.port_listener is not None:
            self.port_listener.stopListening()
            self.port_listener = None
            logger.info(f"[Facade] '{self.config['name']}' port libéré")