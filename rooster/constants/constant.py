import os

from colorama import Fore, Style
from typing import Final, Literal


class Maxima:
    __slots__: tuple[str, ...] = (
        "AANTAL_TIJDSLOTEN_WEEK", "AANTAL_WEKEN_JAAR", "AANTAL_WERKCOLLEGES_TEGELIJKERTIJD_PER_VAK", "GROOTSTE_ZAAL",
        "ONGELDIG_ALGORITME"
    )

    def __init__(self) -> None:
        self.AANTAL_TIJDSLOTEN_WEEK: Final[int] = 20  # 5 dagen per week, vier tijdsloten per dag
        self.AANTAL_WEKEN_JAAR: Final[int] = 52  # 5 dagen per week, vier tijdsloten per dag
        self.GROOTSTE_ZAAL: Final[str] = "C0.110"


class Tekst:
    __slots__: tuple[str, ...] = (
        "ONGELDIG_TIJDSLOT", "TOELICHTING_TEKORT_VLAGGEN", "KOLOMMEN_RESULTATEN_CSV", "KOLOMMEN_PRESTATIES_ALGORITMEN_CSV",
        "CSV_BESTAAT_NIET", "ONGELDIG_ALGORITME"
    )

    def __init__(self) -> None:
        self.ONGELDIG_TIJDSLOT: Final[str] = (
            "Invalide tijdslot. Wel toegestaan: 9.00–11.00, 11.00–13.00, 13.00–15.00, 15.00–17.00 or 17.00–19.00*."
        )
        self.TOELICHTING_TEKORT_VLAGGEN: Final[str] = (
            f"Onvoldoende vlaggen; geef de volgende vlaggen mee aan main.py:\n{'-' * 115}\n\n"
            f"1. {Fore.YELLOW}--vakken{Style.RESET_ALL} <pad csv-bestand vakken>\n"
            f"2. {Fore.YELLOW}--zalen{Style.RESET_ALL} <pad csv-bestand zalen>\n"
            f"3. {Fore.YELLOW}--sv{Style.RESET_ALL} <pad csv-bestand student-vakdata>\n"
            f"4. {Fore.YELLOW}--prestatie{Style.RESET_ALL} <pad csv-bestand student-vakdata>\n"
            f"4. {Fore.YELLOW}--algoritme{Style.RESET_ALL} <type algoritme>\n"
            f"4. {Fore.YELLOW}--lussen{Style.RESET_ALL} <het aantal lussen voor het algortime>\n"
            
            f"\nVoorbeeld: {Fore.CYAN}python3.12 main.py {Fore.YELLOW}--vakken{Fore.CYAN} mnt/c/test/vakken.csv"
            f" {Fore.YELLOW}--zalen{Fore.CYAN} ./zalen.csv {Fore.YELLOW}"
            f"--sv{Fore.CYAN} ../studentVak.csv"
            f"{Fore.YELLOW}--resultaat{Fore.CYAN} ../roosterAlgoritme1.csv"
            f"{Fore.YELLOW}--prestatie{Fore.CYAN} ../prestatiesAlgoritmen.csv"
            f" {Fore.YELLOW}--lussen{Fore.CYAN} 1500"
            f" {Fore.YELLOW}--algoritme{Fore.CYAN} hillclimbing {Style.RESET_ALL}\n\n"
        )
        self.CSV_BESTAAT_NIET: Final[str] = "minstens één van de opgegeven csv-bestandpaden bestaat niet.\n"
        self.ONGELDIG_ALGORITME: Final[str] = f"ongeldig algoritme; programma gestopt. Kies uit: {Algoritme().VALIDEN}\n\n"

        self.KOLOMMEN_RESULTATEN_CSV: Final[str] = "naamStudent,vak,type,zaal,dag,tijdslot\n"
        self.KOLOMMEN_PRESTATIES_ALGORITMEN_CSV: Final[str] = (
            "naamAlgoritme,dubbelIngeroosterd,tussentijdsloten,vakNietIngeroosterd,avond,"
            "overvol,aantalLussen,totaal,duurGenerenSeconden\n"
        )


class Returncode:
    __slots__: tuple[str, ...] = ("SUCCES", "MISLUKT")

    def __init__(self) -> None:
        self.SUCCES: Final[Literal[0, -1]] = 0
        self.MISLUKT: Final[Literal[0, -1]] = -1


class Tijdeenheid:
    __slots__: tuple[str, ...] = ("WEEKDAGEN", "TIJDSLOTEN")

    def __init__(self) -> None:
        self.WEEKDAGEN: Final[tuple[str, ...]] = ("maandag", "dinsdag", "woensdag", "donderdag", "vrijdag")
        self.TIJDSLOTEN: Final[tuple[str, ...]] = ("9.00–11.00", "11.00–13.00", "13.00–15.00", "15.00–17.00")


class Algoritme:
    __slots__: tuple[str, ...] = ("VALIDEN",)

    def __init__(self) -> None:
        self.VALIDEN: Final[tuple[str, ...]] = ("hillclimber", "deterministisch", "simulatedAnnealing", "genetisch")


class ShareLibraryFunctie:
    __slots__: tuple[str, ...] = ("PAD_DLL_SO_BESTAND_C_FUNCTIES",)

    def __init__(self) -> None:
        naam_dll_so: str = "reken.so" if (os.name == "posix") else "reken.dll"
        self.PAD_DLL_SO_BESTAND_C_FUNCTIES: Final[str] = f"{os.getcwd()}/rooster/c_functies/{naam_dll_so}"


maxima: Maxima = Maxima()
teksten: Tekst = Tekst()
returncodes: Returncode = Returncode()
tijdeenheden: Tijdeenheid = Tijdeenheid()
algoritmen: Algoritme = Algoritme()
sharedlibraryfuncties: ShareLibraryFunctie = ShareLibraryFunctie()
