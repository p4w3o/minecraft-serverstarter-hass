import socket
import threading
import logging
from mc_protocol import MinecraftProtocol

logger = logging.getLogger(__name__)


class FacadeServer:

    def __init__(self, config, ha):
        self.config = config
        self.ha = ha
        self.running = False

    def start(self):

        port = self.config["port"]

        self.sock = socket.socket()
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen()

        self.running = True

        threading.Thread(target=self.loop, daemon=True).start()

        logger.info("Facade '%s' listening on %s",
                    self.config["name"], port)

    def loop(self):

        proto = MinecraftProtocol(self.config, self.ha)

        while self.running:

            conn, addr = self.sock.accept()

            threading.Thread(
                target=proto.handle,
                args=(conn, addr),
                daemon=True
            ).start()

    def set_enabled(self, enabled):

        if enabled and not self.running:
            self.start()

        elif not enabled and self.running:
            self.running = False
            self.sock.close()
