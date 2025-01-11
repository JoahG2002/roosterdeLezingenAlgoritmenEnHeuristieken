import sys
import time
import random

from colorama import Fore, Style
from typing import Literal, Final, Optional

from .vak import Vak
from .student import Student
from .tijdslot import Tijdslot
from .zaal import Zaal, Zaalslot
from .activiteit import Activiteit
from .strafpunt import BundelStrafpunten
from .activiteit import Vakactiviteit
from ..dataverwerking.lees import Roosterdata
from ..constants.constant import tijdeenheden, teksten


class Roostermaker:
    __slots__: tuple[str, ...] = (
        "__ZALEN", "__vakken", "__TIJDSLOTEN", "__rooster", "__pad_resultaten_csv", "__studenten", "__strafpuntenbundel",
        "__aantal_ingeroosterde_tijdsloten", "__aantal_plaatsen_rooster", "__zaalsloten_ingeroosterd", "__index_zalen",
        "__index_tijdsloten", "__modus_algoritme", "__aantal_lussen", "__pad_csv_prestaties_algoritmen", "start_genereren",
        "duur_genereren_seconden"
    )

    def __init__(self, roosterdata: Roosterdata) -> None:
        self.__ZALEN: tuple[Zaal, ...] = self._sorteer_zalen(roosterdata.ZALEN)
        self.__vakken: tuple[Vak, ...] = self._sorteer_vakken_op_grootte(roosterdata.VAKKEN)
        self.__studenten: tuple[Student, ...] = roosterdata.STUDENTEN
        self.__pad_resultaten_csv: str = roosterdata.PAD_CSV_RESULTATEN
        self.__pad_csv_prestaties_algoritmen: str = roosterdata.PAD_CSV_PRESTATIES_ALGORITMEN
        self.__modus_algoritme: str = roosterdata.MODUS_ALGORITME
        self.__aantal_lussen: int = roosterdata.AANTAL_LUSSEN

        self.__TIJDSLOTEN: Final[tuple[Tijdslot, ...]] = (
            Tijdslot(weekdag="maandag", tijdstip="09.00–11.00"), Tijdslot(weekdag="maandag", tijdstip="11.00–13.00"),
            Tijdslot(weekdag="maandag", tijdstip="13.00–15.00"), Tijdslot(weekdag="maandag", tijdstip="15.00–17.00"),
            Tijdslot(weekdag="maandag", tijdstip="17.00–19.00"), Tijdslot(weekdag="dinsdag", tijdstip="09.00–11.00"),
            Tijdslot(weekdag="dinsdag", tijdstip="11.00–13.00"), Tijdslot(weekdag="dinsdag", tijdstip="13.00–15.00"),
            Tijdslot(weekdag="dinsdag", tijdstip="15.00–17.00"), Tijdslot(weekdag="dinsdag", tijdstip="17.00–19.00"),
            Tijdslot(weekdag="woensdag", tijdstip="09.00–11.00"), Tijdslot(weekdag="woensdag", tijdstip="11.00–13.00"),
            Tijdslot(weekdag="woensdag", tijdstip="13.00–15.00"), Tijdslot(weekdag="woensdag", tijdstip="15.00–17.00"),
            Tijdslot(weekdag="woensdag", tijdstip="17.00–19.00"), Tijdslot(weekdag="donderdag", tijdstip="09.00–11.00"),
            Tijdslot(weekdag="donderdag", tijdstip="11.00–13.00"), Tijdslot(weekdag="donderdag", tijdstip="13.00–15.00"),
            Tijdslot(weekdag="donderdag", tijdstip="15.00–17.00"), Tijdslot(weekdag="donderdag", tijdstip="17.00–19.00"),
            Tijdslot(weekdag="vrijdag", tijdstip="09.00–11.00"), Tijdslot(weekdag="vrijdag", tijdstip="11.00–13.00"),
            Tijdslot(weekdag="vrijdag", tijdstip="13.00–15.00"), Tijdslot(weekdag="vrijdag", tijdstip="15.00–17.00"),
            Tijdslot(weekdag="vrijdag", tijdstip="17.00–19.00")
        )

        self.__aantal_ingeroosterde_tijdsloten: int = 0
        self.__aantal_plaatsen_rooster: int = len(self.__ZALEN) * len(self.__TIJDSLOTEN)
        self.__rooster: list[Activiteit | None] = [None] * self.__aantal_plaatsen_rooster
        self.__zaalsloten_ingeroosterd: set[Zaalslot] = set()

        self.__strafpuntenbundel: BundelStrafpunten | None = None

        self.__index_zalen: int = 0
        self.__index_tijdsloten: int = 0

        self.start_genereren: float = 0.0
        self.duur_genereren_seconden: float = 0.0

    @staticmethod
    def _sorteer_zalen(zalen: tuple[Zaal, ...]) -> tuple[Zaal, ...]:
        """
        Sorteert de zalen van groot naar klein — zodat de grote zalen eerder gebruikt kunnen worden voor de hoorcolleges.
        """
        return tuple(sorted(zalen, key=lambda x: x.capaciteit, reverse=True))

    @staticmethod
    def _sorteer_vakken_op_grootte(vakken: tuple[Vak, ...]) -> tuple[Vak, ...]:
        """
        Sorteert de vakken op grootte — de groten eerst.
        """
        return tuple(sorted(vakken, key=lambda x: x.aantal_studenten(), reverse=True))

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
        def vind_geschikt_zaalslot(vak_activiteit: Vakactiviteit) -> Optional[tuple[Zaalslot, int, int]]:
            """
            Vindt een geschikte zaal en tijdslot voor de gegeven activiteit of None als geen gevonden is.
            """
            index_tijdslot_index: int = self.__index_tijdsloten
            index_zaal: int = self.__index_zalen

            for i in range(len(self.__TIJDSLOTEN)):
                for j in range(len(self.__ZALEN)):
                    if index_tijdslot_index >= len(self.__TIJDSLOTEN):
                        index_tijdslot_index = 0

                    if index_zaal >= len(self.__ZALEN):
                        index_zaal = 0

                    zaalslot: Zaalslot = Zaalslot(self.__TIJDSLOTEN[index_tijdslot_index], self.__ZALEN[index_zaal])

                    if not self._is_al_ingeroosterd(zaalslot) and self._kan_faciliteren(zaalslot.zaal, vak_activiteit):
                        return zaalslot, index_zaal, index_tijdslot_index

                    index_zaal += 1

                index_tijdslot_index += 1
                index_zaal = 0

            return None

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
                    vakactiviteit: Vakactiviteit = Vakactiviteit(vak_, type__)
                    geschikt_zaalslot: tuple[Zaalslot, int, int] | None = vind_geschikt_zaalslot(vakactiviteit)

                    if not geschikt_zaalslot:
                        continue

                    zaalslot, index_nieuwe_zaal, index_tijdslot = geschikt_zaalslot

                    self.__index_zalen = (index_nieuwe_zaal + 1)
                    self.__index_tijdsloten = (index_tijdslot + 1)

                    activiteit: Activiteit = Activiteit(zaalslot, vakactiviteit, vak.aantal_studenten())
                    getattr(vak_, toevoegmethode)(zaalslot)

                    self._voeg_activiteit_toe_aan_rooster(activiteit)
                    self._voeg_activiteit_toe_aan_rooster_studenten(activiteit)

                    return

            groepgrootten_werkcollege: list[int] = self._verdeel_studenten_over_werkgroepen(
                totaalaantal_studenten=vak_.aantal_studenten(),
                maximumaantal_studenten_groep=aantal_studenten_per_activiteit_
            )

            for aantal_studenten_activiteit in groepgrootten_werkcollege:
                vakactiviteit: Vakactiviteit = Vakactiviteit(vak_, type__)
                geschikt_zaalslot: tuple[Zaalslot, int, int] | None = vind_geschikt_zaalslot(vakactiviteit)

                if not geschikt_zaalslot:
                    continue

                zaalslot, index_nieuwe_zaal, index_tijdslot = geschikt_zaalslot

                self.__index_zalen = (index_nieuwe_zaal + 1)
                self.__index_tijdsloten = (index_tijdslot + 1)

                activiteit: Activiteit = Activiteit(zaalslot, vakactiviteit, aantal_studenten_activiteit)
                getattr(vak_, toevoegmethode)(zaalslot)

                self._voeg_activiteit_toe_aan_rooster(activiteit)
                self._voeg_activiteit_toe_aan_rooster_studenten(activiteit)

        for vak in self.__vakken:
            activiteitaantallen_met_methoden: tuple[tuple[int, str, Literal["hoorcollege", "werkcollege", "practicum"], int], ...] = (
                (vak.aantal_hoorcolleges, "voeg_hoorcollege_toe", "hoorcollege", vak.aantal_studenten()),
                (vak.aantal_werkcolleges, "voeg_werkcollege_toe", "werkcollege", vak.aantal_studenten_per_werkcollege),
                (vak.aantal_practica, "voeg_practicum_toe", "practicum", vak.aantal_studenten_per_practicum)
            )

            for aantal, methode, type_, aantal_studenten_per_activiteit in activiteitaantallen_met_methoden:
                if aantal == 0:
                    continue

                rooster_activiteit_vak_in(
                    vak_=vak,
                    aantal_activiteiten=aantal,
                    toevoegmethode=methode,
                    type__=type_,
                    aantal_studenten_per_activiteit_=aantal_studenten_per_activiteit
                )

    def _geneer_rooster_hillclimbing(self) -> None:
        """
        Geneert een n-aantal rooster met, en geeft het beste rooster uit dat n-aantal terug — hillclimbing ('bergklimmen').
        """
        def verwissel_activiteiten(index_activiteit1: int, index_activiteit2: int) -> None:
            """
            Verwisselt de posities van twee activiteiten.
            """
            tijdelijke_container_activiteit: Activiteit = self.__rooster[index_activiteit1]
            self.__rooster[index_activiteit1] = self.__rooster[index_activiteit2]
            self.__rooster[index_activiteit2] = tijdelijke_container_activiteit

            if self.__rooster[index_activiteit1]:
                self.__zaalsloten_ingeroosterd.add(self.__rooster[index_activiteit1].zaalslot)
            if self.__rooster[index_activiteit2]:
                self.__zaalsloten_ingeroosterd.add(self.__rooster[index_activiteit2].zaalslot)

        def is_valide_wissel(index_activiteit1: int, index_activiteit2: int) -> bool:
            """
            Geeft terug of een positiewissel geldig is.
            """
            activiteit1: Activiteit = self.__rooster[index_activiteit1]
            activiteit2: Activiteit = self.__rooster[index_activiteit2]

            if (activiteit1 is None) or (activiteit2 is None):
                return True

            zaal1: Zaal = self.__rooster[index_activiteit1].zaalslot.zaal
            zaal2: Zaal = self.__rooster[index_activiteit2].zaalslot.zaal

            if not self._kan_faciliteren(zaal1, activiteit1.vakactiviteit):
                return False
            if not self._kan_faciliteren(zaal2, activiteit2.vakactiviteit):
                return False

            return True

        def bereken_strafpunten_lus() -> int:
            """
            Berekent het aantal strafpunten van de huidige lus.
            """
            self._bereken_strafpunten()

            return self.__strafpuntenbundel.totaal()

        huidig_aantal_strafpunten: int = bereken_strafpunten_lus()
        minste_aantal_strafpunten: int = huidig_aantal_strafpunten
        beste_rooster: list[Activiteit | None] = self.__rooster[:]

        for lus in range(self.__aantal_lussen):
            willekeurige_index1: int = random.randint(0, (self.__aantal_plaatsen_rooster - 1))
            willekeurige_index2: int = random.randint(0, (self.__aantal_plaatsen_rooster - 1))

            if not is_valide_wissel(willekeurige_index1, willekeurige_index2):
                continue

            verwissel_activiteiten(willekeurige_index1, willekeurige_index2)

            vorige_rooster: list[Activiteit | None] = self.__rooster[:]
            vorige_zaalsloten: set[Zaalslot] = self.__zaalsloten_ingeroosterd.copy()

            nieuw_aantal_strafpunten: int = bereken_strafpunten_lus()

            if nieuw_aantal_strafpunten < huidig_aantal_strafpunten:
                huidig_aantal_strafpunten = nieuw_aantal_strafpunten

                if nieuw_aantal_strafpunten < minste_aantal_strafpunten:
                    minste_aantal_strafpunten = nieuw_aantal_strafpunten
                    beste_rooster = self.__rooster[:]

                    sys.stdout.write(
                        f"\nRooster verbeterd! Huidige aantal strafpunten:"
                        f" {Fore.GREEN}{nieuw_aantal_strafpunten}{Style.RESET_ALL}\n"
                    )

                continue

            self.__rooster = vorige_rooster
            self.__zaalsloten_ingeroosterd = vorige_zaalsloten

        self.__rooster = beste_rooster
        self._bereken_strafpunten()

    def genereer_rooster(self) -> None:
        """
        Genereert een rooster voor een gegeven tuple vakactiviteiten.
        """
        self.start_genereren = time.time()
        self._genereer_basisrooster()

        if self.__modus_algoritme == "hillclimber":
            self._geneer_rooster_hillclimbing()

        self.duur_genereren_seconden = (time.time() - self.start_genereren)

    def is_valide_rooster(self) -> bool:
        """
        Geeft terug of het rooster valide is, of iedere activiteit van ieder vak is ingeroosterd.
        """
        return all(vak.alle_activiteiten_ingeroosterd() for vak in self.__vakken)

    def print_rooster(self) -> None:
        """
        Print het rooster naar de stdout (de standaarduitvoerstroom).
        """
        if not self.__rooster:
            raise ValueError("Geen rooster is not gegenereerd; printen onmogelijk.")

        for dag in tijdeenheden.WEEKDAGEN:
            sys.stdout.write(f"\n{dag.upper()}\n{'-' * 110}\n")

            for activiteit in self.__rooster:
                if not activiteit:
                    continue

                if activiteit.zaalslot.tijdslot.weekdag == dag:
                    sys.stdout.write(
                        f"- {Fore.BLUE}{activiteit.zaalslot.zaal.naam}: {Fore.MAGENTA}{activiteit.vakactiviteit.vak.naam} "
                        f"{Fore.YELLOW}({activiteit.vakactiviteit.type}){Style.RESET_ALL} {activiteit.grootte_groep} studenten\n"
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
        self.__strafpuntenbundel: BundelStrafpunten = BundelStrafpunten(studenten=self.__studenten, rooster=self.__rooster)

    def print_strafpunten(self) -> None:
        """
        Print de strafpunten van het rooster.
        """
        if not self.__strafpuntenbundel:
            self._bereken_strafpunten()

        sys.stdout.write(f"\nSTRAFPUNTEN ROOSTER\n{'-' * 85}\n")

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
                f"{self.__aantal_lussen},{self.__strafpuntenbundel.totaal()},{self.duur_genereren_seconden}\n"
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

                for activiteit in student.geef_rooster():
                    vakken_met_huidig_werkcollege[activiteit.vakactiviteit.vak.naam][activiteit.vakactiviteit.type] += 1

                    csv_bestand.write(
                        f"{student.volledige_naam},{activiteit.vakactiviteit.vak.naam},"
                        f"{activiteit.vakactiviteit.type}{vakken_met_huidig_werkcollege[activiteit.vakactiviteit.vak.naam][activiteit.vakactiviteit.type]},"
                        f"{activiteit.zaalslot.zaal.naam},{activiteit.zaalslot.tijdslot.weekdag},{activiteit.zaalslot.tijdslot.tijdstip} uur\n"
                    )
