import chromadb
import os

# Inizializziamo il client ChromaDB in locale.
# Creerà una cartella "chroma_db" nel tuo progetto per salvare i dati.
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# Creiamo (o recuperiamo se esiste già) una "collezione" (come una tabella di un database)
collection = chroma_client.get_or_create_collection(name="memoria_assistente")

def carica_documenti():
    """Legge i file .txt nella cartella 'data' e li salva nel database vettoriale."""
    if not os.path.exists("data"):
        os.makedirs("data")
        print("Cartella 'data' creata. Inserisci dei file .txt al suo interno.")
        return

    # Contiamo quanti frammenti inseriamo per dare loro un ID univoco
    id_counter = 0

    for filename in os.listdir("data"):
        if filename.endswith(".txt"):
            percorso_file = os.path.join("data", filename)
            with open(percorso_file, "r", encoding="utf-8") as f:
                testo = f.read()

                # Per semplicità, dividiamo il testo in righe/paragrafi (ogni riga vuota è un taglio)
                paragrafi = testo.split("\n")

                for paragrafo in paragrafi:
                    if len(paragrafo.strip()) > 5:  # Ignoriamo le righe vuote o troppo corte
                        # Inseriamo il frammento di testo nel database
                        collection.upsert(
                            documents=[paragrafo],
                            ids=[f"doc_{id_counter}"]
                        )
                        id_counter += 1

    print(f"Caricamento completato: {id_counter} frammenti salvati nel database locale.")

def cerca_nel_database(query):
    """Cerca il frammento di testo più pertinente alla domanda dell'utente."""
    risultati = collection.query(
        query_texts=[query],
        n_results=1  # Vogliamo solo il risultato più rilevante
    )

    # Se ha trovato qualcosa, restituisce il testo
    if risultati['documents'] and risultati['documents'][0]:
        return risultati['documents'][0][0]

    return "Non ho trovato informazioni rilevanti nei miei documenti."