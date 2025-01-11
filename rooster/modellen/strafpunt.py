from .student import Student
from .activiteit import Activiteit


class BundelStrafpunten:
    __slots__: tuple[str, ...] = (
        "__totaalaantal_strafpunten", "roostergaten", "avondactiviteiten", "overvolle_zalen", "dubbel_ingeroosterd",
        "ongebruikte_tijdsloten"
    )

    def __init__(self,
                 studenten: set[Student],
                 rooster: list[Activiteit | None]) -> None:
        self.__totaalaantal_strafpunten: int = 0
        self.roostergaten: int = self._bereken_strafpunten_roostergaten(studenten)
        self.dubbel_ingeroosterd: int = self._bereken_strafpunten_dubbel_ingeroosterd(studenten)
        self.avondactiviteiten: int = self._bereken_avondstrafpunten(rooster)
        self.overvolle_zalen: int = self._bereken_strafpunten_overvolle_zalen(rooster)
        self.ongebruikte_tijdsloten: int = self._tel_aantal_ongebruikte_tijdsloten(rooster)

    def _bereken_strafpunten_roostergaten(self, studenten: set[Student]) -> int:
        """
        Berekent het totaalaantal strafpunten door roostergaten.
        """
        strafpunten_roostergaten: int = 0

        for student in studenten:
            strafpunten_roostergaten += student.bereken_strafpunten_roostergaten()

        self.__totaalaantal_strafpunten += strafpunten_roostergaten

        return strafpunten_roostergaten

    def _bereken_avondstrafpunten(self, rooster: list[Activiteit | None]) -> int:
        """
        Berekent het aantal strafpunten opgelopen door avondactiviteiten.
        """
        strafpunten_avondactiviteiten: int = sum(
            5 for activiteit in rooster if activiteit
            and activiteit.zaalslot.tijdslot.tijdstip.startswith("17")
            and not activiteit.vakactiviteit.type.startswith('h')
        )

        self.__totaalaantal_strafpunten += strafpunten_avondactiviteiten

        return strafpunten_avondactiviteiten

    def totaal(self) -> int:
        """
        Geeft het totaalaantal strafpunten terug.
        """
        return self.__totaalaantal_strafpunten

    @staticmethod
    def _tel_aantal_ongebruikte_tijdsloten(rooster: list[Activiteit | None]) -> int:
        """
        Telt het aantal ongebruikte tijdsloten.
        """
        return rooster.count(None)

    @staticmethod
    def _bereken_strafpunten_overvolle_zalen(rooster: list[Activiteit | None]) -> int:
        """
        Geeft het aantal strafpunten voor te volle zalen terug.
        """
        return sum(
            1 for activiteit in rooster if activiteit and activiteit.zaalslot.zaal.capaciteit < activiteit.grootte_groep
        )

    @staticmethod
    def _bereken_strafpunten_dubbel_ingeroosterd(studenten: set[Student]) -> int:
        """
        Geeft het aantal dubbelingeroosterde activiteiten terug als strafpunten.
        """
        aantal_dubbele_indelingen_studenten: int = 0

        for student in studenten:
            aantal_dubbele_indelingen_studenten += student.aantal_dubbel_dubbele_inroosteringen()

        return aantal_dubbele_indelingen_studenten
