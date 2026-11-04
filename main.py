import time
import difflib
from audio import ascolta, parla
from rag import carica_documenti, cerca_nel_database
from llm import genera_risposta_rag, deduci_intento_ricerca

# Cache per le domande identiche
cache_risposte = {}
# Buffer per ricordare gli ultimi scambi (Memoria conversazionale)
storico_conversazione = []

if __name__ == "__main__":
    print("Avvio sistema e controllo documenti...")
    carica_documenti()
    parla("Ciao, sono pronto a rispondere alle tue domande.")

    while True:
        print("\n--- In attesa di input ---")
        domanda = ascolta()

        if domanda:
            domanda_pulita = domanda.lower().strip()

            if "esci" in domanda_pulita or "stop" in domanda_pulita:
                parla("D'accordo, mi spengo. Alla prossima!")
                break

            print("\nInizio elaborazione...")
            inizio_totale = time.time()
            risposta_finale = None

            # 1. CONTROLLO CACHE (Similarity Matching)
            for domanda_salvata, risposta_salvata in cache_risposte.items():
                # Calcola quanto si somigliano le due stringhe (da 0.0 a 1.0)
                somiglianza = difflib.SequenceMatcher(None, domanda_salvata, domanda_pulita).ratio()

                # Se sono identiche per almeno l'85%, è un Cache Hit valido
                if somiglianza > 0.85:
                    print(f"[Telemetria] CACHE HIT! (Affinità: {somiglianza*100:.1f}%)")
                    risposta_finale = risposta_salvata
                    break

            if not risposta_finale:
                testo_storico = "\n".join(storico_conversazione)

                # --- IL CERVELLO RIFLETTE ---
                inizio_ragionamento = time.time()
                # Deduce il vero significato della tua domanda basandosi sulla memoria
                domanda_esplicita = deduci_intento_ricerca(domanda, testo_storico)
                print(f"[Cervello] Ho interpretato il tuo intento come: '{domanda_esplicita}'")

                # --- IL BIBLIOTECARIO CERCA ---
                inizio_rag = time.time()
                # Usa la domanda esplicita per cercare nei documenti (non quella originale)
                contesto = cerca_nel_database(domanda_esplicita)
                print(f"[Telemetria] Ricerca ChromaDB: {time.time() - inizio_rag:.2f} secondi.")

                # --- L'IA RISPONDE ---
                inizio_llm = time.time()
                # Genera la risposta usando la tua domanda originale, così sembra naturale
                risposta_finale = genera_risposta_rag(domanda, contesto, testo_storico)
                print(f"[Telemetria] Generazione LLM: {time.time() - inizio_llm:.2f} secondi.")

                cache_risposte[domanda_pulita] = risposta_finale

                storico_conversazione.append(f"Utente: {domanda}")
                storico_conversazione.append(f"Assistente: {risposta_finale}")

                if len(storico_conversazione) > 4:
                    storico_conversazione = storico_conversazione[-4:]

            print(f"[Telemetria] Latenza totale: {time.time() - inizio_totale:.2f} secondi.\n")
            parla(risposta_finale)