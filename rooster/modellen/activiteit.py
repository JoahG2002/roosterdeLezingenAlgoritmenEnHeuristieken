from typing import Literal

from .vak import Vak
from zaal import Zaalslot


class Vakactiviteit:
    __slots__: tuple[str, ...] = ("vak", "type")

    def __init__(self, vak: Vak, type_: Literal["hoorcollege", "werkcollege", "practicum"]) -> None:
        self.vak: Vak = vak
        self.type: Literal["hoorcollege", "werkcollege", "practicum"] = type_

    def __hash__(self) -> int:
        return hash((self.vak, self.type))


class Activiteit:
    __slots__: tuple[str, ...] = ("zaalslot", "vakactiviteit", "grootte_groep")

    def __init__(self, zaalslot: Zaalslot, vakactiviteit: Vakactiviteit, grootte_groep: int) -> None:
        self.zaalslot: Zaalslot = zaalslot
        self.vakactiviteit: Vakactiviteit = vakactiviteit
        self.grootte_groep: int = grootte_groep
