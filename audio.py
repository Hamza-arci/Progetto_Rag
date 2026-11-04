import speech_recognition as sr
from gtts import gTTS
import ctypes
import os
import time

def ascolta():
    """
    Ascolta l'audio dal microfono e lo converte in testo usando le API di Google.
    """
    # Inizializziamo il riconoscitore vocale
    recognizer = sr.Recognizer()

    # Usiamo il microfono di default del sistema come sorgente audio
    with sr.Microphone() as source:
        print("Calibrazione del rumore di fondo (2 secondi)...")
        # Aumentiamo a 2 secondi per una lettura più precisa dell'ambiente
        recognizer.adjust_for_ambient_noise(source, duration=2)

        # Parametri di ottimizzazione
        recognizer.dynamic_energy_threshold = True
        recognizer.energy_threshold = 400  # Alza il valore se registra anche i respiri/rumori, abbassalo se non ti sente
        recognizer.pause_threshold = 2.0   # Aspetta 1.2 secondi di silenzio prima di considerare finita la frase

        print("Dimmi qualcosa, ti ascolto...")
        audio = recognizer.listen(source)

        try:
            print("Elaborazione in corso...")
            # Usiamo il servizio gratuito di Google per la trascrizione, impostando l'italiano
            testo_trascritto = recognizer.recognize_google(audio, language="it-IT")
            print(f"Hai detto: {testo_trascritto}")
            return testo_trascritto

        except sr.UnknownValueError:
            # Eccezione sollevata se l'audio non contiene parole riconoscibili
            print("Scusa, non ho capito cosa hai detto.")
            return None
        except sr.RequestError as e:
            # Eccezione sollevata se c'è un problema di rete o con i server di Google
            print(f"Errore di connessione con il servizio di riconoscimento: {e}")
            return None

def riproduci_mp3_nativo(percorso_file):
    """
    Usa la Media Control Interface (MCI) nativa di Windows per riprodurre MP3.
    Bypassa librerie problematiche come pygame o playsound.
    """
    alias = "voce_assistente"

    # 1. Forza la chiusura di eventuali flussi audio precedenti rimasti aperti
    ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)

    # 2. Apre il file audio
    risultato_apertura = ctypes.windll.winmm.mciSendStringW(f'open "{percorso_file}" type mpegvideo alias {alias}', None, 0, None)

    if risultato_apertura == 0:
        # 3. Riproduce e blocca l'esecuzione finché non finisce (wait)
        ctypes.windll.winmm.mciSendStringW(f'play {alias} wait', None, 0, None)
        # 4. Chiude il file per sbloccarlo (fondamentale per permettere a Python di cancellarlo)
        ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
    else:
        print("Errore a livello di sistema operativo nell'apertura del file audio.")

def parla(testo):
    """
    Genera l'audio neurale con Google Cloud TTS e lo riproduce nativamente su Windows.
    """
    if not testo:
        return

    print(f"Assistente: {testo}")

    # Crea un nome univoco basato sul timestamp
    nome_file = f"voce_temp_{int(time.time())}.mp3"

    try:
        # Genera il file e salvalo su disco
        tts = gTTS(text=testo, lang='it', slow=False)
        tts.save(nome_file)

        # Riproduce agganciandosi ai driver nativi di Windows
        riproduci_mp3_nativo(nome_file)

    except Exception as e:
        print(f"Errore nella generazione della voce: {e}")
    finally:
        # Blocco di sicurezza: garantisce l'eliminazione del file temporaneo in ogni caso
        if os.path.exists(nome_file):
            try:
                os.remove(nome_file)
            except Exception as delete_error:
                print(f"Impossibile eliminare il file temporaneo: {delete_error}")