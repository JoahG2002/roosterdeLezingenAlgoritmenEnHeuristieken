from typing import Literal, Self

from ..constants.constant import returncodes


class Vak:
    __slots__: tuple[str, ...] = (
        "naam", "aantal_hoorcolleges", "aantal_werkcolleges", "aantal_practica", "verwacht_aantal_student",
        "maximumaantal_studenten_werkcollege", "__aantal_studenten_per_werkcollege", "__studentnummers",
        "__aantal_studenten_per_practicum", "__grootten_werkcolleges", "__grootten_practica"
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
        self.__aantal_studenten_per_werkcollege: int | None = aantal_studenten_per_werkcollege
        self.__aantal_studenten_per_practicum: int | None = aantal_studenten_per_practicum

        self.__studentnummers: set[int] = set()
        self.__grootten_werkcolleges: list[int] = []
        self.__grootten_practica: list[int] = []

        self._bepaald_grootten_colleges()

    def __str__(self) -> str:
        return f"Vak({self.naam=}, {self.aantal_studenten=})"

    def __hash__(self) -> int:
        return hash(self.naam)

    def __eq__(self, other: Self) -> bool:
        return self.naam == other.naam

    def _bepaald_grootten_colleges(self) -> None:
        """
        Bepaalt de grootte van ieder werkcollege en practicum van het vak.
        """
        if self.aantal_werkcolleges > 0:
            for i in range(self.aantal_werkcolleges):
                self.__grootten_werkcolleges.append(0)

        if self.aantal_practica > 0:
            for i in range(self.aantal_practica):
                self.__grootten_werkcolleges.append(0)

    def geef_aantal_studenten_per_niet_hoorcollege(self, voor_werkcollege: bool) -> int:
        """
        Geeft terug hoeveel studenten zijn toegestaan bij een activiteit die geen hoorcollege is — waarbij niet het gehele leerjaar aanwezig mag zijn in één zaal.
        """
        if voor_werkcollege:
            return self.__aantal_studenten_per_werkcollege

        return self.__aantal_studenten_per_practicum

    def voeg_student_toe(self, id_student: int, activiteittype: str) -> Literal[0, -1]:
        """
        Voegt een student toe aan het vak, en geeft met een code terug of dat is gelukt.
        """
        if activiteittype == "hoorcollege":
            return returncodes.SUCCES

        plek_gevonden: bool = False

        if activiteittype == "werkcollege":
            for i in range(1, 5):
                if self.__grootten_werkcolleges.__len__() == i:
                    for j in range(i):
                        if not plek_gevonden and (self.__grootten_werkcolleges[j] < self.__aantal_studenten_per_werkcollege):
                            self.__studentnummers.add(id_student)

                            self.__grootten_werkcolleges[j] += 1
                            plek_gevonden = True

                            break

        if activiteittype == "practicum":
            for i in range(1, 5):
                if self.__grootten_practica.__len__() == i:
                    for j in range(i):
                        if not plek_gevonden and (self.__grootten_practica[j] < self.__aantal_studenten_per_practicum):
                            self.__studentnummers.add(id_student)

                            self.__grootten_werkcolleges[j] += 1
                            plek_gevonden = True

                            break

        if not plek_gevonden:
            return returncodes.MISLUKT

        return returncodes.SUCCES

    def aantal_studenten(self) -> int:
        """
        Geeft het huidig aantal studenten dat voor het vak ingeschreven staat terug.
        """
        return len(self.__studentnummers)
