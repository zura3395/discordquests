# Discord Quest Heartbeat Tool (Python)

This Python script mirrors the behavior of the in-page JavaScript from `index.html`, sending heartbeat requests to the Discord Quests API using the Discord desktop User-Agent.

## Requirements

- Python 3.9+
- `requests` library

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Usage

Run the script and follow the prompts. Each required value can fall back to the corresponding `DQ_*` environment variable if you press Enter without typing anything.

Required inputs:

- Quest ID or URL
- Voice Channel ID
- User ID
- Authorization header (hidden input)
- X-Super-Properties header (hidden input)

You can pre-populate defaults with environment variables using an `.env` file.
Create a file with the contents:

```py
DQ_VOICE_CHANNEL_ID=numbers
DQ_USER_ID=numbers
DQ_AUTHORIZATION="content"
DQ_X_SUPER_PROPERTIES="content"
```

The script sets the User-Agent to:

```text
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9210 Chrome/134.0.6998.205 Electron/35.3.0 Safari/537.36
```
