import sys
import random

from colorama import Fore, Style
from typing import Literal, Iterator, Self

from .zaal import Zaalslot
from .tijdslot import Tijdslot
from .activiteit import Activiteit
from ..constanten.constant import tijdeenheden, returncodes


class Student:
    __slots__: tuple[str, ...] = ("studentnummer", "__vaknamen", "__zaalsloten", "volledige_naam", "__rooster")

    def __init__(self, studentnummer: int, voornaam: str, achternaam: int, vaknamen: set[str]) -> None:
        self.studentnummer: int = studentnummer
        self.volledige_naam: str = f"{voornaam} {achternaam}"
        self.__vaknamen: set[str] = vaknamen
        self.__zaalsloten: set[Zaalslot] = set()
        self.__rooster: list[Activiteit] = []

    def __hash__(self) -> int:
        return hash(self.studentnummer)

    def __eq__(self, other: Self) -> bool:
        return self.studentnummer == other.studentnummer

    def volgt_vak(self, vaknaam: str) -> bool:
        """
        Geeft terug of een student een bepaald vak volgt.
        """
        return vaknaam in self.__vaknamen

    def voeg_activiteit_toe_aan_rooster(self, activiteit: Activiteit) -> None:
        """
        Voegt een vakactiviteit toe aan het persoonlijke rooster van een student.
        """
        self.__rooster.append(activiteit)
        self.__zaalsloten.add(activiteit.zaalslot)

    def geef_rooster(self) -> Iterator[Activiteit]:
        """
        Geeft een pointer naar een students zaalsloten.
        """
        return iter(self.__rooster)

    def geef_vaknamen(self) -> Iterator[str]:
        """
        Geeft een iterable van de students vaknamen terug.
        """
        return iter(self.__vaknamen)

    def verwijder_zaalslot(self, zaalslot: Zaalslot) -> Literal[0, -1]:
        """
        Verwijdert een zaalslot uit een students zaalsloten en rooster, als de student het volgt.
        """
        if not (zaalslot in self.__zaalsloten):
            return returncodes.MISLUKT

        self.__zaalsloten.remove(zaalslot)
        self.__rooster.remove(next(activiteit for activiteit in self.__rooster if (activiteit.zaalslot == zaalslot)))

        return returncodes.SUCCES

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

            for activiteit in self.__rooster:
                if activiteit.zaalslot.tijdslot.weekdag == dag:
                    sys.stdout.write(
                        f"- {Fore.BLUE}{activiteit.zaalslot.zaal.naam}: {Fore.MAGENTA}{activiteit.vakactiviteit.vak.naam} "
                        f"{Fore.YELLOW}({activiteit.vakactiviteit.type}){Style.RESET_ALL}\n"
                    )

    def geef_aantal_dubbele_inroosteringen(self) -> int:
        """
        Geeft het aantal keer dat een student dubbel is ingeroosterd terug.
        """
        aantal_unieke_tijdstippen_rooster: int = len(self.__zaalsloten)

        if aantal_unieke_tijdstippen_rooster == len(self.__rooster):
            return 0

        return len(self.__rooster) - aantal_unieke_tijdstippen_rooster

    def heeft_activiteit_op_tijdslot(self, tijdslot: Tijdslot) -> bool:
        """
        Geeft terug of de student al een activiteit heeft op een gegeven tijdslot.
        """
        return any(zaalslot.tijdslot == tijdslot for zaalslot in self.__zaalsloten)

    @staticmethod
    def _aantal_strafpunten_tijdslot(starttijd: int, eindtijd: int) -> Literal[0, 1, 3, 1000]:
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

    def geeft_tijdstippen_drietijdslotgaten(self) -> list[Tijdslot]:
        """
        Geeft alle laatste tijdsloten terug die leiden tot drietijdslotgaten.
        """
        tijdstippen_drietijdslotgaten: list[Tijdslot] = []

        for weekdag in tijdeenheden.WEEKDAGEN:
            tijdsloten_op_dag_start_tot_eind: tuple[Tijdslot, ...] = tuple(
                sorted(
                    tuple(
                        activiteit.zaalslot.tijdslot for activiteit in self.__rooster
                        if (activiteit.zaalslot.tijdslot.weekdag == weekdag)
                    ),
                    key=lambda tijdslot: self._tijdstip_naar_integer(tijdslot.tijdstip)
                )
            )

            if not tijdsloten_op_dag_start_tot_eind or (len(tijdsloten_op_dag_start_tot_eind) == 1):
                continue

            i: int = 0

            while i < (len(tijdsloten_op_dag_start_tot_eind) - 1):
                if self._aantal_strafpunten_tijdslot(
                    starttijd=self._tijdstip_naar_integer(tijdsloten_op_dag_start_tot_eind[i].tijdstip),
                    eindtijd=self._tijdstip_naar_integer(tijdsloten_op_dag_start_tot_eind[i + 1].tijdstip)
                ) == 1000:
                    tijdstippen_drietijdslotgaten.append(tijdsloten_op_dag_start_tot_eind[i + 1])  # het laatste tijdslot veroorzaakt het gat

                i += 1

        return tijdstippen_drietijdslotgaten

    def geef_willekeurig_tijdslot(self) -> Tijdslot:
        """
        Geeft een willekeurig tijdslot uit een students rooster terug.
        """
        return random.choice(list(zaalslot.tijdslot for zaalslot in self.__zaalsloten))

    def wissel_tijdsloten(self, oud_tijdslot: Tijdslot, nieuw_tijdslot: Tijdslot) -> None:
        """
        Wisselt een oud tijdslot in een students rooster met een nieuw tijdslot (van een andere student).
        """
        for activiteit in self.__rooster:
            if activiteit.zaalslot.tijdslot == oud_tijdslot:
                activiteit.zaalslot.tijdslot = nieuw_tijdslot

                break

        for zaalslot in self.__zaalsloten:
            if zaalslot.tijdslot == oud_tijdslot:
                zaalslot.tijdslot = nieuw_tijdslot
                break

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
                    self._tijdstip_naar_integer(activiteit.zaalslot.tijdslot.tijdstip) for activiteit in self.__rooster
                    if (activiteit.zaalslot.tijdslot.weekdag == weekdag)
                )
            )

            if not tijdsloten_op_dag_start_tot_eind or (len(tijdsloten_op_dag_start_tot_eind) == 1):
                continue

            i: int = 0

            while i < (len(tijdsloten_op_dag_start_tot_eind) - 1):
                strafpunten_tussentijdsloten += self._aantal_strafpunten_tijdslot(
                    starttijd=tijdsloten_op_dag_start_tot_eind[i],
                    eindtijd=tijdsloten_op_dag_start_tot_eind[i + 1]
                )

                i += 1

        return strafpunten_tussentijdsloten

    def geef_aantal_ingeroosterde_vakken(self) -> int:
        """
        Geeft het aantal ingeroosterde vakken van een student terug.
        """
        return self.__zaalsloten.__len__()
