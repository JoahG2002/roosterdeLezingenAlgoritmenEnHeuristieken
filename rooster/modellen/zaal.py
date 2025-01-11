from typing import Self

from .tijdslot import Tijdslot


class Zaal:
    __slots__: tuple[str, ...] = ("naam", "capaciteit", "bezette_plaatsen")

    def __init__(self, naam: str, capaciteit: int) -> None:
        self.naam: str = naam
        self.capaciteit: int = capaciteit
        self.bezette_plaatsen: int = 0


class Zaalslot:
    __slots__: tuple[str, ...] = ("tijdslot", "zaal")

    def __init__(self, tijdslot: Tijdslot, zaal: Zaal) -> None:
        self.tijdslot: Tijdslot = tijdslot
        self.zaal: Zaal = zaal

    def __hash__(self) -> int:
        return hash((self.tijdslot.weekdag, self.tijdslot.tijdstip, self.zaal.naam))

    def __eq__(self, other: Self) -> bool:
        return ((self.tijdslot.weekdag, self.tijdslot.tijdstip, self.zaal.naam)
                == (other.tijdslot.weekdag, other.tijdslot.tijdstip, other.zaal.naam))

    def __str__(self) -> str:
        return f"Zaalslot({self.zaal.naam=}, {self.tijdslot.weekdag=}, {self.tijdslot.tijdstip=})"

    def __repr__(self) -> str:
        return f"Zaalslot({self.zaal.naam=}, {self.tijdslot.weekdag=}, {self.tijdslot.tijdstip=})"
