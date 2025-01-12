# Algoritmen en Heuristieken

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
- run: `python3.12 main.py`

1. --vakken <pad csv-bestand vakken>
2. --zalen <pad csv-bestand zalen>
3. --sv <pad csv-bestand student-vakdata>
4. --prestatie <pad csv-bestand student-vakdata>
4. --algoritme <type algoritme>
4. --lussen <het aantal lussen voor het algortime>

Voorbeeld: python3.12 main.py --vakken mnt/c/test/vakken.csv --zalen ./zalen.csv --sv ../studentVak.csv--resultaat ../roosterAlgoritme1.csv--prestatie ../prestatiesAlgoritmen.csv --lussen 1500 --algoritme hillclimbing

