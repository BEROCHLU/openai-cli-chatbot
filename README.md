なるほど。いまの README は情報量は十分ですが、少し冗長で重複があるので、
**見出しを整理**して **繰り返しを削除**、さらに **コードや例はフォーマットを統一**するとぐっと見やすくなります。

以下のようにまとめ直すとスッキリします👇

---

# CLI Chatbot Using the OpenAI API

## Overview

A simple command-line chatbot powered by the OpenAI API.
It supports conversation history, file analysis, and instant saving.

## Features

* Conversational interface with context-aware replies
* Conversation history saved to `./history`
* File input via `|` operator:

  * Text-based files (`.txt`, `.csv`, `.py`, `.md`, etc.)
  * Excel files (`.xlsx`, automatically converted to JSON)
  * PDF files (`.pdf`)
  * Images (`.jpg`, `.jpeg`, `.png`)
* Instant save using `!save` command

## Requirements

* Python 3.10+
* Install dependencies:

  ```bash
  pip install -r requirements.txt
  ```

**Optional (Windows):**
[Windows Terminal](https://apps.microsoft.com/detail/windows-terminal/9N0DX20HK701) for better rendering and fewer artifacts.

## Setup

1. **Set API Key**

   ```bash
   setx OPENAI_API_KEY "your_api_key_here"   # Windows
   export OPENAI_API_KEY="your_api_key_here" # Linux / macOS
   ```

2. **Configure Settings**
   Copy `settings_example.py` → `settings.py` and edit:

   ```python
   MODEL = "gpt-5"  # gpt-5 | gpt-5-mini | gpt-5-chat-latest | gpt-4.1 | gpt-4.1-mini | o4-mini | o3 | gpt-4o
   TEMPERATURE = 1.0
   REASONING_EFFORT = "medium"  # low | medium | high | minimal
   ```

3. **Run**

   ```bash
   python chatbot-openai.py
   ```

   *(Windows users can use `script/wt-openai.bat` to launch in Windows Terminal.)*

## Usage

**Basic chat**

```plaintext
user: Your question
```

**File analysis** (multiple files supported, space around `|` is required)

```plaintext
user: Explain this code | /path/to/example.py | /path/to/another_file.py
```

**Exit session**
Press **Enter** on empty input → history is saved to `./history`.

**Instant save**

```plaintext
user: !save
```

## Example

```plaintext
user: Explain these files | chatbot-openai.py | settings_example.py
assistant: Great! Let’s break down what these two files are doing...

user: What is this? | .file/DSC9999.JPG
assistant: This image shows a group of people having a meal together on a boat...
```

## Configuration

* **MODEL**: OpenAI model (e.g. `gpt-5`, `gpt-4.1`, `o4-mini`)
* **TEMPERATURE**: Higher = more creative, Lower = more deterministic
* **REASONING\_EFFORT**: Controls reasoning depth (`low` / `medium` / `high` / `minimal`)
  *(only for reasoning models including `gpt-5`, `gpt-5-mini`)*

## Notes

* `max_completion_tokens` depends on the model
* If `REASONING_EFFORT="minimal"` is set for non-`gpt-5` models, it falls back to `low`

## License

MIT