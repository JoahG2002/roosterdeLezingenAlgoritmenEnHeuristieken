import sys

from rooster.modellen.genereer import Roostermaker
from rooster.dataverwerking.lees import Roosterdata
from rooster.dataverwerking.schrijf import schrijf_foutmelding
from rooster.constants.constant import returncodes, teksten


def main(argc: int, argv: list[str]) -> None:
    if not (argc == 9):
        schrijf_foutmelding(teksten.TOELICHTING_TEKORT_VLAGGEN)
        exit(returncodes.MISLUKT)

    roosterdata: Roosterdata = Roosterdata(argv)

    if not roosterdata.inlezen_geslaagd():
        schrijf_foutmelding("minstens één van de opgegeven csv-bestandpaden bestaat niet.\n")
        exit(returncodes.MISLUKT)

    roostermaker: Roostermaker = Roostermaker(roosterdata)

    roostermaker.genereer_rooster()
    roostermaker.print_alle_studentroosters()
    roostermaker.naar_csv()

    exit(returncodes.SUCCES)


if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
