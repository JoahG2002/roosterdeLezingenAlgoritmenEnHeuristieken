#include <math.h>
#include <stdint.h>


double bereken_temperatuur(const double lus, const double totaalaantal_lussen, const double aanvankelijke_temperatuur);
uint8_t accepteer_slechtste_oplossing(const double vorig_aantal_strafpunten,
                                   const double nieuw_aantal_strafpunten,
                                   const double temperature,
                                   const double willekeurige_waarde_tussen_0_1);


/**
 * @brief Berekent de huidige temperatuur van het (exponentiële) algoritme op basis van voorafgaande lussen.
 * @return double.
 */
double bereken_temperatuur(const double lus, const double totaalaantal_lussen, const double aanvankelijke_temperatuur)
{
    return aanvankelijke_temperatuur * pow(0.95, (lus * 20.0 / totaalaantal_lussen));
}


/**
 * @brief Geeft terug of de slechtste oplossing moet worden aangenomen op basis van de huidige temperatuur.
 * @return uint8_t (always 0 or 1).
 */
uint8_t accepteer_slechtste_oplossing(const double vorig_aantal_strafpunten,
                                   const double nieuw_aantal_strafpunten,
                                   const double temperature,
                                   const double willekeurige_waarde_tussen_0_1)
{
    if (vorig_aantal_strafpunten > nieuw_aantal_strafpunten)
        return 1;

    double kans = exp((vorig_aantal_strafpunten - nieuw_aantal_strafpunten) / temperature);

    return (willekeurige_waarde_tussen_0_1 < kans) ? 1 : 0;
}
