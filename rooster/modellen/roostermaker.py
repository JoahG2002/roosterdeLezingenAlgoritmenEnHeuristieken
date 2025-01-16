import sys
import time
import random

from copy import deepcopy
from ctypes import c_double
from colorama import Fore, Style
from typing import Literal, Final, Optional

from .vak import Vak
from ..c_functies import c
from .student import Student
from .tijdslot import Tijdslot
from .zaal import Zaal, Zaalslot
from .activiteit import Activiteit
from .activiteit import Vakactiviteit
from .genetisch import GenetischRooster
from .strafpunt import BundelStrafpunten
from ..dataverwerking.lees import Roosterdata
from ..constanten.constant import tijdeenheden, teksten, maxima
from ..dataverwerking.schrijf import schrijf_voortgang_algoritme


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

        self.__studenten: set[Student] = set(roosterdata.STUDENTEN)

        self.__pad_resultaten_csv: str = roosterdata.PAD_CSV_RESULTATEN
        self.__pad_csv_prestaties_algoritmen: str = roosterdata.PAD_CSV_PRESTATIES_ALGORITMEN
        self.__modus_algoritme: Literal["deterministisch", "hillclimber", "simulatedAnnealing", "genetisch", ''] = roosterdata.MODUS_ALGORITME
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

        def _rooster_activiteit_vak_in(
                vak_: Vak,
                aantal_activiteiten: int,
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
                    vak_.voegt_zaalslot_toe(zaalslot, type__)

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
                vak_.voegt_zaalslot_toe(zaalslot, type__)

                self._voeg_activiteit_toe_aan_rooster(activiteit)
                self._voeg_activiteit_toe_aan_rooster_studenten(activiteit)

        for vak in self.__vakken:
            activiteitaantallen_met_methoden: tuple[tuple[int, Literal["hoorcollege", "werkcollege", "practicum"], int], ...] = (
                (vak.aantal_hoorcolleges, "hoorcollege", vak.aantal_studenten()),
                (vak.aantal_werkcolleges, "werkcollege", vak.aantal_studenten_per_werkcollege),
                (vak.aantal_practica, "practicum", vak.aantal_studenten_per_practicum)
            )

            for aantal, type_, aantal_studenten_per_activiteit in activiteitaantallen_met_methoden:
                if aantal == 0:
                    continue

                _rooster_activiteit_vak_in(
                    vak_=vak,
                    aantal_activiteiten=aantal,
                    type__=type_,
                    aantal_studenten_per_activiteit_=aantal_studenten_per_activiteit
                )

    @staticmethod
    def _geef_willekeurige_wissel(rooster: list[Activiteit | None]) -> Optional[tuple[Activiteit, Activiteit]]:
        """
        Kiest twee willekeurige activiteiten uit het rooster voor een zaalslot wissel.
        """
        activiteiten: list[Activiteit] = [activiteit for activiteit in rooster if activiteit]

        if activiteiten.__len__() < 2:
            return None

        activiteit1_: Activiteit = random.choice(activiteiten)
        activiteit2_: Activiteit = random.choice(activiteiten)

        while activiteit1_.zaalslot.tijdslot == activiteit2_.zaalslot.tijdslot:
            activiteit2_ = random.choice(activiteiten)

        return activiteit1_, activiteit2_

    @staticmethod
    def _update_activiteit_in_rooster(rooster: list[Activiteit | None], activiteit: Activiteit) -> None:
        """
        Updatet een activiteit in het rooster.
        """
        for i, activiteit_ in enumerate(rooster):
            if (activiteit_
                    and (activiteit_.vakactiviteit.vak == activiteit.vakactiviteit.vak)
                    and (activiteit_.vakactiviteit.type == activiteit.vakactiviteit.type)):
                rooster[i] = activiteit
                break

    def _verwissel_activiteiten(self,
                                activiteit1: Activiteit,
                                activiteit2: Activiteit,
                                zaalsloten_ingeroosterd: set[Zaalslot],
                                rooster: list[Activiteit | None],
                                studenten: set[Student],
                                vakken: list[Vak]) -> None:
        """
        Verwisselt de zaalsloten van twee activiteiten.
        """
        if activiteit1.zaalslot in zaalsloten_ingeroosterd:
            zaalsloten_ingeroosterd.remove(activiteit1.zaalslot)
        if activiteit2.zaalslot in zaalsloten_ingeroosterd:
            zaalsloten_ingeroosterd.remove(activiteit2.zaalslot)

        for student in studenten:
            student.verwijder_zaalslot(activiteit1.zaalslot)
            student.verwijder_zaalslot(activiteit2.zaalslot)

        for vak in vakken:
            if vak.naam == activiteit1.vakactiviteit.vak.naam:
                vak.verwijder_zaalslot(activiteit1.zaalslot, activiteit1.vakactiviteit.type)

            if vak.naam == activiteit2.vakactiviteit.vak.naam:
                vak.verwijder_zaalslot(activiteit2.zaalslot, activiteit2.vakactiviteit.type)

        bezette_plaatsen_zaal_activiteit1: int = activiteit1.zaalslot.zaal.bezette_plaatsen
        bezette_plaatsen_zaal_activiteit2: int = activiteit2.zaalslot.zaal.bezette_plaatsen

        tijdelijke_container_zaalslot: Zaalslot = activiteit1.zaalslot
        activiteit1.zaalslot = activiteit2.zaalslot
        activiteit2.zaalslot = tijdelijke_container_zaalslot

        activiteit1.zaalslot.zaal.bezette_plaatsen = bezette_plaatsen_zaal_activiteit1
        activiteit2.zaalslot.zaal.bezette_plaatsen = bezette_plaatsen_zaal_activiteit2

        self._update_activiteit_in_rooster(rooster, activiteit1)
        self._update_activiteit_in_rooster(rooster, activiteit2)

        zaalsloten_ingeroosterd.add(activiteit1.zaalslot)
        zaalsloten_ingeroosterd.add(activiteit2.zaalslot)

        for student in studenten:
            if student.volgt_vak(activiteit1.vakactiviteit.vak.naam):
                student.voeg_activiteit_toe_aan_rooster(activiteit1)

            if student.volgt_vak(activiteit2.vakactiviteit.vak.naam):
                student.voeg_activiteit_toe_aan_rooster(activiteit2)

        for vak in vakken:
            if vak.naam == activiteit1.vakactiviteit.vak.naam:
                vak.voegt_zaalslot_toe(activiteit1.zaalslot, activiteit1.vakactiviteit.type)

            if vak.naam == activiteit2.vakactiviteit.vak.naam:
                vak.voegt_zaalslot_toe(activiteit2.zaalslot, activiteit2.vakactiviteit.type)

    def _is_valide_zaalwissel(self, activiteit1: Activiteit, activiteit2: Activiteit) -> bool:
        """
        Geeft terug of een zaalwissel geldig is – of zalen van beide activiteiten elkaars capaciteit in aan zouden kunnen bij een mogelijke wissel.
        """
        return (self._kan_faciliteren(activiteit1.zaalslot.zaal, activiteit2.vakactiviteit)
                and self._kan_faciliteren(activiteit2.zaalslot.zaal, activiteit1.vakactiviteit))

    @staticmethod
    def _geef_wissel_tijdsloten_studenten(studenten: set[Student]
                                          ) -> tuple[tuple[Student, Tijdslot], tuple[Student, Tijdslot]]:
        """
        Geeft een willekeurige wissel van twee studenten en hun tijdsloten terug, en probeert deze wissel te doen tussen een student met een drietijslotengat in zijn rooster en een zonder.
        """
        def geef_twee_willekeurige_student_tijdslotparen(student_tijdslotpaar1: dict[Student, Tijdslot],
                                                         student_tijdslotpaar2: dict[Student, Tijdslot] | None = None
                                                         ) -> tuple[tuple[Student, Tijdslot], tuple[Student, Tijdslot]]:
            """
            Geeft twee willekeurige tijdsloten van twee studenten terug om te wisselen.
            """
            student1_: Student | None = None
            student2_: Student | None = None
            tijdstip1_: Tijdslot | None = None
            tijdstip2_: Tijdslot | None = None

            student_tijdslotpaar1_: list[tuple[Student, Tijdslot]] = list(student_tijdslotpaar1.items())

            if student_tijdslotpaar2:
                student_tijdslotpaar2_: list[tuple[Student, Tijdslot]] = list(student_tijdslotpaar2.items())
            else:
                student_tijdslotpaar2_: list[tuple[Student, Tijdslot]] = student_tijdslotpaar1_

            while (student1_ == student2_) or (tijdstip1_ == tijdstip2_):
                student1_, tijdstip1_ = random.choice(student_tijdslotpaar1_)
                student2_, tijdstip2_ = random.choice(student_tijdslotpaar2_)

            return (student1_, tijdstip1_), (student2_, tijdstip2_)

        studenten_met_tijdstippen_drietijdslotgaten: dict[Student, list[Tijdslot]] = {
            student: student.geeft_tijdstippen_drietijdslotgaten() for student in studenten
        }
        studenten_met_drietijdslotgaten: dict[Student, Tijdslot] = {
            student: tijdstippen_gaten[0] for student, tijdstippen_gaten in studenten_met_tijdstippen_drietijdslotgaten.items()
            if tijdstippen_gaten
        }
        studenten_met_willekeurig_tijdstip: dict[Student, Tijdslot] = {
            student: student.geef_willekeurig_tijdslot() for student in studenten
        }

        student_tijdslotparen_wissel: tuple[tuple[Student, Tijdslot], tuple[Student, Tijdslot]] = geef_twee_willekeurige_student_tijdslotparen(
            student_tijdslotpaar1=studenten_met_willekeurig_tijdstip,
            student_tijdslotpaar2=studenten_met_drietijdslotgaten if studenten_met_drietijdslotgaten else None
        )

        return ((student_tijdslotparen_wissel[0][0], student_tijdslotparen_wissel[0][1]),
                (student_tijdslotparen_wissel[1][0], student_tijdslotparen_wissel[1][1]))

    @staticmethod
    def _wissel_tijdsloten_studenten(student1_met_tijdslot: tuple[Student, Tijdslot],
                                     student2_met_tijdslot: tuple[Student, Tijdslot]) -> None:
        """
        Wisselt de tijdsloten van twee studenten.
        """
        student1_met_tijdslot[0].wissel_tijdsloten(
            oud_tijdslot=student1_met_tijdslot[1],
            nieuw_tijdslot=student2_met_tijdslot[1]
        )
        student2_met_tijdslot[0].wissel_tijdsloten(
            oud_tijdslot=student2_met_tijdslot[1],
            nieuw_tijdslot=student1_met_tijdslot[1]
        )

    def _geneer_rooster_hillclimbing(self) -> None:
        """
        Geneert een n-aantal rooster door willekeurige zaalsloten te wisselen, en geeft het beste rooster uit dat n-aantal terug — hillclimbing ('bergklimmen').
        """
        huidig_aantal_strafpunten: int = self.__strafpuntenbundel.totaal()
        minste_strafpunten: int = huidig_aantal_strafpunten

        beste_rooster: list[Activiteit | None] = deepcopy(self.__rooster)
        zaalsloten_beste_rooster: set[Zaalslot] = deepcopy(self.__zaalsloten_ingeroosterd)
        studenten_beste_rooster: set[Student] = deepcopy(self.__studenten)
        vakken_beste_rooster: list[Vak] = deepcopy(list(self.__vakken))

        for lus in range(self.__aantal_lussen):
            rooster_huidige_lus: list[Activiteit | None] = deepcopy(beste_rooster)
            zaalsloten_huidige_lus: set[Zaalslot] = deepcopy(zaalsloten_beste_rooster)
            studenten_huidige_lus: set[Student] = deepcopy(studenten_beste_rooster)
            vakken_huidige_lus: list[Vak] = deepcopy(vakken_beste_rooster)

            if minste_strafpunten > maxima.STRAFPUNTENGRENS_VAKWISSELEN_NAAR_STUDENT:
                activiteitenwissel: tuple[Activiteit, Activiteit] | None = self._geef_willekeurige_wissel(rooster_huidige_lus)

                if not activiteitenwissel:
                    continue

                activiteit1, activiteit2 = activiteitenwissel

                if not self._is_valide_zaalwissel(activiteit1, activiteit2):
                    continue

                self._verwissel_activiteiten(
                    activiteit1=activiteit1,
                    activiteit2=activiteit2,
                    zaalsloten_ingeroosterd=zaalsloten_huidige_lus,
                    rooster=rooster_huidige_lus,
                    studenten=studenten_huidige_lus,
                    vakken=vakken_huidige_lus
                )
            else:
                student1_met_tijdslot, student2_met_tijdslot  = self._geef_wissel_tijdsloten_studenten(
                    studenten_huidige_lus
                )
                self._wissel_tijdsloten_studenten(student1_met_tijdslot, student2_met_tijdslot)

            nieuw_aantal_strafpunten: int = BundelStrafpunten(studenten_huidige_lus, rooster_huidige_lus).totaal()

            if nieuw_aantal_strafpunten >= minste_strafpunten:
                continue

            minste_strafpunten = nieuw_aantal_strafpunten

            beste_rooster = deepcopy(rooster_huidige_lus)
            zaalsloten_beste_rooster = deepcopy(zaalsloten_huidige_lus)
            studenten_beste_rooster = deepcopy(studenten_huidige_lus)
            vakken_beste_rooster = deepcopy(vakken_huidige_lus)

            schrijf_voortgang_algoritme(nieuw_aantal_strafpunten, lus, self.__aantal_lussen)

        self.__rooster = beste_rooster
        self.__zaalsloten_ingeroosterd = zaalsloten_beste_rooster
        self.__studenten = studenten_beste_rooster
        self.__vakken = tuple(vakken_beste_rooster)

    def _genereer_rooster_simulated_annealing(self) -> None:
        """
        Genereert een rooster door gebruik te maken van simulated annealing. Deze methode staat slechte oplossingen toe met een kans die naarmate tijd vordert afneemt. Uiteindelijk wordt hierdoor een optimale staat bereikt.
        """
        aanvankelijke_temperatuur: float = 100.0
        aantal_lussen_double: c_double = c_double(self.__aantal_lussen)
        huidig_aantal_strafpunten: int = self.__strafpuntenbundel.totaal()
        laagste_aantal_strafpunten: int = huidig_aantal_strafpunten

        beste_rooster: list[Activiteit | None] = deepcopy(self.__rooster)
        zaalsloten_beste_rooster: set[Zaalslot] = deepcopy(self.__zaalsloten_ingeroosterd)
        studenten_beste_rooster: set[Student] = deepcopy(self.__studenten)
        vakken_beste_rooster: list[Vak] = deepcopy(list(self.__vakken))

        for lus in range(self.__aantal_lussen):
            rooster_huidige_lus: list[Activiteit | None] = deepcopy(self.__rooster)
            zaalsloten_huidige_lus: set[Zaalslot] = deepcopy(self.__zaalsloten_ingeroosterd)
            studenten_huidige_lus: set[Student] = deepcopy(self.__studenten)
            vakken_huidige_lus: list[Vak] = deepcopy(list(self.__vakken))

            activiteitenwissel: tuple[Activiteit, Activiteit] | None = self._geef_willekeurige_wissel(rooster_huidige_lus)

            if not activiteitenwissel:
                continue

            activiteit1, activiteit2 = activiteitenwissel

            if not self._is_valide_zaalwissel(activiteit1, activiteit2):
                continue

            self._verwissel_activiteiten(
                activiteit1=activiteit1,
                activiteit2=activiteit2,
                zaalsloten_ingeroosterd=zaalsloten_huidige_lus,
                rooster=rooster_huidige_lus,
                studenten=studenten_huidige_lus,
                vakken=vakken_huidige_lus
            )

            nieuw_aantal_strafpunten: int = BundelStrafpunten(studenten_huidige_lus, rooster_huidige_lus).totaal()

            temperature: float = c.bereken_temperatuur(
                c_double(lus),
                aantal_lussen_double,
                c_double(aanvankelijke_temperatuur)
            )

            if not c.accepteer_slechtste_oplossing(
                    c_double(huidig_aantal_strafpunten),
                    c_double(nieuw_aantal_strafpunten),
                    c_double(temperature),
                    c_double(random.random())
            ):
                continue

            huidig_aantal_strafpunten = nieuw_aantal_strafpunten

            self.__rooster = deepcopy(rooster_huidige_lus)
            self.__zaalsloten_ingeroosterd = deepcopy(zaalsloten_huidige_lus)
            self.__studenten = deepcopy(studenten_huidige_lus)
            self.__vakken = tuple(vakken_huidige_lus)

            if nieuw_aantal_strafpunten >= laagste_aantal_strafpunten:
                continue

            laagste_aantal_strafpunten = nieuw_aantal_strafpunten

            beste_rooster = deepcopy(rooster_huidige_lus)
            zaalsloten_beste_rooster = deepcopy(zaalsloten_huidige_lus)
            studenten_beste_rooster = deepcopy(studenten_huidige_lus)
            vakken_beste_rooster = deepcopy(vakken_huidige_lus)

            schrijf_voortgang_algoritme(nieuw_aantal_strafpunten, lus, self.__aantal_lussen)

        self.__rooster = beste_rooster
        self.__zaalsloten_ingeroosterd = zaalsloten_beste_rooster
        self.__studenten = studenten_beste_rooster
        self.__vakken = tuple(vakken_beste_rooster)

    def _genereer_rooster_genetisch(self) -> None:
        """
        Genereert een rooster vanuit een genetische benadering:

        1. creëert eem aanvankelijke populatie valide roosters;
        2. evalueert deze vervolgens aan de hand van strafpunten;
        3. kiest de roosters met de beste 'genen';
        4. creëert een mixmutatie van deze roosters;
        5. herhaalt dit tot het n-aantal lussen.
        """
        POPULATIEGROOTTE: int = 50
        GROOTTE_ELITE: int = 5
        MUTATIETEMPO: float = 0.1

        def creeer_los_rooster() -> GenetischRooster:
            """
            Creëert een willekeurig, geldig rooster middels mutaties van het huidige rooster.
            """
            new_rooster: list[Activiteit | None] = deepcopy(self.__rooster)
            new_zaalsloten: set[Zaalslot] = deepcopy(self.__zaalsloten_ingeroosterd)
            new_studenten: set[Student] = deepcopy(self.__studenten)
            new_vakken: list[Vak] = deepcopy(list(self.__vakken))

            for _ in range(int(len(new_rooster) * MUTATIETEMPO)):
                activiteitenwissel_: tuple[Activiteit, Activiteit] | None= self._geef_willekeurige_wissel(new_rooster)

                if not activiteitenwissel_:
                    continue

                activiteit1_, activiteit2_ = activiteitenwissel_

                if not self._is_valide_zaalwissel(activiteit1_, activiteit2_):
                    continue

                self._verwissel_activiteiten(
                    activiteit1=activiteit1_,
                    activiteit2=activiteit2_,
                    zaalsloten_ingeroosterd=new_zaalsloten,
                    rooster=new_rooster,
                    studenten=new_studenten,
                    vakken=new_vakken
                )

            return GenetischRooster(new_rooster, new_zaalsloten, new_studenten, new_vakken)

        def berekent_strafpunten(roosterdata: GenetischRooster) -> int:
            """
            Evalueert de geschiktheid middels het strafpuntensysteem (negatieve straffen voor betere geschiktheid).
            """
            return -1 * BundelStrafpunten(roosterdata.studenten, roosterdata.rooster).totaal()

        def muteer_roosters(data_ouderrooster1: GenetischRooster, data_ouderrooster2: GenetischRooster) -> GenetischRooster:
            """
            Creëert een nieuw rooster uit twee ouderroosters.
            """
            kindrooster: list[Activiteit | None] = deepcopy(data_ouderrooster1.rooster)
            zaalsloten_kindrooster: set[Zaalslot] = deepcopy(data_ouderrooster1.zaalsloten)
            studenten_kindrooster: set[Student] = deepcopy(data_ouderrooster1.studenten)
            vakken_kinderrooster: list[Vak] = deepcopy(data_ouderrooster1.vakken)

            for i in range(len(kindrooster)):
                if (random.random() < 0.5) and data_ouderrooster2.rooster[i]:
                    if kindrooster[i]:
                        oude_activiteit: Activiteit = kindrooster[i]

                        if oude_activiteit.zaalslot in zaalsloten_kindrooster:
                            zaalsloten_kindrooster.remove(oude_activiteit.zaalslot)

                        for student in studenten_kindrooster:
                            student.verwijder_zaalslot(oude_activiteit.zaalslot)

                    nieuwe_activiteit: Activiteit = deepcopy(data_ouderrooster2.rooster[i])
                    kindrooster[i] = nieuwe_activiteit

                    zaalsloten_kindrooster.add(nieuwe_activiteit.zaalslot)

                    for student in studenten_kindrooster:
                        if student.volgt_vak(nieuwe_activiteit.vakactiviteit.vak.naam):
                            student.voeg_activiteit_toe_aan_rooster(nieuwe_activiteit)

            return GenetischRooster(kindrooster, zaalsloten_kindrooster, studenten_kindrooster, vakken_kinderrooster)

        populaties: list[GenetischRooster] = [creeer_los_rooster() for _ in range(POPULATIEGROOTTE)]

        beste_rooster: GenetischRooster | None = None
        beste_geschiktheid: int = -500_000

        for generatie in range(self.__aantal_lussen):
            roosters_met_geschiktheid: list[tuple[GenetischRooster, int]] = [
                (rooster, berekent_strafpunten(rooster)) for rooster in populaties
            ]
            roosters_met_geschiktheid.sort(key=lambda x: x[1], reverse=True)

            if roosters_met_geschiktheid[0][1] > beste_geschiktheid:
                beste_geschiktheid = roosters_met_geschiktheid[0][1]
                beste_rooster = roosters_met_geschiktheid[0][0]

                schrijf_voortgang_algoritme(-beste_geschiktheid, generatie, self.__aantal_lussen)

            nieuwe_populaties: list[GenetischRooster] = [rooster for rooster, _ in roosters_met_geschiktheid[:GROOTTE_ELITE]]

            while len(nieuwe_populaties) < POPULATIEGROOTTE:
                willekeurige_roosters: list[GenetischRooster] = random.sample(roosters_met_geschiktheid, 5)
                ouderrooster1: GenetischRooster = max(willekeurige_roosters, key=lambda x: x[1])[0]

                willekeurige_roosters = random.sample(roosters_met_geschiktheid, 5)
                ouderrooster2: GenetischRooster = max(willekeurige_roosters, key=lambda x: x[1])[0]

                kindrooster_: GenetischRooster = muteer_roosters(ouderrooster1, ouderrooster2)

                if random.random() < MUTATIETEMPO:
                    activiteitenwissel: tuple[Activiteit, Activiteit] | None = self._geef_willekeurige_wissel(kindrooster_.rooster)

                    if activiteitenwissel:
                        activiteit1, activiteit2 = activiteitenwissel

                        if self._is_valide_zaalwissel(activiteit1, activiteit2):
                            self._verwissel_activiteiten(
                                activiteit1=activiteit1,
                                activiteit2=activiteit2,
                                zaalsloten_ingeroosterd=kindrooster_.zaalsloten,
                                rooster=kindrooster_.rooster,
                                studenten=kindrooster_.studenten,
                                vakken=kindrooster_.vakken
                            )

                nieuwe_populaties.append(kindrooster_)

            populaties = nieuwe_populaties

        if beste_rooster:
            self.__rooster = beste_rooster.rooster
            self.__zaalsloten_ingeroosterd = beste_rooster.zaalsloten
            self.__studenten = beste_rooster.studenten
            self.__vakken = beste_rooster.vakken

    def genereer_rooster(self) -> None:
        """
        Genereert een rooster voor een gegeven tuple vakactiviteiten.
        """
        self.start_genereren = time.time()

        self._genereer_basisrooster()
        self._bereken_strafpunten()

        if self.__modus_algoritme == "hillclimber":
            self._geneer_rooster_hillclimbing()

        if self.__modus_algoritme == "simulatedAnnealing":
            self._genereer_rooster_simulated_annealing()

        if self.__modus_algoritme == "genetisch":
            self._genereer_rooster_genetisch()

        self._bereken_strafpunten()

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
