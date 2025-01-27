
import numpy as np
from seaborn import heatmap
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from pandas import DataFrame, Series

from ..constanten.constant import plotgegevens, algoritmen


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


def plot_duur_prestatieratios_algoritmen(prestatiedata_algoritme: DataFrame) -> None:
    """
    Plot de duur-prestatieratios van de diverse roosteralgoritmen.
    """
    for afkorting_algoritme in algoritmen.VOOR_PLOT:
        eerste_vier_karakters_algoritmetype: str = afkorting_algoritme[:4]

        totale_scores_met_duur_seconden: dict[int, float] = {
            prestatiedata_algoritme["totaal"][i]: prestatiedata_algoritme["duurGenerenSeconden"][i]
            for i in range(prestatiedata_algoritme.__len__())
            if prestatiedata_algoritme["naamAlgoritme"][i].startswith(eerste_vier_karakters_algoritmetype)
        }

        totale_scores_met_duur_seconden = dict(
            sorted(totale_scores_met_duur_seconden.items(), key=lambda x: x[1], reverse=True)
        )

        duren_algoritmen: np.array = np.array(list(totale_scores_met_duur_seconden.values()))
        prestaties_algoritmen: np.array = np.array(list(totale_scores_met_duur_seconden.keys()))
        coefficients: np.array = np.polyfit(duren_algoritmen, prestaties_algoritmen, 1)
        trendline: np.poly1d = np.poly1d(coefficients)

        fig: go.Figure = go.Figure(
            data=go.Bar(
                x=list(totale_scores_met_duur_seconden.values()),
                y=list(totale_scores_met_duur_seconden.keys())
            )

        )
        fig.update_layout(
            title=(
                f"Generatieduur-strafpuntverhouding {afkorting_algoritme}"
                f"{'-' if not afkorting_algoritme.endswith("sch") else ' '}algoritme"
            ),
            xaxis_title="duur generen rooster seconden",
            yaxis_title="aantal strafpunten")

        fig.add_trace(
            go.Scatter(
                x=duren_algoritmen,
                y=trendline(duren_algoritmen),
                mode="lines",
                name="Trendline",
                line=dict(color="red", dash="dash")
            )
        )
        fig.show()


def maak_frequentieklassen(prestatiedata_algoritme: DataFrame, doelalgoritme: str) -> dict[str, int]:
    """
    Ontvangt een dataframe algoritmeprestaties, en geeft het aantal strafpunten van een doelalgoritmen terug — opgedeeld in frequentieklassen.
    """
    frequentieklassen_strafpunten: dict[str, int] = {
        "< 100": 0, "100–300": 0, "300–500": 0, "500–750": 0, "750–1.000": 0, "1.000–1.500": 0, "1.500–2.000": 0,
        "2.000–3.000": 0, "3.000–4.000": 0, "4.000–8.000": 0, "8.000–15.000": 0, "15.000–30.000": 0,  "30.000–50.000": 0,
        "> 50.000": 0,
    }

    for i in range(prestatiedata_algoritme.__len__()):
        if not (prestatiedata_algoritme["naamAlgoritme"][i] == doelalgoritme):
            continue

        aantal_strafpunten_run: int = prestatiedata_algoritme["totaal"][i]

        if aantal_strafpunten_run < 100:
            frequentieklassen_strafpunten["< 100"] += 1
        elif aantal_strafpunten_run < 300:
            frequentieklassen_strafpunten["100–300"] += 1
        elif aantal_strafpunten_run < 500:
            frequentieklassen_strafpunten["300–500"] += 1
        elif aantal_strafpunten_run < 750:
            frequentieklassen_strafpunten["500–750"] += 1
        elif aantal_strafpunten_run < 1_000:
            frequentieklassen_strafpunten["750–1.000"] += 1
        elif aantal_strafpunten_run < 1_500:
            frequentieklassen_strafpunten["1.000–1.500"] += 1
        elif aantal_strafpunten_run < 2_000:
            frequentieklassen_strafpunten["1.500–2.000"] += 1
        elif aantal_strafpunten_run < 3_000:
            frequentieklassen_strafpunten["2.000–3.000"] += 1
        elif aantal_strafpunten_run < 4_000:
            frequentieklassen_strafpunten["3.000–4.000"] += 1
        elif aantal_strafpunten_run < 8_000:
            frequentieklassen_strafpunten["4.000–8.000"] += 1
        elif aantal_strafpunten_run < 15_000:
            frequentieklassen_strafpunten["8.000–15.000"] += 1
        elif aantal_strafpunten_run < 30_000:
            frequentieklassen_strafpunten["15.000–30.000"] += 1
        elif aantal_strafpunten_run < 50_000:
            frequentieklassen_strafpunten["30.000–50.000"] += 1
        else:
            frequentieklassen_strafpunten["> 50.000"] += 1

    return frequentieklassen_strafpunten


def plot_verdeling_data(sleutels_met_waarden: dict[str, int | float],
                        titel_grafiek: str,
                        titel_x_as: str,
                        titel_y_as: str,
                        kleur_balken_grafiek: str,
                        gesorteerd: bool = False) -> None:
    """
    Plot de frequentie van een tijdeenheid van de geboortedata.
    """
    if gesorteerd:
        sleutels_met_waarden = dict(sorted(sleutels_met_waarden.items(), key=lambda x: x[1]))

    fig: go.Figure = go.Figure(
        data=go.Bar(
            x=list(sleutels_met_waarden.keys()),
            y=list(sleutels_met_waarden.values()),
            marker_color=kleur_balken_grafiek
        )
    )

    fig.update_layout(title=titel_grafiek, xaxis_title=titel_x_as, yaxis_title=titel_y_as)
    fig.update_xaxes(type="category")
    fig.show()
