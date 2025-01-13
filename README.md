# **Algoritmen en Heuristieken**

Deze repository bevat een project voor het genereren en optimaliseren van een rooster voor onderwijsactiviteiten. Het project maakt gebruik van verschillende algoritmen en heuristieken om tot een optimale oplossing te komen. 

## Inhoud van de Repository

- **`requirements.txt`**: lijst van Python-pakketten die nodig zijn om het project uit te voeren;
- **`main.py`**: het hoofdscript waarmee het rooster gegenereerd wordt;
- **`data/`**: map voor de opslag van de benodigde roosterinformatiedata voor de algoritmen, algoritmeprestaties en roosters; 
- **`rooster/`**: de module waarop `main.py` leunt.

## Installatie

1. **ideaal**: `python3.12`;
2. **installatie vereisten**: `pip install -r requirements.txt`.

# Gebruik
1. run `main.py`

Voorbeeld: `python3.12 main.py --vakken ./data/vakken.csv --zalen ./data/zalen.csv --sv ./data/studenten_en_vakken.csv --resultaat ./data/roosterHillclimber.csv --prestatie ./data/prestatiesAlgoritmen.csv --lussen 500 --algoritme genetisch`

### Toelichting vlaggen
1. `--vakken` <pad csv-bestand vakken>;
2. `--zalen` <pad csv-bestand zalen>;
3. `--sv` <pad csv-bestand student-vakdata>;
4. `--prestatie` <pad csv-bestand student-vakdata>;
5. `--algoritme` <type algoritme>;
6. `--lussen` <het aantal lussen voor het algortime>.

Kiest uit de volgende algoritmen: 
 - `"hillclimber"`: geneert een n-aantal rooster door willekeurige zaalsloten te wisselen, en geeft het beste rooster uit dat n-aantal terug — hillclimbing ('bergklimmen');
- `"deterministisch"`: genereert een rooster door gebruik te maken van simulated annealing. Deze methode staat slechte oplossingen toe met een kans die naarmate tijd vordert afneemt. Uiteindelijk wordt hierdoor een optimale staat bereikt;
- `"simulatedAnnealing"`: genereert een rooster door gebruik te maken van simulated annealing. Deze methode staat slechte oplossingen toe met een kans die naarmate tijd vordert afneemt. Uiteindelijk wordt hierdoor een optimale staat bereikt;
- `"genetisch"`: genereert een rooster vanuit een genetische benadering:
        1. creëert eem aanvankelijke populatie valide roosters;
        2. evalueert deze vervolgens aan de hand van strafpunten;
        3. kiest de roosters met de beste 'genen';
        4. creëert een mixmutatie van deze roosters;
        5. herhaalt dit tot het n-aantal lussen.

# Optioneel
Mocht u het nodig vinden de C-programma's te hercompileren, dan kan dat in deze volgorde (`main.py` houdt automatisch rekening met het besturingssysteem).
1. `gcc -O3 -fPIC -c reken.c -o reken.o -Wall -Werror`
2. `gcc -O3 -shared -o reken.dll -fPIC reken.c -Wall -Werror`
3. `gcc -O3 -shared -o reken.so reken.o -lm -Wall -Werror`
