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

Before running the script, open and login to Discord on your web browser and do the following to get the required inputs:

- Enable Discord Developer Mode if you have not enabled it before: Go to `Settings > Advanced > Developer Mode` and turn it on.
- **Quest URL**: Accept the quest, select that you will be completing the quest on Desktop if needed. Copy the Quest URL using the Share button for the quest you want to complete. The Share button is hidden under the 3 dots ⋯ menu on the quest's banner image.
- **User ID**: Click your own username in the bottom left and select "Copy User ID".
- **Channel ID** Right-click the voice channel in any server for the quest and select "Copy Channel ID". You don't need to be in the voice channel.
- Open your browser's developer tools by pressing `F12`.
- Go to the "Network" tab in the developer tools.
- Send a message in any Discord channel. A new request named "messages" will appear at the bottom of the network log. Click on it.
- **Headers**: In the "Headers" tab for the "messages" request, scroll down to "Request Headers". Copy the values for `Authorization` and `X-Super-Properties` and paste them into the respective fields below.

You can pre-populate defaults with environment variables using an `.env` file.
Create a file with the contents in the cloned directory:

```py
DQ_VOICE_CHANNEL_ID=numbers
DQ_USER_ID=numbers
DQ_AUTHORIZATION="content"
DQ_X_SUPER_PROPERTIES="content"
```

Make sure to include quotation marks around the Authorization and X-Super-Properties headers to avoid issues with non-alphnumeric characters.

Run the script and follow the prompts. The script will skip user input for a given variable if an environment variable is available.

The script sets the User-Agent to:

```text
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9210 Chrome/134.0.6998.205 Electron/35.3.0 Safari/537.36
```
