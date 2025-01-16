import sys

from datetime import datetime
from colorama import Fore, Style


def schrijf_foutmelding(tekst_foutmelding: str) -> None:
    """
    Schrijft een gekleurde, geformatteerde foutmelding naar de stderr (foutmeldingsstroom).
    """
    sys.stderr.write(f"\n{Fore.RED}- [FOUT]{Style.RESET_ALL} {tekst_foutmelding}")


def schrijf_voortgang_algoritme(nieuw_aantal_strafpunten: int, huidige_lus: int, totaalaantal_lussen: int) -> None:
    """
    Print voortgang algoritme.
    """
    nu: datetime = datetime.now()

    sys.stdout.write(
        f"\n{Fore.BLUE}[UPDATE]{Style.RESET_ALL} Rooster verbeterd! Huidige aantal strafpunten:"
        f" {Fore.GREEN}{nieuw_aantal_strafpunten}{Fore.YELLOW} - lus ({huidige_lus} / {totaalaantal_lussen:,}){Fore.CYAN}"
        f" - {str(nu.day).zfill(2)}-{str(nu.month).zfill(2)}-{str(nu.year).zfill(2)}"
        f" {str(nu.hour).zfill(2)}.{str(nu.minute).zfill(2)} uur{Style.RESET_ALL}\n"
    )
