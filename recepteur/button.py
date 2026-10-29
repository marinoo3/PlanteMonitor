# Bouton poussoir câblé entre la broche et GND (pull-up interne)
from machine import Pin
import time


class Button:
    def __init__(self, broche: int, anti_rebond_ms: int = 200) -> None:
        self.anti_rebond = anti_rebond_ms
        self._t = time.ticks_ms()
        self._appui = False
        self.pin = Pin(broche, Pin.IN, Pin.PULL_UP)
        self.pin.irq(trigger=Pin.IRQ_FALLING, handler=self._irq)

    def _irq(self, _) -> None:
        t = time.ticks_ms()
        if time.ticks_diff(t, self._t) > self.anti_rebond:
            self._t = t
            self._appui = True

    def pressed(self) -> bool:
        """
        True when clicked, reset when consumed

        Returns:
            bool: Has button been pressed
        """
        if self._appui:
            self._appui = False
            return True
        return False
