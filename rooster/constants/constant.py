from colorama import Fore, Style
from typing import Final, Literal


class Maxima:
    __slots__: tuple[str, ...] = (
        "AANTAL_TIJDSLOTEN_WEEK", "AANTAL_WEKEN_JAAR", "AANTAL_WERKCOLLEGES_TEGELIJKERTIJD_PER_VAK"
    )

    def __init__(self) -> None:
        self.AANTAL_TIJDSLOTEN_WEEK: Final[int] = 20  # 5 dagen per week, vier tijdsloten per dag
        self.AANTAL_WEKEN_JAAR: Final[int] = 52  # 5 dagen per week, vier tijdsloten per dag
        self.AANTAL_WERKCOLLEGES_TEGELIJKERTIJD_PER_VAK: Final[int] = 5


class Tekst:
    __slots__: tuple[str, ...] = ("ONGELDIG_TIJDSLOT", "TOELICHTING_VLAGGEN")

    def __init__(self) -> None:
        self.ONGELDIG_TIJDSLOT: Final[str] = (
            "Invalide tijdslot. Wel toegestaan: 9.00–11.00, 11.00–13.00, 13.00–15.00 of 15.00–17.00."
        )
        self.TOELICHTING_VLAGGEN: Final[str] = (
            f"Onvoldoende vlaggen; geef de volgende vlaggen mee aan main.py:\n{'-' * 115}\n\n"
            f"1. {Fore.YELLOW}--vakken{Style.RESET_ALL} <pad csv-bestand vakken>\n"
            f"2. {Fore.YELLOW}--zalen{Style.RESET_ALL} <pad csv-bestand zalen>\n"
            f"3. {Fore.YELLOW}--sv{Style.RESET_ALL} <pad csv-bestand student-vakdata>\n"
            f"\nVoorbeeld: {Fore.CYAN}python3.12 main.py {Fore.YELLOW}--vakken{Fore.CYAN} mnt/c/test/vakken.csv"
            f" {Fore.YELLOW}--zalen{Fore.CYAN} ./zalen.csv {Fore.YELLOW}--sv{Fore.CYAN} ../studentVak.csv {Style.RESET_ALL}\n\n"
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


maxima: Maxima = Maxima()
teksten: Tekst = Tekst()
returncodes: Returncode = Returncode()
tijdeenheden: Tijdeenheid = Tijdeenheid()
