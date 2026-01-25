# 🚀 CLI Chatbot Using the OpenAI Responses API

## 📖 Overview

A command-line chatbot powered by the OpenAI Responses API.

It supports persistent conversation history, multi-modal file analysis, and instant session saving. The app uses event streaming and `previous_response_id` to maintain context efficiently across multiple turns.

---

## ✨ Features

* 🗨️ **Context-Aware Chat**: Maintains dialogue state using the Responses API's `previous_response_id`.
* ⌨️ **Advanced Input**:
* Multi-line prompt support (**Enter** for new line, **Alt+Enter** to send).
* Emacs-style keyboard shortcuts (e.g., `Ctrl+A`, `Ctrl+E`, `Ctrl+K`).
* 💾 **History Management**: Automatically saves conversation logs to the `./history` directory in Markdown format.
* 📂 **Flexible File Analysis**: Load files by starting a line with `~ ` (tilde + space):
* **Text-based**: `.txt`, `.py`, `.md`, `.csv`, etc..
* **Excel**: `.xlsx` files are automatically converted to JSON for the model.
* **Images**: `.jpg`, `.jpeg`, `.png` via local path or URL (uses Files API for local).
* **PDF**: Local files or URLs (uses Files API for local).
* ⚡ **Instant Save**: Use the `!save` command to export the current transcript immediately without exiting.

---

## ⚙️ Requirements

* Python **3.10+**
* Install dependencies:
```bash
pip install -r requirements.txt
```



---

## 🔑 Setup

1. **Set OpenAI API Key**
```bash
# Windows
setx OPENAI_API_KEY "your_api_key_here"
# Linux / macOS
export OPENAI_API_KEY="your_api_key_here"
```


2. **Configure Settings**
Edit `settings.py` to define your defaults:
```python
PROMPT = "You are a helpful assistant."
MODEL = "gpt-5.1-chat-latest"
TEMPERATURE = 1.0
STREAM = False
REASONING_EFFORT = "none"  # low | medium | high | minimal | none
```


3. **Run**
```bash
python clichatbot.py
```

---

## 💬 Usage

### Basic Interaction

* Type your message.
* **`Alt+Enter`** (or `Esc` then `Enter`) → Send.
* **`Alt+Enter`** on an empty prompt → Save and Exit.

### Analyzing Files

You can attach multiple files by adding paths or URLs on new lines starting with `~ `:

```plaintext
user: Please analyze these files
~ ./src/main.py
~ https://example.com/data.pdf
```

---

## ⚙️ Model Specifics

The application applies different parameters based on the `MODEL` string defined in `settings.py`:

| Model Group | Max Tokens | Reasoning Effort | Temperature |
| --- | --- | --- | --- |
| **`gpt-5.x`** | 128,000 | Supported | Not Applied |
| **`gpt-5.x-chat-latest`** | 16,384 | Not Applied | Not Applied |
| **`gpt-4.1`** | 32,768 | Not Applied | Supported |

---

## 📝 Notes

* **Constraints**: Surrogate pair characters are not supported due to a limitation in `prompt_toolkit`.

---

## 📜 License

MIT
