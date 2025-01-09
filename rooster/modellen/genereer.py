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
from ..constants.constant import returncodes, tijdeenheden, teksten


class Roostermaker:
    __slots__: tuple[str, ...] = ("zalen", "vakken", "TIJDSLOTEN", "rooster", "pad_resultaten_csv", "studenten")

    def __init__(self, roosterdata: Roosterdata) -> None:
        self.zalen: tuple[Zaal, ...] = roosterdata.ZALEN
        self.vakken: tuple[Vak, ...] = roosterdata.VAKKEN
        self.studenten: tuple[Student, ...] = roosterdata.STUDENTEN
        self.pad_resultaten_csv: str = roosterdata.PAD_CSV_RESULTATEN

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
            Tijdslot(weekdag="vrijdag", tijdstip="13.00–15.00"), Tijdslot(weekdag="vrijdag", tijdstip="15.00–17.00")
        )

        self.rooster: dict[Zaalslot, Vakactiviteit] = {}

    def is_vrij(self, zaalslot: Zaalslot) -> bool:
        """
        Geeft terug of een tijd-zaalcombinaties (zaalslot) vrij is — of er nog geen vakactiviteit is ingeroosterd voor een bepaalde zaal op een gegeven tijdstip.
        """
        return zaalslot not in self.rooster

    @staticmethod
    def _kan_faciliteren(zaal: Zaal, vakactiviteit: Vakactiviteit) -> bool:
        """
        Geeft terug of een zaal een bepaalde vakactiviteit kan faciliteren — of de zaal genoeg zitplaatsen heeft voor het vereiste aantal studenten.
        """
        if vakactiviteit.type == "hoorcollege":
            return zaal.capaciteit >= vakactiviteit.vak.aantal_studenten()

        if vakactiviteit.vak.aantal_studenten_per_werkcollege:
            return zaal.capaciteit >= vakactiviteit.vak.aantal_studenten_per_werkcollege

        return True

    def _voeg_activiteit_toe_aan_rooster_studenten(self, zaalslot: Zaalslot, vakactiviteit: Vakactiviteit) -> None:
        """
        Voegt een ingeroosterde vakactiviteit toe aan de persoonlijke roosters van iedere student die het vak van de activiteit volgt.
        """
        for student in self.studenten:
            if not student.volgt_vak(vakactiviteit.vak.naam):
                continue

            student.voeg_activiteit_toe_aan_rooster(zaalslot, vakactiviteit)

    def rooster_activiteit_in(self, vakactiviteit: Vakactiviteit) -> Literal[0, -1]:
        """
        Poogt een activiteit in te roosteren, en geeft met een returncode terug of dit is gelukt.
        """
        for tijdslot in self.TIJDSLOTEN:
            for zaal in self.zalen:
                zaalslot: Zaalslot = Zaalslot(tijdslot, zaal)

                if not self.is_vrij(zaalslot):
                    continue

                if not self._kan_faciliteren(zaal, vakactiviteit):
                    continue

                self.rooster[zaalslot] = vakactiviteit

                self._voeg_activiteit_toe_aan_rooster_studenten(zaalslot, vakactiviteit)

                return returncodes.SUCCES

        return returncodes.MISLUKT

    def genereer_rooster(self) -> dict[Zaalslot, Vakactiviteit]:
        """
        Genereert een rooster voor een gegeven tuple vakactiviteiten.
        """
        for vak in self.vakken:
            for _ in range(vak.aantal_hoorcolleges):
                if self.rooster_activiteit_in(Vakactiviteit(vak, "hoorcollege")) == returncodes.MISLUKT:
                    schrijf_foutmelding(f"het is niet gelukt een hoorcollegetijdslot te vinden voor {vak.naam}!")

            for _ in range(vak.aantal_werkcolleges):
                if self.rooster_activiteit_in(Vakactiviteit(vak, "werkcollege")) == returncodes.MISLUKT:
                    schrijf_foutmelding(f"het is niet gelukt een werkcollegetijdslot te vinden voor {vak.naam}!")

            for _ in range(vak.aantal_practica):
                if self.rooster_activiteit_in(Vakactiviteit(vak, "practicum")) == returncodes.MISLUKT:
                    schrijf_foutmelding(f"het is niet gelukt een practicumtijdslot te vinden voor {vak.naam}!")

        return self.rooster

    def print_rooster(self) -> None:
        """
        Print het rooster naar de stdout (de standaarduitvoerstroom).
        """
        if not self.rooster:
            raise ValueError("Geen rooster is not gegenereerd; printen onmogelijk.")

        for dag in tijdeenheden.WEEKDAGEN:
            sys.stdout.write(f"\n{dag.upper()}\n{'-' * 110}\n")

            for zaalslot, vakactiviteit in self.rooster.items():
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
        for student in self.studenten:
            self.print_rooster_student(student)

    def naar_csv(self) -> None:
        """
        Schrijft de data van het genereerde rooster naar een csv-bestand.
        """
        if not self.rooster:
            raise ValueError("Geen rooster is not gegenereerd; schrijven naar csv-bestand onmogelijk.")

        with open(self.pad_resultaten_csv, 'w', encoding="utf-8") as csv_bestand:
            csv_bestand.write(teksten.KOLOMMEN_RESULTATEN_CSV)

            for student in self.studenten:
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
