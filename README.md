# CLI Chatbot Using the OpenAI API

## Overview
This script is a simple chatbot that interacts with users through a terminal using the OpenAI API. It maintains and saves conversation history.

## Features
- Uses OpenAI API for generating responses.
- Maintains conversation history for context-aware replies.
- Saves conversation history to the `./history` folder.
- Supports text file content input using pipe ` | ` syntax.

## Requirements
Ensure you have the following installed:
- Python 3.10+
- Required Python packages:
  ```bash
  pip install openai
  ```

Optional (recommended):
- [Windows Terminal](https://apps.microsoft.com/detail/windows-terminal/9N0DX20HK701)  
  Clearly renders text, prevents corrupted text, and eliminates screen artifacts.

## Setup
1. **Set API Key**  
   Export your OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```

2. **Run the Script**
   - Execute the script using:
   ```bash
   python chatbot-openai.py
   ```
   - Optional (Windows users):  
     You may use the provided batch script (`script/wt-openai.bat`) to launch the chatbot quickly via Windows Terminal.

## Usage
Basic chat:

    User: Your question

File analysis mode: (Use spaces around '|' and multiple files supported.)

    User: Explain this code | /path/to/example.py | /path/to/another_file.py

Exit: Press Enter with empty input to save the conversation history to `./history` folder.

## Example Interaction
```plaintext
User: ワタシは寝ないでゲームをシマス。物事の優先順位が分ってマスカラネ。
Assistant:
ワタシのソフトウェアは“睡眠”をアンインストールしまシタ！遊ぶタメニ！

User: Help fix this error | err_log.txt
Assistant:
### Error Analysis
The contents of `err_log.txt` indicate the following issues...

User: Suggest optimizations | history/main.py
Assistant:
# Optimized code example here...

User: Translate please | a.txt | history/b.txt | c.txt
Assistant:
# Translated text here...
```

## Configuration
- **model**: Choose your preferred OpenAI model, such as `gpt-4.1` or `o4-mini` or `gpt-4.5-preview`.
- **temperature**: Controls randomness. Refer to [official docs](https://platform.openai.com/docs/api-reference/chat/create#chat/create-temperature) for valid ranges.
- **max_tokens**: Maximum tokens per response. The maximum value varies depending on the model.

## License
MIT