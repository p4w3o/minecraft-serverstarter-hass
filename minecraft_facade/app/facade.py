import socket
import threading
import logging
from mc_protocol import MinecraftProtocol

logger = logging.getLogger(__name__)


class FacadeServer:

    def start(self):
        port = self.config["port"]

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen()
        self.sock.settimeout(0.5)  # timeout pour exit rapide

        self.running = True

        threading.Thread(target=self.loop, daemon=True).start()

        logger.info(f"Facade '{self.config['name']}' listening on {port}")

    def loop(self):
        proto = MinecraftProtocol(self.config, self.ha)

        while self.running:
            try:
                conn, addr = self.sock.accept()
            except socket.timeout:
                continue
            except OSError:
                break  # socket fermé

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
