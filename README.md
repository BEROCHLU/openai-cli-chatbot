# CLI Chatbot Using the OpenAI API

## Overview
This script is a simple chatbot that interacts with users through a terminal using the OpenAI API. It maintains and saves conversation history.

## Features
- Uses OpenAI API for generating responses.
- Maintains conversation history for context-aware replies.
- Saves conversation history to the `./history` folder.
- Supports Excel (`.xlsx`, automatically converted to JSON), text, or image files as input using the pipe ` | ` syntax.
- Supports text-based files (e.g., `.txt`, `.csv`, `.json`, `.py`, `.md`, etc.)
- Supports image files (`.jpg`, `.jpeg`, `.png`).
- Supports instant saving of conversation history using the `!save` command without ending the session.

## Requirements
Ensure you have the following installed:
- Python 3.10+
- Required Python packages:
  ```bash
  pip install -r requirements.txt
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
2. **Rename `settings_example.py` to `settings.py`, then open `settings.py` and set:**
   ```bash
   MODEL = "gpt-5"  # gpt-5 | gpt-5-mini | gpt-5-chat-latest | gpt-4.1 | gpt-4.1-mini | o4-mini | o3 | gpt-4o
   TEMPERATURE = 1.0
   REASONING_EFFORT = "medium"  # low | medium | high | minimal
   ```
3. **Run the Script**
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

Immediately save conversation history at any time:

    User: !save

Typing `!save` will instantly save the current conversation history without exiting.

## Example Interaction
```plaintext
user: ワタシは寝ないでゲームをシマス。物事の優先順位が分ってマスカラネ。
gpt-5-chat-latest_0.65 assistant:
ワタシのソフトウェアは“睡眠”をアンインストールしまシタ！遊ぶタメニ！

user: Explain there files | chatbot-openai.py | settings_example.py
Completed loading the file: 'chatbot-openai.py'
Completed loading the file: 'settings_example.py'
gpt-5-chat-latest_0.65 assistant:
Great! Let’s break down what these two files are doing.  

## **1. `chatbot-openai.py`**
This is the **main script** that runs the chatbot. It connects to the OpenAI API,
...

user: What is this? | .file/DSC0507.JPG
Image loaded and encoded: '.file/DSC0507.JPG'
gpt-5-chat-latest_0.65 assistant:
This image shows a **group of people having a meal together on a boat**.  

Details:  
- They are sitting under a canopy for shade.  
- The boat is out on the ocean with clear blue water visible in the background.  
- The table is full of food, including **grilled seafood, watermelon, mangoes, and other dishes**.  
- Several people are shirtless, suggesting it’s a casual beach or island trip.  
- They appear to be enjoying a feast, some giving thumbs-up signs and posing for the camera.  

So overall, this looks like a **seafood and fruit feast on a boat trip** — likely part of an island-hopping or beach outing. 🌊🍉🦐  

Would you like me to describe the **types of food on the table in more detail**?
```

## Configuration
- **MODEL**: Choose your preferred OpenAI model, such as `gpt-5`, `gpt-4.1` or `o4-mini`.
- **TEMPERATURE**: Higher means more creativity but less reproducibility; lower means more consistency and reproducibility. To be ignored in the case of reasoning models.
- **REASONING_EFFORT**: Higher means the model will take more time to process your request, and the more tokens it will consume. This parameter is only for reasoning models, including `gpt-5` and `gpt-5-mini`.

## Note
- **max_completion_tokens**: The maximum value is set depending on the model.
- **REASONING_EFFORT = "minimal"**: This value is intended for `gpt-5` and `gpt-5-mini`. If set with other reasoning models, it will be automatically changed to low.

## License
MIT