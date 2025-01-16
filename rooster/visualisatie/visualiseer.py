import matplotlib.pyplot as plt

from seaborn import heatmap
from pandas import DataFrame, Series

from ..constanten.constant import plotgegevens


def is_numerieke_kolom(kolom_dataframe: Series) -> bool:
    """
    Geeft terug of een kolom van een dataframe numeriek is.
    """
    return all(isinstance(waarde, (float, int)) for waarde in kolom_dataframe)


def normaliseer_dataframe(dataframe: DataFrame) -> DataFrame:
    """
    Geeft een dataframe als genormaliseerde kopie terug.
    """
    dataframe_genormaliseerd: DataFrame = dataframe.copy()

    for kolomnaam in plotgegevens.KOLOMNAMEN_VOOR_PLOT:
        if not is_numerieke_kolom(dataframe[kolomnaam]):
            continue

        maximumwaarde_kolom: float | int = dataframe[kolomnaam].max()

        if maximumwaarde_kolom <= 0:
            continue

        dataframe_genormaliseerd[kolomnaam] = (dataframe[kolomnaam] / maximumwaarde_kolom)

    return dataframe_genormaliseerd


def plot_prestaties_algoritmen(prestatiedata_algoritme: DataFrame) -> None:
    """
    Plot de prestatiedata van een algoritme voor iedere run van een gegeven algoritme in één afbeelding, waarin iedere regel de relatieve, genormaliseerde score tot de kolomwaarden van de andere algoritmeruns visualiseert.
    """
    prestatiedata_doelkolommen: DataFrame = prestatiedata_algoritme[plotgegevens.KOLOMNAMEN_VOOR_PLOT].copy()

    plt.figure(figsize=(15, len(prestatiedata_algoritme) * 0.4))

    prestaties_genormaliseerd: DataFrame = normaliseer_dataframe(prestatiedata_algoritme)

    heatmap(
        data=prestaties_genormaliseerd.set_index("naamAlgoritme")[plotgegevens.KOLOMNAMEN_VOOR_PLOT[1:]],
        cmap="RdYlGn_r",
        annot=prestatiedata_doelkolommen.set_index("naamAlgoritme")[plotgegevens.KOLOMNAMEN_VOOR_PLOT[1:]],
        fmt='g',
        cbar_kws={"label": "Prestatie genormaliseerd (hoger = slechter)"},
        yticklabels=True
    )

    plt.title("Vergelijking prestaties algoritmen", fontsize=21)
    plt.xlabel("metriek")
    plt.ylabel("algoritme")
    plt.xticks(ha="right", rotation=50)
    plt.tight_layout()

    plt.show()
