

class Tijdslot:
    __slots__: tuple[str, ...] = ("weekdag", "tijdstip")

    def __init__(self, weekdag: str, tijdstip: str) -> None:
        self.weekdag: str = weekdag
        self.tijdstip: str = tijdstip

    def __str__(self) -> str:
        return f"{self.tijdstip} uur"

    def __repr__(self) -> str:
        return f"{self.tijdstip} uur"
