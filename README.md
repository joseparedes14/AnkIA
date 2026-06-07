# AnkIA

**AI-powered vocabulary flashcards — right on your desktop.**

AnkIA is a desktop overlay widget that helps you build Anki-compatible vocabulary decks using a local LLM (Ollama). Type a word, get an instant translation with an example sentence, and save it directly to your deck. No browser needed.

![widget](https://img.shields.io/badge/platform-Windows-blue)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![llm](https://img.shields.io/badge/LLM-Ollama-orange)

---

## Features

- **Desktop overlay widget** — sits at the right edge of your screen, always available
- **AI translations** — powered by Ollama (local LLM, no API keys, no cloud)
- **Smart recommendations** — the AI suggests new words based on your level and theme
- **Anki-compatible export** — download `.txt` files ready to import into Anki
- **Web UI alternative** — also includes a Streamlit web interface
- **Context-aware** — each deck can have a description (e.g., "kitchen vocabulary") to guide recommendations

---

## Quick Start

### 1. Install Ollama

Download and install [Ollama](https://ollama.com), then pull a model:

```sh
ollama pull gpt-oss:120b-cloud
```

Ollama must be running (`http://localhost:11434`) for AnkIA to work.

### 2. Install AnkIA

```sh
git clone https://github.com/anomalyco/ankia.git
cd ankia
pip install -r requirements.txt
```

### 3. Launch

**Desktop widget (recommended):**

```sh
python widget.py
```

A panel will appear anchored to the right side of your screen. Click `›` to expand it.

**Web UI (alternative):**

```sh
streamlit run app.py
```

---

## Usage

### Creating a deck

1. Click **+ NUEVO MAZO** in the widget
2. Enter a name, source/target languages, and CEFR level
3. Optionally add a description (e.g., *"vocabulario de cocina"*) to help the AI give better recommendations
4. Click **CREAR MAZO**

### Adding cards

Type a word in the source language and press Enter. The AI translates it, generates an example sentence, and saves it to the current deck.

### Getting recommendations

Open a deck, click **RECOMENDAR**, set how many words you want, and click **GENERAR**. Review the suggestions, check the ones you like, and save them.

### Exporting to Anki

Open a deck and click **DESCARGAR** to save an Anki-compatible `.txt` file.

---

## Project Structure

```
ankia/
├── widget.py                 # Desktop overlay widget (main entry point)
├── app.py                    # Streamlit web UI (alternative)
├── ankia/                    # Package
│   └── utils/
│       ├── anki_manager.py   # Deck file CRUD (Anki .txt format)
│       ├── context_manager.py# Deck metadata management
│       └── ollama_client.py  # Ollama API client (translate + recommend)
├── decks/                    # User vocabulary data
│   └── metadata.json
├── tests/
├── requirements.txt
└── pyproject.toml
```

---

## Requirements

- **Python 3.10+**
- **Ollama** running locally with a compatible model
- **PySide6** (for the desktop widget)
- **Streamlit** (optional, for the web UI)

---

## License

MIT
