from typing import Literal

from .vak import Vak


class Vakactiviteit:
    __slots__: tuple[str, ...] = ("vak", "type")

    def __init__(self, vak: Vak, type_: Literal["hoorcollege", "werkcollege", "practicum"]) -> None:
        self.vak: Vak = vak
        self.type: Literal["hoorcollege", "werkcollege", "practicum"] = type_
