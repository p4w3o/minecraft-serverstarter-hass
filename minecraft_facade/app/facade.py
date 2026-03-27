import socket
import threading
import logging
from mc_facade_protocol import MinecraftFacade

logger = logging.getLogger(__name__)


class FacadeServer:

    def __init__(self, config, ha_client):
        self.config = config
        self.ha_client = ha_client
        self.server = None
        self.running = False

    def start(self):
        port = self.config["port"]

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("0.0.0.0", port))
        self.server.listen()

        self.running = True

        threading.Thread(target=self.accept_loop, daemon=True).start()

        logger.info(f"[Facade] '{self.config['name']}' listening on {port}")

    def accept_loop(self):
        protocol = MinecraftFacade(self.config, self.ha_client)

        while self.running:
            conn, addr = self.server.accept()

            threading.Thread(
                target=protocol.handle_client,
                args=(conn, addr),
                daemon=True
            ).start()

    def set_enabled(self, enabled):
        if not enabled and self.running:
            self.running = False
            self.server.close()
