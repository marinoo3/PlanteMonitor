# Mémorise les dernières valeurs reçues de chaque émetteur
import time
try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    ValueType = tuple[float, int]


class History:
    def __init__(self, size: int = 2):
        self.size = size
        self.data: dict[str, list[ValueType]] = {} 

    def add(self, name: str, value: float) -> None:
        vals = self.data.setdefault(name, [])
        vals.insert(0, (value, time.time()))
        if len(vals) > self.size:
            vals.pop()

    def names(self) -> list[str]:
        """
        Get all names

        Returns:
            list[str]: List of available names
        """
        return sorted(self.data)

    def values(self, name: str) -> list[ValueType]:
        """
        Get values for a specific emitor

        Args:
            name (str): Name of the emitor to retrieve

        Returns:
            float: Emitor value
        """
        return self.data[name]
