# mc_protocol.py
import logging
from quarry.net.server import ServerFactory, ServerProtocol

logger = logging.getLogger(__name__)

class FacadeProtocol(ServerProtocol):

    def connection_made(self):
        super().connection_made()
        self.session_id = id(self)  # Unique session ID per connection
        logger.info(f"[Protocol] Connection from {self.transport.getPeer().host}, session={self.session_id}")

    def player_joined(self):
        username = self.display_name
        logger.info(f"[Protocol] Join attempt: {username} on port {self.factory.config['port']} session={self.session_id}")
        self.factory.on_join_attempt(username, self.session_id)
        self.close(self.factory.config.get("kick_message", "Server is starting..."))

    def status_response(self):
        return self.factory.build_status()


class FacadeFactory(ServerFactory):
    protocol = FacadeProtocol
    motd = "Minecraft Facade"

    def __init__(self, config, ha_client):
        self.config = config
        self.ha_client = ha_client
        self.sessions = {}  # store per-session data

    def on_join_attempt(self, username, session_id):
        self.sessions[session_id] = {"username": username}
        self.ha_client.fire_event(self.config["name"], username)
        logger.info(f"[Factory] Session {session_id} tracked for user {username}")

    def build_status(self):
        favicon = self.ha_client.get_icon_b64(self.config.get("icon", ""))
        status = {
            "description": {"text": self.config.get("motd", "Minecraft Facade")},
            "players": {"max": 0, "online": 0},
            "version": {"name": "Facade", "protocol": 779},  # latest Minecraft
        }
        if favicon:
            status["favicon"] = favicon
        return status
