import sys
import random

from colorama import Fore, Style
from typing import Literal, Final

from .vak import Vak
from .student import Student
from .tijdslot import Tijdslot
from .zaal import Zaal, Zaalslot
from .activiteit import Activiteit
from .strafpunt import BundelStrafpunten
from .activiteit import Vakactiviteit
from ..dataverwerking.lees import Roosterdata
from ..constants.constant import returncodes, tijdeenheden, teksten


class Roostermaker:
    __slots__: tuple[str, ...] = (
        "__zalen", "__vakken", "TIJDSLOTEN", "__rooster", "__pad_resultaten_csv", "__studenten", "__strafpuntenbundel",
        "__aantal_ingeroosterde_tijdsloten", "__aantal_plaatsen_rooster", "__zaalsloten_ingeroosterd", "__index_zalen",
        "__index_tijdsloten", "__modus_algoritme", "__aantal_lussen", "__pad_csv_prestaties_algoritmen"
    )

    def __init__(self, roosterdata: Roosterdata) -> None:
        self.__zalen: tuple[Zaal, ...] = self._sorteer_zalen(roosterdata.ZALEN)
        self.__vakken: tuple[Vak, ...] = roosterdata.VAKKEN
        self.__studenten: tuple[Student, ...] = roosterdata.STUDENTEN
        self.__pad_resultaten_csv: str = roosterdata.PAD_CSV_RESULTATEN
        self.__pad_csv_prestaties_algoritmen: str = roosterdata.PAD_CSV_PRESTATIES_ALGORITMEN

        self.TIJDSLOTEN: Final[tuple[Tijdslot, ...]] = (
            Tijdslot(weekdag="maandag", tijdstip="09.00–11.00"), Tijdslot(weekdag="maandag", tijdstip="11.00–13.00"),
            Tijdslot(weekdag="maandag", tijdstip="13.00–15.00"), Tijdslot(weekdag="maandag", tijdstip="15.00–17.00"),
            Tijdslot(weekdag="dinsdag", tijdstip="09.00–11.00"), Tijdslot(weekdag="dinsdag", tijdstip="11.00–13.00"),
            Tijdslot(weekdag="dinsdag", tijdstip="13.00–15.00"), Tijdslot(weekdag="dinsdag", tijdstip="15.00–17.00"),
            Tijdslot(weekdag="woensdag", tijdstip="09.00–11.00"), Tijdslot(weekdag="woensdag", tijdstip="11.00–13.00"),
            Tijdslot(weekdag="woensdag", tijdstip="13.00–15.00"), Tijdslot(weekdag="woensdag", tijdstip="15.00–17.00"),
            Tijdslot(weekdag="donderdag", tijdstip="09.00–11.00"), Tijdslot(weekdag="donderdag", tijdstip="11.00–13.00"),
            Tijdslot(weekdag="donderdag", tijdstip="13.00–15.00"), Tijdslot(weekdag="donderdag", tijdstip="15.00–17.00"),
            Tijdslot(weekdag="vrijdag", tijdstip="09.00–11.00"), Tijdslot(weekdag="vrijdag", tijdstip="11.00–13.00"),
            Tijdslot(weekdag="vrijdag", tijdstip="13.00–15.00"), Tijdslot(weekdag="vrijdag", tijdstip="15.00–17.00"),
            Tijdslot(weekdag="vrijdag", tijdstip="17.00–19.00")
        )

        self.__aantal_ingeroosterde_tijdsloten: int = 0
        self.__aantal_plaatsen_rooster: int = len(self.__zalen) * len(self.TIJDSLOTEN)
        self.__rooster: list[Activiteit | None] = [None] * self.__aantal_plaatsen_rooster
        self.__zaalsloten_ingeroosterd: set[Zaalslot] = set()

        self.__strafpuntenbundel: BundelStrafpunten | None = None

        self.__index_zalen: int = 0
        self.__index_tijdsloten: int = 0
        self.__aantal_lussen: int = 0

        self.__modus_algoritme: str = "onbekend"

    @staticmethod
    def _sorteer_zalen(zalen: tuple[Zaal, ...]) -> tuple[Zaal, ...]:
        """
        Sorteert de zalen van groot naar klein — zodat de grote zalen eerder gebruikt kunnen worden voor de hoorcolleges.
        """
        zaalnamen_met_grootten: dict[str, int] = {zaal.naam: zaal.capaciteit for zaal in zalen}
        zalen_gesorteerd: list[tuple[str, int]] = sorted(zaalnamen_met_grootten.items(), key=lambda x: x[1])

        zalen_gesorteerd_: list[Zaal | None] = [None] * zalen.__len__()

        for i, zaalnaam_met_grootte in enumerate(zalen_gesorteerd):
            for zaal in zalen:
                if zaal.naam == zaalnaam_met_grootte[0]:
                    zalen_gesorteerd_[i] = zaal
                    break

        return tuple(zalen_gesorteerd_)

    def _is_al_ingeroosterd(self, zaalslot: Zaalslot) -> bool:
        """
        Geeft terug of een tijd-zaalcombinaties (zaalslot) vrij is — of er nog geen vakactiviteit is ingeroosterd voor een bepaalde zaal op een gegeven tijdstip.
        """
        return zaalslot in self.__zaalsloten_ingeroosterd

    @staticmethod
    def _kan_faciliteren(zaal: Zaal, vakactiviteit: Vakactiviteit) -> bool:
        """
        Geeft terug of een zaal een bepaalde vakactiviteit kan faciliteren — of de zaal genoeg zitplaatsen heeft voor het vereiste aantal studenten.
        """
        if vakactiviteit.type == "hoorcollege":
            return zaal.capaciteit >= vakactiviteit.vak.aantal_studenten()

        if vakactiviteit.type == "werkcollege":
            return zaal.capaciteit >= vakactiviteit.vak.aantal_studenten_per_werkcollege

        return zaal.capaciteit >= vakactiviteit.vak.aantal_studenten_per_practicum

    def _voeg_activiteit_toe_aan_rooster_studenten(self, activiteit: Activiteit) -> None:
        """
        Voegt een ingeroosterde vakactiviteit toe aan de persoonlijke roosters van iedere student die het vak van de activiteit volgt.
        """
        for student in self.__studenten:
            if not student.volgt_vak(activiteit.vakactiviteit.vak.naam):
                continue

            student.voeg_activiteit_toe_aan_rooster(activiteit)

    def _voeg_activiteit_toe_aan_rooster(self, activiteit: Activiteit) -> None:
        """
        Voegt een vak toe aan het hoofdrooster.
        """
        self.__rooster[self.__aantal_ingeroosterde_tijdsloten] = activiteit
        self.__aantal_ingeroosterde_tijdsloten += 1

        self.__zaalsloten_ingeroosterd.add(activiteit.zaalslot)

    # def rooster_activiteit_in(self, vakactiviteit: Vakactiviteit) -> Literal[0, -1]:
    #     """
    #     Poogt een activiteit in te roosteren, en geeft met een returncode terug of dit is gelukt.
    #     """
    #     for tijdslot in self.TIJDSLOTEN:
    #         for zaal in self.__zalen:
    #             zaalslot: Zaalslot = Zaalslot(tijdslot, zaal)
    #
    #             if self._is_al_ingeroosterd(zaalslot):
    #                 continue
    #
    #             if not self._kan_faciliteren(zaal, vakactiviteit):
    #                 continue
    #
    #             self._voeg_activiteit_toe_aan_rooster(zaalslot, vakactiviteit)
    #             self._voeg_activiteit_toe_aan_rooster_studenten(zaalslot, vakactiviteit)
    #
    #             return returncodes.SUCCES
    #
    #     return returncodes.MISLUKT

    @staticmethod
    def _verdeel_studenten_over_werkgroepen(totaalaantal_studenten: int, maximumaantal_studenten_groep: int) -> list[int]:
        """
        Verdeelt de studenten van een vak over de verschillende werkgroepen van het vak per werkgroepmoment, en geeft de grootte van iedere werkgroep terug.
        """
        werkgroepen: list[int] = []

        while totaalaantal_studenten > 0:
            werkgroepen.append(min(maximumaantal_studenten_groep, totaalaantal_studenten))

            totaalaantal_studenten -= maximumaantal_studenten_groep

        return werkgroepen

    def _genereer_basisrooster(self) -> None:
        """
        Genereert een startpunt voor het rooster.
        """
        def rooster_activiteit_vak_in(
                vak_: Vak,
                aantal_activiteiten: int,
                toevoegmethode: str,
                type__: Literal["hoorcollege", "werkcollege", "practicum"],
                aantal_studenten_per_activiteit_: int
        ) -> None:
            """
            Roostert de activiteiten van een vak in voor een bepaald type activiteit.
            """
            if aantal_activiteiten == 0:
                return

            if type__ == "hoorcollege":
                for _ in range(aantal_activiteiten):
                    if self.__index_tijdsloten == len(self.TIJDSLOTEN):
                        self.__index_tijdsloten = 0  # overschrijf
                    if self.__index_zalen == len(self.__zalen):
                        self.__index_zalen = 0

                    zaalslot: Zaalslot = Zaalslot(self.TIJDSLOTEN[self.__index_tijdsloten], self.__zalen[self.__index_zalen])
                    activiteit: Activiteit = Activiteit(zaalslot, Vakactiviteit(vak_, type__), vak_.aantal_studenten())

                    getattr(vak_, toevoegmethode)(zaalslot)

                    self._voeg_activiteit_toe_aan_rooster(activiteit)
                    self._voeg_activiteit_toe_aan_rooster_studenten(activiteit)

                    self.__index_zalen += 1
                    self.__index_tijdsloten += 1

            groepgrootten_werkcollege: list[int] = self._verdeel_studenten_over_werkgroepen(
                totaalaantal_studenten=vak_.aantal_studenten(),
                maximumaantal_studenten_groep=aantal_studenten_per_activiteit_
            )

            for aantal_studenten_activiteit in groepgrootten_werkcollege:
                if self.__index_tijdsloten == len(self.TIJDSLOTEN):
                    self.__index_tijdsloten = 0  # overschrijf
                if self.__index_zalen == len(self.__zalen):
                    self.__index_zalen = 0

                zaalslot: Zaalslot = Zaalslot(self.TIJDSLOTEN[self.__index_tijdsloten], self.__zalen[self.__index_zalen])
                activiteit: Activiteit = Activiteit(zaalslot, Vakactiviteit(vak_, type__), aantal_studenten_activiteit)

                getattr(vak_, toevoegmethode)(zaalslot)

                self._voeg_activiteit_toe_aan_rooster(activiteit)
                self._voeg_activiteit_toe_aan_rooster_studenten(activiteit)

                self.__index_zalen += 1
                self.__index_tijdsloten += 1

        for vak in self.__vakken:
            activiteitaantallen_met_methode: tuple[tuple[int, str, Literal["hoorcollege", "werkcollege", "practicum"], int], ...] = (
                (vak.aantal_hoorcolleges, "voeg_hoorcollege_toe", "werkcollege", 0),
                (vak.aantal_werkcolleges, "voeg_werkcollege_toe", "hoorcollege", vak.aantal_studenten_per_werkcollege),
                (vak.aantal_practica, "voeg_practicum_toe", "practicum", vak.aantal_studenten_per_practicum)
            )

            for aantal, methode, type_, aantal_studenten_per_activiteit in activiteitaantallen_met_methode:
                rooster_activiteit_vak_in(
                    vak_=vak,
                    aantal_activiteiten=aantal,
                    toevoegmethode=methode,
                    type__=type_,
                    aantal_studenten_per_activiteit_=aantal_studenten_per_activiteit
                )

    def genereer_rooster(self,
                         modus: Literal["deterministisch", "hillcimber"],
                         aantal_lussen: int) -> None:
        """
        Genereert een rooster voor een gegeven tuple vakactiviteiten.
        """
        self.__aantal_lussen: int = aantal_lussen

        if modus == "deterministisch":
            self._genereer_basisrooster()

        if modus == "hillclimber":
            self._genereer_basisrooster()

    def print_rooster(self) -> None:
        """
        Print het rooster naar de stdout (de standaarduitvoerstroom).
        """
        if not self.__rooster:
            raise ValueError("Geen rooster is not gegenereerd; printen onmogelijk.")

        for dag in tijdeenheden.WEEKDAGEN:
            sys.stdout.write(f"\n{dag.upper()}\n{'-' * 110}\n")

            for roosterslot in self.__rooster:
                if not roosterslot:
                    continue

                zaalslot, vakactiviteit, grootte_groep = roosterslot

                if zaalslot.tijdslot.weekdag == dag:
                    sys.stdout.write(
                        f"- {Fore.BLUE}{zaalslot.zaal.naam}: {Fore.MAGENTA}{vakactiviteit.vak.naam} "
                        f"{Fore.YELLOW}({vakactiviteit.type}){Style.RESET_ALL} {grootte_groep} studenten\n"
                    )

    def print_alle_studentroosters(self) -> None:
        """
        Print het rooster van iedere student.
        """
        for student in self.__studenten:
            student.print_rooster()

    def _bereken_strafpunten(self) -> None:
        """
        Berekent het aantal strafpunten van de huidige roosterconfiguratie terug als bundel strafpuntcategoriën
        """
        if self.__strafpuntenbundel:
            return

        self.__strafpuntenbundel: BundelStrafpunten = BundelStrafpunten(studenten=self.__studenten, rooster=self.__rooster)

    def print_strafpunten(self) -> None:
        """
        Print de strafpunten van het rooster.
        """
        if not self.__strafpuntenbundel:
            self._bereken_strafpunten()

        sys.stdout.write(f"f\nSTRAFPUNTEN ROOSTER\n{'-' * 85}\n")

        sys.stdout.write(
            f"\n- {Fore.BLUE}roostergaten{Style.RESET_ALL}: {Fore.RED}{self.__strafpuntenbundel.roostergaten}{Style.RESET_ALL};\n"
            f"- {Fore.BLUE}avondactiviteiten{Style.RESET_ALL}: {Fore.RED}{self.__strafpuntenbundel.avondactiviteiten}{Style.RESET_ALL};\n"
            f"- {Fore.BLUE}zaal vol{Style.RESET_ALL}: {Fore.RED}{self.__strafpuntenbundel.overvolle_zalen}{Style.RESET_ALL};\n"
            f"- {Fore.BLUE}dubbel ingeroosterd{Style.RESET_ALL}: {Fore.RED}{self.__strafpuntenbundel.dubbel_ingeroosterd}{Style.RESET_ALL}.\n"
            f"\n{Fore.LIGHTYELLOW_EX}TOTAAL: {Fore.RED}{self.__strafpuntenbundel.totaal()}{Style.RESET_ALL}.\n\n"
        )

    def prestatie_algoritme_naar_csv(self) -> None:
        """
        Slaat de prestatie van een roostergeneratiealgortime op in csv-formaat.
        """
        if not self.__strafpuntenbundel:
            self._bereken_strafpunten()

        with open(self.__pad_csv_prestaties_algoritmen, 'a', encoding="utf-8") as csv_bestand_prestaties:
            csv_bestand_prestaties.write(
                f"{self.__modus_algoritme},{self.__strafpuntenbundel.dubbel_ingeroosterd},"
                f"{self.__strafpuntenbundel.roostergaten},{self.__strafpuntenbundel.ongebruikte_tijdsloten},"
                f"{self.__strafpuntenbundel.avondactiviteiten},{self.__strafpuntenbundel.overvolle_zalen},"
                f"{self.__aantal_lussen},{self.__strafpuntenbundel.totaal()}\n"
            )

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
                    naam_vak: {"practicum": 0, "hoorcollege": 0, "werkcollege": 0} for naam_vak in student.geef_vaknamen()
                }

                for zaalslot, activiteit in student.geef_rooster():
                    vakken_met_huidig_werkcollege[activiteit.vak.naam][activiteit.type] += 1

                    csv_bestand.write(
                        f"{student.volledige_naam},{activiteit.vak.naam},"
                        f"{activiteit.type}{vakken_met_huidig_werkcollege[activiteit.vak.naam][activiteit.type]},"
                        f"{zaalslot.zaal.naam},{zaalslot.tijdslot.weekdag},{zaalslot.tijdslot.tijdstip} uur\n"
                    )
