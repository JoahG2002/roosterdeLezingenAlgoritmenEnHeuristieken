from ..constants.constant import maxima


class Vak:
    __slots__: tuple[str, ...] = (
        "naam", "aantal_hoorcolleges", "aantal_werkcolleges", "aantal_practica", "verwacht_aantal_student",
        "maximumaantal_studenten", "aantal_studenten_per_werkcollege"
    )

    def __init__(self,
                 naam: str,
                 aantal_lezingen: int,
                 aantal_werkcolleges: int,
                 aantal_practica: int,
                 verwacht_aantal_student: int,
                 maximumaantal_studenten: int) -> None:
        self.naam: str = naam
        self.aantal_hoorcolleges: int = aantal_lezingen
        self.aantal_werkcolleges: int = aantal_werkcolleges
        self.aantal_practica: int = aantal_practica
        self.verwacht_aantal_student: int = verwacht_aantal_student
        self.maximumaantal_studenten: int = maximumaantal_studenten
        self.aantal_studenten_per_werkcollege: int = self._bereken_aantal_studenten_per_werkcollege()

    def _bereken_aantal_studenten_per_werkcollege(self) -> int:
        """
        Berekent het aantal studenten waaruit een werkcollege bestaat voor een gegeven opleiding.
        """
        return self.maximumaantal_studenten // maxima.AANTAL_WERKCOLLEGES_TEGELIJKERTIJD_PER_VAK
