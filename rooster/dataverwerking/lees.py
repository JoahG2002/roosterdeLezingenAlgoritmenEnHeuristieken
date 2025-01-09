import os

from threading import Thread
from polars import read_csv, DataFrame

from ..modellen.vak import Vak
from ..modellen.zaal import Zaal
from ..modellen.student import Student


class Roosterdata:
    __slots__: tuple[str, ...] = (
        "__PAD_VAKDATA_CSV", "__PAD_ZAALDATA_CSV", "__PAD_STUDENT_VAKKENDATA_CSV", "VAKKEN", "ZALEN",
        "__student_vakdata_ingelezen", "PAD_CSV_RESULTATEN", "STUDENTEN", "NAAM_NAAR_VAK"
    )

    def __init__(self, argv: list[str]) -> None:
        self.__PAD_VAKDATA_CSV: str = ''
        self.__PAD_ZAALDATA_CSV: str = ''
        self.__PAD_STUDENT_VAKKENDATA_CSV: str = ''
        self.PAD_CSV_RESULTATEN: str = ''

        self.VAKKEN: tuple[Vak, ...] | None = None
        self.ZALEN: tuple[Zaal, ...] | None = None
        self.STUDENTEN: tuple[Student, ...] | None = None

        self._vind_csv_paden(argv)
        self._lees_roosterdata()

    def _vind_csv_paden(self, argv: list[str]) -> None:
        """
        Vindt de csv-bestandpaden in de argv.
        """
        i: int = 1

        while i < argv.__len__():
            if argv[i] == "--vakken":
                self.__PAD_VAKDATA_CSV = argv[i + 1].strip()

                i += 2
                continue

            if argv[i] == "--zalen":
                self.__PAD_ZAALDATA_CSV = argv[i + 1].strip()

                i += 2
                continue

            if argv[i] == "--sv":
                self.__PAD_STUDENT_VAKKENDATA_CSV = argv[i + 1].strip()

                i += 2
                continue

            if argv[i] == "--resultaat":
                self.PAD_CSV_RESULTATEN = argv[i + 1].strip()

                i += 2

            i += 1

    def inlezen_geslaagd(self) -> bool:
        """
        Geeft terug of het inlezen van alle csv-databestanden is geslaagd.
        """
        return bool(self.VAKKEN and self.ZALEN and self.STUDENTEN)

    def _alle_csv_bestanden_bestaan(self) -> bool:
        """
        Geeft terug of ieder csv-bestandpad bestaat.
        """
        if not os.path.exists(self.__PAD_ZAALDATA_CSV):
            return False

        if not os.path.exists(self.__PAD_VAKDATA_CSV):
            return False

        if not os.path.exists(self.__PAD_STUDENT_VAKKENDATA_CSV):
            return False

        return True

    def _lees_vakdata(self) -> None:
        """
        Leest de vakdata in uit het csv-bestand.
        """
        dataframe_vakken: DataFrame = read_csv(self.__PAD_VAKDATA_CSV, infer_schema=35, encoding="utf8")

        self.VAKKEN = tuple(
            Vak(
                naam=dataframe_vakken["Vak"][i],
                aantal_hoorcolleges=dataframe_vakken["#Hoorcolleges"][i],
                aantal_werkcolleges=dataframe_vakken["#Werkcolleges"][i],
                aantal_studenten_per_werkcollege=dataframe_vakken["Max. stud. Werkcollege"][i],
                aantal_practica=dataframe_vakken["#Practica"][i],
                aantal_studenten_per_practicum=dataframe_vakken["Max. stud. Practicum"][i],
                verwacht_aantal_student=dataframe_vakken["Verwacht"][i],
            )
            for i in range(dataframe_vakken.__len__())
        )

    def _lees_zaaldata(self) -> None:
        """
        Leest de zaaldata in uit het csv-bestand.
        """
        dataframe_zalen: DataFrame = read_csv(self.__PAD_ZAALDATA_CSV, infer_schema=11, encoding="utf8")

        self.ZALEN = tuple(
            Zaal(naam=dataframe_zalen["Zaalnummber"][i], capaciteit=dataframe_zalen["Max. capaciteit"][i])
            for i in range(dataframe_zalen.__len__())
        )

    def _lees_student_vakdata(self) -> tuple[Student, ...]:
        """
        Leest de student vakdata in uit het csv-bestand.
        """
        dataframe_student_vakdata: DataFrame = read_csv(self.__PAD_STUDENT_VAKKENDATA_CSV, infer_schema=11, encoding="utf8")

        return tuple(
            Student(
                studentnummer=dataframe_student_vakdata["Stud.Nr."][i],
                voornaam=dataframe_student_vakdata["Voornaam"][i],
                achternaam=dataframe_student_vakdata["Achternaam"][i],
                vaknamen={
                    dataframe_student_vakdata[f"Vak{j}"][i]
                    for j in range(1, 6) if dataframe_student_vakdata[f"Vak{j}"][i]
                }
            )
            for i in range(dataframe_student_vakdata.__len__())
        )

    def _update_studentaantallen_vak(self) -> None:
        """
        Updatet het aantal student dat daadwerkelijk ieder vak volgt.
        """
        for student in self.STUDENTEN:
            for vak_student in student.vaknamen:
                for vak in self.VAKKEN:
                    if not (vak_student == vak.naam):
                        continue

                    vak.voeg_student_toe(student.studentnummer)

    def _lees_roosterdata(self) -> None:
        """
        Leest alle benodigde data voor een rooster in.
        """
        if not self._alle_csv_bestanden_bestaan():
            return

        proces1: Thread = Thread(target=self._lees_vakdata)
        proces2: Thread = Thread(target=self._lees_zaaldata)

        proces1.start()
        proces2.start()

        proces1.join()
        proces2.join()

        self.STUDENTEN = self._lees_student_vakdata()

        self._update_studentaantallen_vak()
