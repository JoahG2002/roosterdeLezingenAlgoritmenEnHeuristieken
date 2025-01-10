from .zaal import Zaalslot
from .student import Student
from .vakactiviteit import Vakactiviteit


class BundelStrafpunten:
    __slots__: tuple[str, ...] = (
        "__totaalaantal_strafpunten", "roostergaten", "avondactiviteiten", "zaal_vol", "dubbel_ingeroosterd"
    )

    def __init__(self, studenten: tuple[Student, ...], rooster: list[tuple[Zaalslot, Vakactiviteit] | None]) -> None:
        self.__totaalaantal_strafpunten: int = 0
        self.roostergaten: int = self._bereken_strafpunten_roostergaten(studenten)
        self.avondactiviteiten: int = self._bereken_avondstrafpunten(rooster)
        self.zaal_vol: int = self._bereken_avondstrafpunten(rooster)
        self.dubbel_ingeroosterd: int = self._bereken_avondstrafpunten(rooster)

        # volle kamer
        # conflict

    def _bereken_strafpunten_roostergaten(self, studenten: tuple[Student, ...]) -> int:
        """
        Berekent het totaalaantal strafpunten door roostergaten.
        """
        strafpunten_roostergaten: int = 0

        for student in studenten:
            strafpunten_roostergaten += student.bereken_strafpunten_roostergaten()

        self.__totaalaantal_strafpunten += strafpunten_roostergaten

        return strafpunten_roostergaten

    def _bereken_avondstrafpunten(self, rooster: list[tuple[Zaalslot, Vakactiviteit] | None]) -> int:
        """
        Berekent het aantal strafpunten opgelopen door avondactiviteiten.
        """
        strafpunten_avondactiviteiten: int = sum(
            5 for roosteractiviteit in rooster
            if roosteractiviteit and roosteractiviteit[0].tijdslot.tijdstip.startswith("17")
            and not roosteractiviteit[1].type.startswith('h')
        )

        self.__totaalaantal_strafpunten += strafpunten_avondactiviteiten

        return strafpunten_avondactiviteiten

    def totaal(self) -> int:
        """
        Geeft het totaalaantal strafpunten terug.
        """
        return self.__totaalaantal_strafpunten
