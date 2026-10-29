# Écran LCD I2C 20x4 : affiche les émetteurs un par un, en boucle
import time
from machine import I2C
from i2c_lcd import I2cLcd

from history import History


def _age(t):
    s = time.time() - t
    if s < 3600:
        return "%d min" % (s // 60)
    if s < 48 * 3600:
        return "%d h" % (s // 3600)
    return "%d j" % (s // 86400)


class Display:
    def __init__(
            self, 
            i2c: I2C, 
            adresse: int = 0x27, 
            periode_ms: int = 5000, 
            lignes: int = 4, 
            colonnes: int = 20
        ) -> None:
        self.lcd = I2cLcd(i2c, adresse, lignes, colonnes)
        self.colonnes = colonnes
        self.periode = periode_ms
        self.index = 0
        self.dernier = time.ticks_ms() - periode_ms

    def tick(self, historique: History) -> None:
        """
        Show next view each `periode_ms`

        Args:
            historique (History): App values history
        """
        if time.ticks_diff(time.ticks_ms(), self.dernier) >= self.periode:
            self.next(historique)

    def next(self, historique: History) -> None:
        """
        Show next view and reset count down

        Args:
            historique (History): App values history
        """
        self.dernier = time.ticks_ms()
        self._show(historique)
        self.index += 1

    def _line(self, n: int, text) -> None:
        """
        Write an entire line

        Args:
            n (int): Line index
            text (_type_): Text to write on line
        """
        self.lcd.move_to(0, n)
        self.lcd.putstr((text + " " * self.colonnes)[:self.colonnes])

    def _line_lr(self, n: int, left: str, right: str) -> None:
        """
        Write `left` aligned left and `right` aligned right on the same line
        (`left` is truncated if needed)

        Args:
            n (int): Line index
            left (str): Text on the left
            right (str): Text on the right
        """
        left = left[:max(0, self.colonnes - len(right) - 1)]
        self._line(n, left + " " * (self.colonnes - len(left) - len(right)) + right)

    def _show(self, historique: History) -> None:
        """
        Show a view. Write all information on screen

        Args:
            historique (History): App values history
        """
        noms = historique.names()
        if not noms:
            self._line(0, "En attente des")
            self._line(1, "emetteurs...")
            self._line(2, "")
            self._line(3, "")
            return
        self.index %= len(noms)
        nom = noms[self.index]
        vals = historique.values(nom)
        valeur, t = vals[0]
        self._line_lr(0, nom, _age(t))                  # ex. "Tomates       12 min"
        self._line(1, "Humidite: %d%%" % round(valeur))
        # Évolution entre la valeur la plus récente et la plus ancienne mémorisée
        if len(vals) > 1:
            self._line(2, "Evolution: %+d%%" % round(valeur - vals[-1][0]))
        else:
            self._line(2, "Evolution: --")
        self._line_lr(3, "", "%d/%d" % (self.index + 1, len(noms)))
