import logging
from quarry.net.server import ServerFactory, ServerProtocol

logger = logging.getLogger(__name__)

class FacadeProtocol(ServerProtocol):

    def player_joined(self):
        # Tentative de login → kick + fire event HA
        username = self.display_name
        logger.info(f"[Protocol] Join attempt: {username} on port {self.factory.config['port']}")
        self.factory.on_join_attempt(username)
        self.close(self.factory.config.get("kick_message", "Server is starting..."))

    def status_response(self):
        return self.factory.build_status()


class FacadeFactory(ServerFactory):
    protocol = FacadeProtocol
    motd = "Minecraft Facade"

    def __init__(self, config, ha_client):
        self.config = config
        self.ha_client = ha_client

    def on_join_attempt(self, username):
        self.ha_client.fire_event(self.config["name"], username)

    def build_status(self):
        favicon = self.ha_client.get_icon_b64(self.config.get("icon", ""))
        status = {
            "description": {"text": self.config.get("motd", "Minecraft Facade")},
            "players": {"max": 0, "online": 0},
            "version": {"name": "Facade", "protocol": 764},
        }
        if favicon:
            status["favicon"] = favicon
        return status