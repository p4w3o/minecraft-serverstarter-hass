import json
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


class MinecraftProtocol:

    def __init__(self, config, ha):
        self.config = config
        self.ha = ha

    def handle(self, conn, addr):

        ip = addr[0]

        try:
            read_varint(conn)
            packet_id = read_varint(conn)

            if packet_id != 0:
                return

            read_varint(conn)

            addr_len = read_varint(conn)
            conn.recv(addr_len)

            conn.recv(2)

            next_state = read_varint(conn)

            if next_state == 1:
                self.status(conn)

            elif next_state == 2:
                self.login(conn, ip)

        except Exception as e:
            logger.debug("Protocol error: %s", e)

        conn.close()

    def status(self, conn):

        read_varint(conn)
        read_varint(conn)

        favicon = self.ha.get_icon_b64(self.config.get("icon"))

        response = {
            "version": {"name": "Facade", "protocol": 9999},
            "players": {"max": 0, "online": 0},
            "description": {"text": self.config.get("motd")}
        }

        if favicon:
            response["favicon"] = favicon

        data = json.dumps(response).encode()

        payload = write_varint(len(data)) + data

        send_packet(conn, 0, payload)

    def login(self, conn, ip):

        read_varint(conn)
        read_varint(conn)

        name_len = read_varint(conn)
        username = conn.recv(name_len).decode()

        logger.info("Join attempt %s (%s)", username, ip)

        self.ha.fire_join_event(
            self.config["name"],
            username,
            ip
        )

        msg = json.dumps({
            "text": self.config.get("kick_message")
        }).encode()

        payload = write_varint(len(msg)) + msg

        send_packet(conn, 0, payload)
