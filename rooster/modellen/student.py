import sys

from colorama import Fore, Style
from typing import Literal, ItemsView, Iterator

from .zaal import Zaalslot
from .vakactiviteit import Vakactiviteit
from ..constants.constant import tijdeenheden


class Student:
    __slots__: tuple[str, ...] = ("studentnummer", "__vaknamen", "__rooster", "volledige_naam")

    def __init__(self, studentnummer: int, voornaam: str, achternaam: int, vaknamen: set[str]) -> None:
        self.studentnummer: int = studentnummer
        self.volledige_naam: str = f"{voornaam} {achternaam}"
        self.__vaknamen: set[str] = vaknamen
        self.__rooster: dict[Zaalslot, Vakactiviteit] = {}

    def __hash__(self) -> int:
        return hash(self.studentnummer)

    def volgt_vak(self, vaknaam: str) -> bool:
        """
        Geeft terug of een student een bepaald vak volgt.
        """
        return vaknaam in self.__vaknamen

    def voeg_activiteit_toe_aan_rooster(self, zaalslot: Zaalslot, vakactiviteit: Vakactiviteit) -> None:
        """
        Voegt een vakactiviteit toe aan het persoonlijke rooster van een student.
        """
        self.__rooster[zaalslot] = vakactiviteit

    def geef_rooster(self) -> ItemsView[Zaalslot, Vakactiviteit]:
        """
        Geeft een pointer naar een students rooster.
        """
        return self.__rooster.items()

    def geef_vaknamen(self) -> Iterator[str]:
        """
        Geeft een iterable van de students vaknamen terug.
        """
        return iter(self.__vaknamen)

    def print_rooster(self) -> None:
        """
        Print het persoonlijke rooster van een student naar de stdout (de standaarduitvoerstroom).
        """
        if not self.__rooster:
            raise ValueError("Geen rooster is not gegenereerd voor deze student; printen onmogelijk.")

        sys.stdout.write(
            f"ROOSTER {Fore.GREEN}{self.volledige_naam}{Fore.MAGENTA} ({self.studentnummer}){Style.RESET_ALL}\n{'-' * 85}\n"
        )

        for dag in tijdeenheden.WEEKDAGEN:
            sys.stdout.write(f"\n{dag.upper()}\n{'-' * 110}\n")

            for zaalslot, vakactiviteit in self.__rooster.items():
                if zaalslot.tijdslot.weekdag == dag:
                    sys.stdout.write(
                        f"- {Fore.BLUE}{zaalslot.zaal.naam}: {Fore.MAGENTA}{vakactiviteit.vak.naam} "
                        f"{Fore.YELLOW}({vakactiviteit.type}){Style.RESET_ALL}\n"
                    )

    @staticmethod
    def aantal_strafpunten_tijdslot(starttijd: int, eindtijd: int) -> Literal[0, 1, 3, 1000]:
        """
        Geeft terug of er een tussentijdslot is tussen een students vakken op een dag.
        """
        verschil_tijdslot: int = (eindtijd - starttijd)

        if verschil_tijdslot == 0:
            return 0

        if verschil_tijdslot == 2:
            return 1

        if verschil_tijdslot == 4:
            return 3

        return 1000

    @staticmethod
    def _tijdstip_naar_integer(tijdstip: str) -> int:
        """
        Ontvangt een tijdstip als string en zet de eerste twee karakters om naar een integer.
        """
        return int(tijdstip[:2])

    def bereken_strafpunten_roostergaten(self) -> int:
        """
        Berekent de strafpunten voor de gaten in een students rooster:

        - 1 tussentijdslot levert 1 strafpunt op;
        - 2 tussentijdsloten leveren per dag leveren 3 strafpunten op;
        - 1000 tussentijdsloten op één dag zijn niet toegestaan.
        """
        strafpunten_tussentijdsloten: int = 0

        for weekdag in tijdeenheden.WEEKDAGEN:
            tijdsloten_op_dag_start_tot_eind: tuple[int, ...] = tuple(
                sorted(
                    self._tijdstip_naar_integer(zaalslot.tijdslot.tijdstip) for zaalslot in self.__rooster
                    if (zaalslot.tijdslot.weekdag == weekdag)
                )
            )

            if not tijdsloten_op_dag_start_tot_eind or (len(tijdsloten_op_dag_start_tot_eind) == 1):
                continue

            i: int = 0

            while i < (len(tijdsloten_op_dag_start_tot_eind) - 1):
                strafpunten_tussentijdsloten += self.aantal_strafpunten_tijdslot(
                    starttijd=tijdsloten_op_dag_start_tot_eind[i],
                    eindtijd=tijdsloten_op_dag_start_tot_eind[i + 1]
                )

                i += 1

        return strafpunten_tussentijdsloten
