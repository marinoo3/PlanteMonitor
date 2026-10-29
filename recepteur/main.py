# Récepteur ESP-NOW + LCD I2C 20x4 + bouton
# Copier sur l'ESP32 : main.py, radio.py, history.py, display.py, button.py
# et lib/ (lcd_api.py, i2c_lcd.py du dépôt GitHub dhylands/python_lcd)
import time
from machine import I2C, Pin
from radio import Radio
from history import History
from display import Display
from button import Button

CANAL = 1
PERIODE_MS = 5000      # changement d'émetteur affiché toutes les 5 s
ADRESSE_LCD = 0x27
BROCHE_BOUTON = 0      # 0 = bouton BOOT de la carte ; mettre la broche de ton bouton
NB_VALEURS = 2         # valeurs mémorisées par émetteur

radio = Radio(CANAL)
print("MAC du recepteur :", radio.mac())

historique = History(NB_VALEURS)
ecran = Display(I2C(0, sda=Pin(21), scl=Pin(22), freq=400000), ADRESSE_LCD, PERIODE_MS)
bouton = Button(BROCHE_BOUTON)

while True:
    for nom, valeur in radio.messages():
        historique.add(nom, valeur)

    if bouton.pressed():
        ecran.next(historique)
    else:
        ecran.tick(historique)

    time.sleep_ms(50)
