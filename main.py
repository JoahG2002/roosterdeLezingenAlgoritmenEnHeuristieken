import sys

from rooster.modellen.roostermaker import Roostermaker
from rooster.dataverwerking.lees import Roosterdata
from rooster.dataverwerking.schrijf import schrijf_foutmelding
from rooster.constants.constant import returncodes, teksten, algoritmen


def main(argc: int, argv: list[str]) -> None:
    if not (argc == 15):
        schrijf_foutmelding(teksten.TOELICHTING_TEKORT_VLAGGEN)
        exit(returncodes.MISLUKT)

    roosterdata: Roosterdata = Roosterdata(argv)

    if not roosterdata.inlezen_geslaagd():
        schrijf_foutmelding(teksten.CSV_BESTAAT_NIET)
        exit(returncodes.MISLUKT)

    if not (roosterdata.MODUS_ALGORITME in algoritmen.VALIDEN):
        schrijf_foutmelding(teksten.ONGELDIG_ALGORITME)
        exit(returncodes.MISLUKT)

    roostermaker: Roostermaker = Roostermaker(roosterdata)

    roostermaker.genereer_rooster()

    if not roostermaker.is_valide_rooster():
        schrijf_foutmelding("rooster invalide: niet iedere activiteit van ieder vak is ingeroosterd.\n\n")

    roostermaker.print_rooster()

    # roostermaker.print_alle_studentroosters()

    roostermaker.prestatie_algoritme_naar_csv()
    roostermaker.naar_csv()

    roostermaker.print_strafpunten()

    exit(returncodes.SUCCES)


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
