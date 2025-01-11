import sys

from colorama import Fore, Style


def schrijf_foutmelding(tekst_foutmelding: str) -> None:
    """
    Schrijft een gekleurde, geformatteerde foutmelding naar de stderr (foutmeldingsstroom).
    """
    sys.stderr.write(f"\n{Fore.RED}- [FOUT]{Style.RESET_ALL} {tekst_foutmelding}")
