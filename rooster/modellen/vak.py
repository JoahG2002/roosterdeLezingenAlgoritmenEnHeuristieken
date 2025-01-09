from typing import Literal

from .student import Student
from ..constants.constant import returncodes


class Vak:
    __slots__: tuple[str, ...] = (
        "naam", "aantal_hoorcolleges", "aantal_werkcolleges", "aantal_practica", "verwacht_aantal_student",
        "maximumaantal_studenten", "aantal_studenten_per_werkcollege", "studenten"
    )

    def __init__(self,
                 naam: str,
                 aantal_hoorcolleges: int,
                 aantal_werkcolleges: int,
                 aantal_practica: int,
                 verwacht_aantal_student: int,
                 maximumaantal_studenten: int,
                 aantal_studenten_per_werkcollege: int) -> None:
        self.naam: str = naam
        self.aantal_hoorcolleges: int = aantal_hoorcolleges
        self.aantal_werkcolleges: int = aantal_werkcolleges
        self.aantal_practica: int = aantal_practica
        self.verwacht_aantal_student: int = verwacht_aantal_student
        self.maximumaantal_studenten: int = maximumaantal_studenten
        self.aantal_studenten_per_werkcollege: int = aantal_studenten_per_werkcollege

        self.studenten: set[Student] = set()

    def __str__(self) -> str:
        return f"Vak({self.naam=}, {self.aantal_studenten=})"

    def voeg_student_toe(self, student: Student) -> Literal[0, -1]:
        """
        Voegt een student toe aan het vak, en geeft met een code terug of dat is gelukt.
        """
        if self.maximumaantal_studenten:
            if self.aantal_studenten() == self.maximumaantal_studenten:
                return returncodes.MISLUKT

        self.studenten.add(student)

        return returncodes.SUCCES

    def aantal_studenten(self) -> int:
        """
        Geeft het huidig aantal studenten dat voor het vak ingeschreven staat terug.
        """
        return len(self.studenten)
