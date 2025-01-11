import sys

from datetime import datetime
from colorama import Fore, Style


def schrijf_foutmelding(tekst_foutmelding: str) -> None:
    """
    Schrijft een gekleurde, geformatteerde foutmelding naar de stderr (foutmeldingsstroom).
    """
    sys.stderr.write(f"\n{Fore.RED}- [FOUT]{Style.RESET_ALL} {tekst_foutmelding}")


def print_voortgang_algoritme(nieuw_aantal_strafpunten: int, huidige_lus: int, totaalaantal_lussen: int) -> None:
    """
    Print voortgang algoritme.
    """
    nu: datetime = datetime.now()

    sys.stdout.write(
        f"\n{Fore.BLUE}[UPDATE]{Style.RESET_ALL} Rooster verbeterd! Huidige aantal strafpunten:"
        f" {Fore.GREEN}{nieuw_aantal_strafpunten}{Style.RESET_ALL} lus ({huidige_lus} / {totaalaantal_lussen:,})"
        f" - {nu.day}-{nu.month}-{nu.year} {nu.hour}.{nu.minute} uur\n"
    )
