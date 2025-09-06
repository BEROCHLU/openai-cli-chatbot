# CLI Chatbot Using the OpenAI Responses API

## Overview

A simple command-line chatbot powered by the OpenAI Responses API.  
It supports conversation history, file analysis, and instant saving.  
Uses event streaming and `previous_response_id` to maintain context.

## Features

* Conversational interface with context-aware replies
* Conversation history saved to `./history`
* File input via `^` operator:

  * Text-based files (`.txt`, `.csv`, `.py`, `.md`, etc.)
  * Excel files (`.xlsx`, automatically converted to JSON)
  * PDF files (`.pdf`, supports both **local files and URLs**)
  * Images (`.jpg`, `.jpeg`, `.png`, supports both **local files and URLs**)
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
   STREAM = True     # True | False
   REASONING_EFFORT = "medium"  # low | medium | high | minimal
   ```

3. **Run**

   ```bash
   python clichatbot.py
   ```

   *(Windows users can use `script/wt-openai.bat` to launch in Windows Terminal.)*

## Usage

**Basic chat**

```plaintext
user: Your question
```

**File analysis** (multiple files supported, space around `^` is required)

```plaintext
user: Explain these files ^ /path/to/example.py ^ /path/to/document.pdf ^ /path/to/image.png
```

**Image / PDF via URL**

```plaintext
user: Are these files related? ^ https://example.com/image.jpg ^ https://example.com/document.pdf
```

**Exit session**  
Press **Enter** on empty input → history is saved to `./history`.

**Instant save**

```plaintext
user: !save
```

## Example

```plaintext
user: Explain these files ^ clichatbot.py ^ settings_example.py
Completed loading the file: 'clichatbot.py'
Completed loading the file: 'settings_example.py'
gpt-5-medium assistant:
Here’s a clear walkthrough of what each file does, how to use the CLI chatbot, and how the pieces fit together.

Overview

- clichatbot.py: A command-line chatbot that talks to OpenAI’s Responses API. It supports:
  - Streaming and non-streaming outputs
  - Threaded conversations via previous_response_id (so you don’t resend the full history)
...

user: Analyze the letter and provide a summary of the key points. ^ https://www.berkshirehathaway.com/qtrly/2ndqtr25.pdf
Processing the file: 'https://www.berkshirehathaway.com/qtrly/2ndqtr25.pdf'
gpt-5-medium assistant:
Here’s a concise, decision‑oriented summary of Berkshire Hathaway’s Q2 2025 Form 10‑Q.

Headline results
- Net earnings attributable to Berkshire shareholders: $12.37B for Q2 (vs. $30.35B in Q2’24); $16.97B for 1H’25 (vs. $43.05B in 1H’24).
- Revenues: $92.5B in Q2 (−1% YoY); $182.2B in 1H (−1% YoY).
- EPS (equivalent): Class A $8,601; Class B $5.73.
...
```

## Configuration

* **MODEL**: OpenAI model (e.g. `gpt-5`, `gpt-4.1`, `o4-mini`)
* **TEMPERATURE**: Higher = more creative, Lower = more deterministic
* **STREAM**: Stream output
* **REASONING\_EFFORT**: Controls reasoning depth (`low` / `medium` / `high` / `minimal`)
  *(primarily used by reasoning-capable models such as `gpt-5`, `o3+`)*

## Notes

* Reasoning usage:
  - `gpt-5` (excluding `-chat-latest`): uses `reasoning.effort` as specified.
  - `o3–o9`: uses `reasoning.effort`; when `minimal` is specified it falls back to `low`.
* Set `STREAM=False` to get a single Markdown-rendered reply per turn.

## License

MIT