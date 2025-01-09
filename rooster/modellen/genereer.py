import sys

from colorama import Fore, Style
from typing import Literal, Final

from .vak import Vak
from .student import Student
from .tijdslot import Tijdslot
from .zaal import Zaal, Zaalslot
from .vakactiviteit import Vakactiviteit
from ..dataverwerking.lees import Roosterdata
from ..dataverwerking.schrijf import schrijf_foutmelding
from ..constants.constant import returncodes, tijdeenheden, teksten, maxima


class Roostermaker:
    __slots__: tuple[str, ...] = (
        "__zalen", "__vakken", "TIJDSLOTEN", "__rooster", "__pad_resultaten_csv", "__studenten", "__strafpunten",
        "__grootste_zaal_gebruikt", "__aantal_gebruikte_zalen"
    )

    def __init__(self, roosterdata: Roosterdata) -> None:
        self.__zalen: tuple[Zaal, ...] = self._sorteer_zalen(roosterdata.ZALEN)
        self.__vakken: tuple[Vak, ...] = roosterdata.VAKKEN
        self.__studenten: tuple[Student, ...] = roosterdata.STUDENTEN
        self.__pad_resultaten_csv: str = roosterdata.PAD_CSV_RESULTATEN

        self.TIJDSLOTEN: Final[tuple[Tijdslot, ...]] = (
            Tijdslot(weekdag="maandag", tijdstip="9.00–11.00"), Tijdslot(weekdag="maandag", tijdstip="11.00–13.00"),
            Tijdslot(weekdag="maandag", tijdstip="13.00–15.00"), Tijdslot(weekdag="maandag", tijdstip="15.00–17.00"),
            Tijdslot(weekdag="dinsdag", tijdstip="9.00–11.00"), Tijdslot(weekdag="dinsdag", tijdstip="11.00–13.00"),
            Tijdslot(weekdag="dinsdag", tijdstip="13.00–15.00"), Tijdslot(weekdag="dinsdag", tijdstip="15.00–17.00"),
            Tijdslot(weekdag="woensdag", tijdstip="9.00–11.00"), Tijdslot(weekdag="woensdag", tijdstip="11.00–13.00"),
            Tijdslot(weekdag="woensdag", tijdstip="13.00–15.00"), Tijdslot(weekdag="woensdag", tijdstip="15.00–17.00"),
            Tijdslot(weekdag="donderdag", tijdstip="9.00–11.00"), Tijdslot(weekdag="donderdag", tijdstip="11.00–13.00"),
            Tijdslot(weekdag="donderdag", tijdstip="13.00–15.00"), Tijdslot(weekdag="donderdag", tijdstip="15.00–17.00"),
            Tijdslot(weekdag="vrijdag", tijdstip="9.00–11.00"), Tijdslot(weekdag="vrijdag", tijdstip="11.00–13.00"),
            Tijdslot(weekdag="vrijdag", tijdstip="13.00–15.00"), Tijdslot(weekdag="vrijdag", tijdstip="15.00–17.00"),
            Tijdslot(weekdag="vrijdag", tijdstip="17.00–19.00")
        )

        self.__rooster: dict[Zaalslot, Vakactiviteit] = {}
        self.__aantal_gebruikte_zalen: int = 0
        self.__strafpunten: int = 0
        self.__grootste_zaal_gebruikt: bool = False

    def _sorteer_zalen(self, zalen: tuple[Zaal, ...]) -> tuple[Zaal, ...]:
        """
        Sorteert de zalen van groot naar klein — zodat de grote zalen eerder gebruikt kunnen worden voor de hoorcolleges.
        """
        zaalnamen_met_grootten: dict[str, int] = {zaal.naam: zaal.capaciteit for zaal in self.__zalen}
        zalen_gesorteerd: list[tuple[str, int]] = sorted(zaalnamen_met_grootten.items(), key=lambda x: x[1])

        zalen_gesorteerd_: list[Zaal | None] = [None] * zalen.__len__()

        for i, zaalnaam_met_grootte in enumerate(zalen_gesorteerd):
            for zaal in self.__zalen:
                if zaal.naam == zaalnaam_met_grootte[0]:
                    zalen_gesorteerd_[i] = zaal
                    break

        return tuple(zalen_gesorteerd_)

    def _is_vrij(self, zaalslot: Zaalslot) -> bool:
        """
        Geeft terug of een tijd-zaalcombinaties (zaalslot) vrij is — of er nog geen vakactiviteit is ingeroosterd voor een bepaalde zaal op een gegeven tijdstip.
        """
        return zaalslot not in self.__rooster

    @staticmethod
    def _kan_faciliteren(zaal: Zaal, vakactiviteit: Vakactiviteit) -> bool:
        """
        Geeft terug of een zaal een bepaalde vakactiviteit kan faciliteren — of de zaal genoeg zitplaatsen heeft voor het vereiste aantal studenten.
        """
        if vakactiviteit.type == "hoorcollege":
            return zaal.capaciteit >= vakactiviteit.vak.aantal_studenten()

        voor_werkcollege: bool = True if (vakactiviteit.type == "werkcollege") else False

        return zaal.capaciteit >= vakactiviteit.vak.geef_aantal_studenten_per_niet_hoorcollege(voor_werkcollege)

    def _voeg_activiteit_toe_aan_rooster_studenten(self, zaalslot: Zaalslot, vakactiviteit: Vakactiviteit) -> None:
        """
        Voegt een ingeroosterde vakactiviteit toe aan de persoonlijke roosters van iedere student die het vak van de activiteit volgt.
        """
        for student in self.__studenten:
            if not student.volgt_vak(vakactiviteit.vak.naam):
                continue

            student.voeg_activiteit_toe_aan_rooster(zaalslot, vakactiviteit)

    def _gebruik_grote_zaal(self, zaalslot: Zaalslot, vakactiviteit: Vakactiviteit) -> None:
        """
        Gebruikt de grote zaal voor een vakactiviteit.
        """
        self.__rooster[zaalslot] = vakactiviteit

        self._voeg_activiteit_toe_aan_rooster_studenten(zaalslot, vakactiviteit)

        self.__grootste_zaal_gebruikt = True

        self.__aantal_gebruikte_zalen += 1
        self.__strafpunten += 5

    def _is_laatste_zaal(self) -> bool:
        """
        Geeft terug of de laatste zaal aan bod is.
        """
        return self.__aantal_gebruikte_zalen == (len(self.__zalen) - 1)

    def rooster_activiteit_in(self, vakactiviteit: Vakactiviteit) -> Literal[0, -1]:
        """
        Poogt een activiteit in te roosteren, en geeft met een returncode terug of dit is gelukt.
        """
        ongebruikte_zaalsloten: set[Zaalslot] = set()

        for tijdslot in self.TIJDSLOTEN:
            for zaal in self.__zalen:
                zaalslot: Zaalslot = Zaalslot(tijdslot, zaal)

                if zaalslot.tijdslot.tijdstip.startswith("17"):
                    if self._is_laatste_zaal() and not self.__grootste_zaal_gebruikt:
                        pass

                if not self._is_vrij(zaalslot):
                    if (zaalslot.zaal.naam == maxima.GROOTSTE_ZAAL) and not self.__grootste_zaal_gebruikt:
                        self._gebruik_grote_zaal(zaalslot, vakactiviteit)

                        continue

                    if not self.__grootste_zaal_gebruikt and self._is_laatste_zaal():
                        self._gebruik_grote_zaal(zaalslot, vakactiviteit)

                        continue

                if not self._kan_faciliteren(zaal, vakactiviteit):
                    self.__strafpunten += 1

                self.__rooster[zaalslot] = vakactiviteit
                self._voeg_activiteit_toe_aan_rooster_studenten(zaalslot, vakactiviteit)

                self.__aantal_gebruikte_zalen += 1

                return returncodes.SUCCES

        return returncodes.MISLUKT

    def genereer_rooster(self) -> dict[Zaalslot, Vakactiviteit]:
        """
        Genereert een rooster voor een gegeven tuple vakactiviteiten.
        """
        for vak in self.__vakken:
            for _ in range(vak.aantal_hoorcolleges):
                if self.rooster_activiteit_in(Vakactiviteit(vak, "hoorcollege")) == returncodes.MISLUKT:
                    schrijf_foutmelding(f"het is niet gelukt een hoorcollegetijdslot te vinden voor {vak.naam}!")

            for _ in range(vak.aantal_werkcolleges):
                if self.rooster_activiteit_in(Vakactiviteit(vak, "werkcollege")) == returncodes.MISLUKT:
                    schrijf_foutmelding(f"het is niet gelukt een werkcollegetijdslot te vinden voor {vak.naam}!")

            for _ in range(vak.aantal_practica):
                if self.rooster_activiteit_in(Vakactiviteit(vak, "practicum")) == returncodes.MISLUKT:
                    schrijf_foutmelding(f"het is niet gelukt een practicumtijdslot te vinden voor {vak.naam}!")

        return self.__rooster

    def print_rooster(self) -> None:
        """
        Print het rooster naar de stdout (de standaarduitvoerstroom).
        """
        if not self.__rooster:
            raise ValueError("Geen rooster is not gegenereerd; printen onmogelijk.")

        for dag in tijdeenheden.WEEKDAGEN:
            sys.stdout.write(f"\n{dag.upper()}\n{'-' * 110}\n")

            for zaalslot, vakactiviteit in self.__rooster.items():
                if zaalslot.tijdslot.weekdag == dag:
                    sys.stdout.write(
                        f"- {Fore.BLUE}{zaalslot.zaal.naam}: {Fore.MAGENTA}{vakactiviteit.vak.naam} "
                        f"{Fore.YELLOW}({vakactiviteit.type}){Style.RESET_ALL}\n"
                    )

    @staticmethod
    def print_rooster_student(student: Student) -> None:
        """
        Print het persoonlijke rooster van een student naar de stdout (de standaarduitvoerstroom).
        """
        if not student.rooster:
            raise ValueError("Geen rooster is not gegenereerd voor deze student; printen onmogelijk.")

        sys.stdout.write(
            f"ROOSTER {Fore.GREEN}{student.volledige_naam}{Fore.MAGENTA}"
            f" ({student.studentnummer}){Style.RESET_ALL}\n{'-' * 85}\n"
        )

        for dag in tijdeenheden.WEEKDAGEN:
            sys.stdout.write(f"\n{dag.upper()}\n{'-' * 110}\n")

            for zaalslot, vakactiviteit in student.rooster.items():
                if zaalslot.tijdslot.weekdag == dag:
                    sys.stdout.write(
                        f"- {Fore.BLUE}{zaalslot.zaal.naam}: {Fore.MAGENTA}{vakactiviteit.vak.naam} "
                        f"{Fore.YELLOW}({vakactiviteit.type}){Style.RESET_ALL}\n"
                    )

    def print_alle_studentroosters(self) -> None:
        """
        Print het rooster van iedere student.
        """
        for student in self.__studenten:
            self.print_rooster_student(student)

    def bereken_strafpunten(self) -> int:
        """
        Berekent het aantal strafpunten van de huidige roosterconfiguratie.
        """
        ...

    def naar_csv(self) -> None:
        """
        Schrijft de data van het genereerde rooster naar een csv-bestand.
        """
        if not self.__rooster:
            raise ValueError("Geen rooster is not gegenereerd; schrijven naar csv-bestand onmogelijk.")

        with open(self.__pad_resultaten_csv, 'w', encoding="utf-8") as csv_bestand:
            csv_bestand.write(teksten.KOLOMMEN_RESULTATEN_CSV)

            for student in self.__studenten:
                vakken_met_huidig_werkcollege: dict[str, dict[str, int]] = {
                    naam_vak: {"practicum": 0, "hoorcollege": 0, "werkcollege": 0} for naam_vak in student.vaknamen
                }

                for zaalslot, activiteit in student.rooster.items():
                    vakken_met_huidig_werkcollege[activiteit.vak.naam][activiteit.type] += 1

                    csv_bestand.write(
                        f"{student.volledige_naam},{activiteit.vak.naam},"
                        f"{activiteit.type}{vakken_met_huidig_werkcollege[activiteit.vak.naam][activiteit.type]},"
                        f"{zaalslot.zaal.naam},{zaalslot.tijdslot.weekdag},{zaalslot.tijdslot.tijdstip} uur\n"
                    )
