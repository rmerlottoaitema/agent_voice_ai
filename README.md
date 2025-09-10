# Setup Python e LiveKit Client

Guida l’installazione di Python, la creazione di un virtual environment e l’installazione dei pacchetti necessari per il client Python di LiveKit.

---

## 1 - Installare Python 3

#### Su Linux:
```bash
sudo apt update
sudo apt install python3
```
#### Su macOS (usando Homebrew):
```bash
brew update
brew install python
```
## 2 - Installare pip

#### Su Linux:

```bash
sudo apt install python3-pip
python3 -m pip install --upgrade pip
```

#### Su macOS, pip è incluso con Python:

```bash
python3 -m pip install --upgrade pip
```

## 3 - Creare un Virtual Environment

#### Su Linux:
```bash
sudo apt install python3.12-venv
python3 -m venv venv
```

#### Su macOS:
```bash
python3 -m venv venv
```

#### Attivazione Linux/macOS (bash/zsh):
```bash
source venv/bin/activate
```

## 4 - Installare i pacchetti Python necessari

```bash
pip install livekit-api
pip install livekit.agents
pip install "livekit-agents[deepgram,openai,cartesia,silero,turn-detector]~=1.2"
pip install "livekit-plugins-noise-cancellation~=0.2"
pip install dotenv
```

## 5 - Variabili d'ambiente

#### su file `.env.local`:
```
CARTESIA_API_KEY=""
DEEPGRAM_API_KEY=""
LIVEKIT_API_KEY=""
LIVEKIT_API_SECRET=""
LIVEKIT_URL=""
OPENAI_API_KEY=""
```

| Variabile             | Obbligatoria | Uso                                 |
|-----------------------|--------------|-------------------------------------|
| `LIVEKIT_API_KEY`     | Sì           | Connessione al server LiveKit       |
| `LIVEKIT_API_SECRET`  | Sì           | Connessione al server LiveKit       |
| `LIVEKIT_URL`         | Sì           | URL del server LiveKit              |
| `CARTESIA_API_KEY`    | Opzionale    | Plugin Cartesia                     |
| `DEEPGRAM_API_KEY`    | Opzionale    | Plugin Deepgram per trascrizione    |
| `OPENAI_API_KEY`      | Opzionale    | Plugin OpenAI per AI / NLP          |


## 6 - Comandi LiveKit Agents


| Comando          | Descrizione                                                           |
|------------------|-----------------------------------------------------------------------|
| `connect`        | Connette il client a una stanza specifica di LiveKit.                 |
| `console`        | Avvia una nuova conversazione direttamente nella console interattiva. |
| `dev`            | Avvia il worker in modalità sviluppo (utile per testing e debugging). |
| `download-files` | Scarica i file di dipendenza necessari dai plugin configurati.        |
| `start`          | Avvia il worker in modalità produzione.                               |



## 7 - Esempi pratici di comandi LiveKit Agent


#### Connette l’agente alla stanza `sip-room`

```bash
python src/agent.py connect --room sip-room
```

#### Connette l’agente alla stanza `test-room` con identità `bot1`

```bash
python src/agent.py connect --room test-room --identity bot1
```

#### Avvia una conversazione interattiva nella console

```bash
python src/agent.py console
```

#### Avvia il worker in modalità sviluppo (utile per debugging)

```bash
python src/agent.py dev
```

#### Avvia il worker in modalità produzione
```bash
python src/agent.py start
```

#### Scarica le dipendenze richieste dai plugin configurati (Deepgram, Cartesia, ecc)
```bash
python src/agent.py download-files`
```

## 8 - Setup ed avvio del server LiveKit Agent

#### Installare i pacchetti Python necessari:
```bash
pip install flask
pip install flask_cors
```

#### Esegui il server con:
```bash
python src/server.py
```

#### Server is running on:
[http://0.0.0.0:3000](http://0.0.0.0:3000)