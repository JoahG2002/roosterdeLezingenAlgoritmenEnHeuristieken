from typing import Self

from .zaal import Zaalslot


class Vak:
    __slots__: tuple[str, ...] = (
        "naam", "aantal_hoorcolleges", "aantal_werkcolleges", "aantal_practica", "verwacht_aantal_student",
        "aantal_studenten_per_werkcollege", "aantal_studenten_per_practicum", "__hoorcolleges", "__werkcolleges",
        "__practica", "__studentnummers"
    )

    def __init__(self,
                 naam: str,
                 aantal_hoorcolleges: int,
                 aantal_werkcolleges: int,
                 aantal_practica: int,
                 verwacht_aantal_student: int,
                 aantal_studenten_per_werkcollege: int | None,
                 aantal_studenten_per_practicum: int | None) -> None:
        self.naam: str = naam
        self.aantal_hoorcolleges: int = aantal_hoorcolleges
        self.aantal_werkcolleges: int = aantal_werkcolleges
        self.aantal_practica: int = aantal_practica
        self.verwacht_aantal_student: int = verwacht_aantal_student
        self.aantal_studenten_per_werkcollege: int | None = aantal_studenten_per_werkcollege
        self.aantal_studenten_per_practicum: int | None = aantal_studenten_per_practicum

        self.__studentnummers: set[int] = set()

        self.__hoorcolleges: set[Zaalslot] = set()
        self.__werkcolleges: set[Zaalslot] = set()
        self.__practica: set[Zaalslot] = set()

    def __str__(self) -> str:
        return f"Vak({self.naam=}, {self.aantal_studenten=})"

    def __hash__(self) -> int:
        return hash(self.naam)

    def __eq__(self, other: Self) -> bool:
        return self.naam == other.naam

    def voeg_hoorcollege_toe(self, zaalslot: Zaalslot) -> None:
        """
        Voegt een lezing toe aan het rooster van het vak.
        """
        self.__hoorcolleges.add(zaalslot)

    def voeg_werkcollege_toe(self, zaalslot: Zaalslot) -> None:
        """
        Voegt een werkcollege toe aan het rooster van het vak.
        """
        self.__werkcolleges.add(zaalslot)

    def voeg_practicum_toe(self, zaalslot: Zaalslot) -> None:
        """
        Voegt een practicum toe aan het rooster van het vak.
        """
        self.__practica.add(zaalslot)

    def geef_aantal_studenten_per_niet_hoorcollege(self, voor_werkcollege: bool) -> int:
        """
        Geeft terug hoeveel studenten zijn toegestaan bij een activiteit die geen hoorcollege is — waarbij niet het gehele leerjaar aanwezig mag zijn in één zaal.
        """
        if voor_werkcollege:
            return self.aantal_studenten_per_werkcollege

        return self.aantal_studenten_per_practicum

    def voeg_student_toe(self, studentnummer: int) -> None:
        """
        Voegt een student toe aan het vak.
        """
        self.__studentnummers.add(studentnummer)

    def aantal_studenten(self) -> int:
        """
        Geeft het huidig aantal studenten dat voor het vak ingeschreven staat terug.
        """
        return len(self.__studentnummers)
