# Réception ESP-NOW
# Format d'un message : 4 octets (float little-endian) + nom de l'émetteur
import network, espnow, struct


class Radio:
    def __init__(self, canal: int = 1):
        self.sta = network.WLAN(network.STA_IF)
        self.sta.active(True)
        self.sta.disconnect()          # avant de changer de canal, sinon erreur Wifi
        self.sta.config(channel=canal)
        self.e = espnow.ESPNow()
        self.e.active(True)

    def mac(self) -> bytes:
        """
        Get current mac adress

        Returns:
            str: MAC adress
        """
        return self.sta.config('mac')

    def messages(self):
        """
        Non blocking messages reading

        Yields:
            tuple: Name, Voltage
        """
        while True:
            _, msg = self.e.recv(0)
            if msg is None:
                return
            if len(msg) <= 4:
                continue
            try:
                nom = msg[4:].decode()
            except ValueError:
                continue
            yield nom, struct.unpack('<f', msg[:4])[0]
