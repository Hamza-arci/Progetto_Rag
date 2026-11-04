import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

load_dotenv() # Carica le variabili dal file .env

client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL"),
    api_key=os.getenv("LLM_API_KEY")
)

def deduci_intento_ricerca(domanda_utente, storico_chat):
    """
    Legge lo storico e deduce il soggetto reale della domanda attuale.
    """
    if not storico_chat:
        return domanda_utente

    try:
        istruzioni_sistema = (
            "Sei un modulo logico. Il tuo unico compito è leggere lo storico e l'ultima domanda, "
            "e riscrivere l'ultima domanda inserendo il soggetto esplicito. "
            "NON rispondere. Restituisci SOLO la domanda riscritta."
        )

        prompt_utente = f"STORICO:\n{storico_chat}\n\nDOMANDA ORIGINALE: {domanda_utente}\n\nRISCRITTURA:"

        response = client.chat.completions.create(
            model="phi3",
            messages=[
                {"role": "system", "content": istruzioni_sistema},
                {"role": "user", "content": prompt_utente}
            ],
            temperature=0.0,
            max_tokens=30
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error("Errore durante la deduzione dell'intento (Dettagli nascosti per sicurezza)")
        return domanda_utente

def genera_risposta_rag(domanda_utente, contesto_trovato, storico_chat=""):
    """
    Genera la risposta finale vincolando il modello a non allucinare.
    """
    if not domanda_utente:
        return None

    try:
        istruzioni_sistema = (
            "Sei un assistente universitario preciso e conciso. "
            "Rispondi SOLO usando le informazioni contenute all'interno del tag <CONTESTO>. "
            "Formula frasi complete. Non usare elenchi puntati. "
            "Se l'informazione non è nel contesto, scrivi ESATTAMENTE: 'Non lo so in base ai miei documenti'. "
            "Non aggiungere MAI commenti, note o esempi extra."
        )

        prompt_utente = (
            f"<STORICO>\n{storico_chat}\n</STORICO>\n\n"
            f"<CONTESTO>\n{contesto_trovato}\n</CONTESTO>\n\n"
            f"<DOMANDA>\n{domanda_utente}\n</DOMANDA>"
        )

        response = client.chat.completions.create(
            model="phi3",
            messages=[
                {"role": "system", "content": istruzioni_sistema},
                {"role": "user", "content": prompt_utente}
            ],
            temperature=0.1,
            max_tokens=100
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Errore LLM locale: {e}")
        return "Errore di generazione."