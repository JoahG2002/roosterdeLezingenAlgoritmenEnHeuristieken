from threading import Thread, Lock

from .student import Student
from .activiteit import Activiteit


class BundelStrafpunten:
    __slots__: tuple[str, ...] = (
        "__totaalaantal_strafpunten", "roostergaten", "avondactiviteiten", "overvolle_zalen", "dubbel_ingeroosterd",
        "ongebruikte_tijdsloten", "thread_lock"
    )

    def __init__(self, studenten: set[Student], rooster: list[Activiteit | None]) -> None:
        self.__totaalaantal_strafpunten: int = 0
        self.roostergaten: int = 0
        self.dubbel_ingeroosterd: int = 0
        self.avondactiviteiten: int = 0
        self.overvolle_zalen: int = 0
        self.ongebruikte_tijdsloten: int = 0

        self.thread_lock: Lock = Lock()

        self._bereken_strafpunten(studenten, rooster)

    def _bereken_strafpunten(self, studenten: set[Student], rooster: list[Activiteit | None]) -> None:
        """
        Berekent de diverse strafpunten per onderdeel op meerdere threads.
        """
        threads: tuple[Thread, ...] = (
            Thread(target=self._bereken_strafpunten_roostergaten, args=(studenten,)),
            Thread(target=self._bereken_strafpunten_dubbel_ingeroosterd, args=(studenten,)),
            Thread(target=self._bereken_avondstrafpunten, args=(rooster,)),
            Thread(target=self._bereken_avondstrafpunten, args=(rooster,)),
            Thread(target=self._bereken_strafpunten_overvolle_zalen, args=(rooster,)),
            Thread(target=self._tel_aantal_ongebruikte_tijdsloten, args=(rooster,)),
        )

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def _bereken_strafpunten_roostergaten(self, studenten: set[Student]) -> None:
        """
        Berekent het totaalaantal strafpunten door roostergaten.
        """
        self.roostergaten: int = 0

        for student in studenten:
            self.roostergaten += student.bereken_strafpunten_roostergaten()

        with self.thread_lock:
            self.__totaalaantal_strafpunten += self.roostergaten

    def _bereken_avondstrafpunten(self, rooster: list[Activiteit | None]) -> None:
        """
        Berekent het aantal strafpunten opgelopen door avondactiviteiten.
        """
        self.avondactiviteiten: int = sum(
            5 for activiteit in rooster if activiteit
            and activiteit.zaalslot.tijdslot.tijdstip.startswith("17")
            and not activiteit.vakactiviteit.type.startswith('h')
        )

        with self.thread_lock:
            self.__totaalaantal_strafpunten += self.avondactiviteiten

    def totaal(self) -> int:
        """
        Geeft het totaalaantal strafpunten terug.
        """
        return self.__totaalaantal_strafpunten

    def _tel_aantal_ongebruikte_tijdsloten(self, rooster: list[Activiteit | None]) -> None:
        """
        Telt het aantal ongebruikte tijdsloten.
        """
        self.ongebruikte_tijdsloten = rooster.count(None)

        with self.thread_lock:
            self.__totaalaantal_strafpunten += self.ongebruikte_tijdsloten

    def _bereken_strafpunten_overvolle_zalen(self, rooster: list[Activiteit | None]) -> None:
        """
        Geeft het aantal strafpunten voor te volle zalen terug.
        """
        self.overvolle_zalen: int = sum(
            1 for activiteit in rooster if activiteit and activiteit.zaalslot.zaal.capaciteit < activiteit.grootte_groep
        )

        with self.thread_lock:
            self.__totaalaantal_strafpunten += self.overvolle_zalen

    def _bereken_strafpunten_dubbel_ingeroosterd(self, studenten: set[Student]) -> None:
        """
        Geeft het aantal dubbelingeroosterde activiteiten terug als strafpunten.
        """
        for student in studenten:
            self.dubbel_ingeroosterd += student.aantal_dubbel_dubbele_inroosteringen()

        with self.thread_lock:
            self.__totaalaantal_strafpunten += self.dubbel_ingeroosterd