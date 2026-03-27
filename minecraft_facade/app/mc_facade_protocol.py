import socket
import json
import struct
import logging

logger = logging.getLogger(__name__)


def read_varint(sock):
    num = 0
    shift = 0

    while True:
        b = sock.recv(1)
        if not b:
            return None

        val = b[0]
        num |= (val & 0x7F) << shift

        if not val & 0x80:
            break

        shift += 7

    return num


def write_varint(value):
    out = bytearray()

    while True:
        b = value & 0x7F
        value >>= 7

        if value:
            out.append(b | 0x80)
        else:
            out.append(b)
            break

    return bytes(out)


def send_packet(sock, packet_id, payload):
    data = write_varint(packet_id) + payload
    length = write_varint(len(data))
    sock.send(length + data)


class MinecraftFacade:

    def __init__(self, config, ha_client):
        self.config = config
        self.ha_client = ha_client

    def handle_client(self, conn, addr):
        ip = addr[0]
        logger.info(f"[Facade] Connection from {ip}")

        try:
            read_varint(conn)  # packet length
            packet_id = read_varint(conn)

            if packet_id != 0:
                conn.close()
                return

            protocol = read_varint(conn)

            addr_len = read_varint(conn)
            conn.recv(addr_len)

            conn.recv(2)  # port
            next_state = read_varint(conn)

            if next_state == 1:
                self.handle_status(conn)

            elif next_state == 2:
                self.handle_login(conn, ip)

        except Exception as e:
            logger.warning(f"[Facade] error: {e}")

        conn.close()

    def handle_status(self, conn):
        read_varint(conn)
        read_varint(conn)

        favicon = self.ha_client.get_icon_b64(self.config.get("icon", ""))

        status = {
            "version": {"name": "Facade", "protocol": 9999},
            "players": {"max": 0, "online": 0},
            "description": {"text": self.config.get("motd", "Minecraft Facade")},
        }

        if favicon:
            status["favicon"] = favicon

        data = json.dumps(status).encode()

        payload = write_varint(len(data)) + data
        send_packet(conn, 0, payload)

    def handle_login(self, conn, ip):
        read_varint(conn)
        read_varint(conn)

        name_len = read_varint(conn)
        username = conn.recv(name_len).decode()

        logger.info(f"[Facade] Join attempt: {username} from {ip}")

        self.ha_client.fire_event(self.config["name"], username)

        msg = json.dumps({
            "text": self.config.get("kick_message", "Server starting")
        }).encode()

        payload = write_varint(len(msg)) + msg
        send_packet(conn, 0, payload)
