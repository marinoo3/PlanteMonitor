# Émetteur ESP-NOW sur pile : mesure -> envoi -> deep sleep 24 h
# À copier sur l'ESP32 émetteur sous le nom main.py
import network, espnow, machine, struct, time
from machine import Pin, ADC

NOM = "Tomates"                     # nom affiché sur le LCD (16 caractères max, sans accents)
PEER = b'\xec\xe34E\xe7\xe0'  # MAC du récepteur (affichée par son main.py)
CANAL = 1                           # même canal que le récepteur
FACTEUR_PONT = 1.0                  # sonde branchée directement (pas de pont)
SEC, MOUILLE = 2.6, 1.2             # calibration la sonde (en V)
DODO_MS = 24 * 3600 * 1000

# Sécurité dev : relier GPIO13 à GND pour garder la carte éveillée (REPL)
if Pin(13, Pin.IN, Pin.PULL_UP).value() == 0:
    raise SystemExit

# 1. Mesure AVANT d'activer la radio (ADC1 uniquement : GPIO 32-39)
alim_sonde = Pin(25, Pin.OUT, value=1)   # alimente le pont diviseur
time.sleep_ms(300)                       # stabilisation du capteur
adc = ADC(Pin(34))
adc.atten(ADC.ATTN_11DB)                 # plage ~0-3,1 V
uv = sum(adc.read_uv() for _ in range(8)) // 8   # moyenne, en µV calibrés
alim_sonde.value(0)
tension = uv / 1_000_000 * FACTEUR_PONT
humidite = max(0, min(100, (SEC - tension) / (SEC - MOUILLE) * 100))

# 2. Envoi ESP-NOW
sta = network.WLAN(network.STA_IF)
sta.active(True)
sta.config(channel=CANAL)
e = espnow.ESPNow()
e.active(True)
e.add_peer(PEER)

payload = struct.pack('<f', humidite) + NOM.encode()   # 4 octets + nom
for _ in range(3):                       # 3 tentatives max
    if e.send(PEER, payload):            # True = accusé de réception reçu
        break
    time.sleep_ms(50)

# 3. Tout couper et dormir
e.active(False)
sta.active(False)
machine.deepsleep(DODO_MS)