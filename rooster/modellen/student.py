from .zaal import Zaalslot
from .vakactiviteit import Vakactiviteit


class Student:
    __slots__: tuple[str, ...] = ("studentnummer", "vaknamen", "rooster", "volledige_naam")

    def __init__(self, studentnummer: int, voornaam: str, achternaam: int, vaknamen: set[str]) -> None:
        self.studentnummer: int = studentnummer
        self.volledige_naam: str = f"{voornaam} {achternaam}"
        self.vaknamen: set[str] = vaknamen
        self.rooster: dict[Zaalslot, Vakactiviteit] = {}

    def __hash__(self) -> int:
        return hash(self.studentnummer)

    def volgt_vak(self, vaknaam: str) -> bool:
        """
        Geeft terug of een student een bepaald vak volgt.
        """
        return vaknaam in self.vaknamen

    def voeg_activiteit_toe_aan_rooster(self, zaalslot: Zaalslot, vakactiviteit: Vakactiviteit) -> None:
        """
        Voegt een vakactiviteit toe aan het persoonlijke rooster van een student.
        """
        self.rooster[zaalslot] = vakactiviteit
