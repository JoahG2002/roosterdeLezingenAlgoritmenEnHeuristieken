from typing import Self


class Tijdslot:
    __slots__: tuple[str, ...] = ("weekdag", "tijdstip")

    def __init__(self, weekdag: str, tijdstip: str) -> None:
        self.weekdag: str = weekdag
        self.tijdstip: str = tijdstip

    def __str__(self) -> str:
        return f"{self.tijdstip} uur"

    def __repr__(self) -> str:
        return f"{self.tijdstip} uur"

    def __hash__(self) -> int:
        return hash(self.weekdag[:2] + self.tijdstip[:2])

    def __eq__(self, other: Self) -> bool:
        return (self.weekdag[:2] + self.tijdstip[:2]) == (other.weekdag[:2] + other.tijdstip[:2])
