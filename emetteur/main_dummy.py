# Émetteur ESP-NOW de TEST : envoie une tension factice (pas encore de sonde)
# À copier sur l'ESP32 émetteur sous le nom main.py
# Même format que le vrai main.py : 4 octets (humidité, float) + nom
import network, espnow, struct, time, random

NOM = "Test"                        # nom affiché sur le LCD (16 caractères max, sans accents)
PEER = b'\xec\xe34E\xe7\xe0'  # MAC du récepteur (affichée par son main.py)
CANAL = 1                           # même canal que le récepteur
SEC, MOUILLE = 2.6, 1.2             # même calibration que le vrai émetteur (en V)
PERIODE_MS = 10_000                 # un envoi toutes les 10 s (pas de deep sleep -> REPL accessible)

# Radio
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.disconnect()                    # avant de changer de canal, sinon erreur Wifi
sta.config(channel=CANAL)
e = espnow.ESPNow()
e.active(True)
e.add_peer(PEER)

while True:
    # 1. Tension factice entre MOUILLE et SEC, convertie comme le vrai émetteur
    tension = MOUILLE + (SEC - MOUILLE) * random.getrandbits(16) / 65535
    humidite = max(0, min(100, (SEC - tension) / (SEC - MOUILLE) * 100))

    # 2. Envoi ESP-NOW
    payload = struct.pack('<f', humidite) + NOM.encode()
    ok = False
    for _ in range(3):              # 3 tentatives max
        if e.send(PEER, payload):   # True = accusé de réception reçu
            ok = True
            break
        time.sleep_ms(50)
    print("%.2f V -> %d %% : %s" % (tension, humidite, "OK" if ok else "ECHEC"))

    time.sleep_ms(PERIODE_MS)
