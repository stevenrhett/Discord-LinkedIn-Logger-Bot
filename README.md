
# Discord LinkedIn Logger Bot

A Python bot for Discord that captures LinkedIn profile URLs posted in specific channels and logs them, along with the author’s username, into a designated Google Sheet.

#### Table of Contents

	•	Requirements
	•	Setup Instructions
	•	Running the Bot
	•	Usage
	•	Troubleshooting

#### Requirements

	•	Python 3.8+
	•	Discord Bot Token (from the Discord Developer Portal)
	•	Google Cloud Account (to enable the Google Sheets API)
	•	Google Sheets API Credentials (credentials.json file)

### Setup Instructions

1. Set Up the Google Sheets API

	1.	Go to the Google Cloud Console.
	2.	Create a new project (or select an existing one).
	3.	Enable the Google Sheets API and Google Drive API for this project.
	4.	Go to APIs & Services > Credentials and create a new Service Account.
	5.	Download the credentials.json file for the service account and save it in the same directory as the bot script.
	6.	Share your Google Sheet with the service account email found in the credentials.json file and grant it Editor access.

2. Configure OAuth Consent Screen (if prompted)

In APIs & Services > OAuth consent screen, set up an app name, support email, and developer contact information.

3. Create and Configure the Discord Bot

	1.	Go to the Discord Developer Portal.
	2.	Create a new application, navigate to the Bot section, and click Add Bot.
	3.	Under OAuth2 > URL Generator, select the following permissions:
	•	Read Messages/View Channels
	•	Send Messages
	•	Read Message History
	4.	Generate an invite link and add the bot to your server.
	5.	Copy the Bot Token (found in the Bot section) for use in the script.

4. Install Dependencies

Activate a virtual environment and install the required libraries:

python3 -m venv .venv
source .venv/bin/activate
pip install discord.py google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client certifi python-dotenv

Running the Bot

1. Update the Bot Script

Use the following code, replacing YOUR_SPREADSHEET_ID and YOUR_DISCORD_TOKEN with your specific values:
```
import os
import re
import certifi
import ssl
import discord
import aiohttp
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")

# Set up Discord client
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Custom SSL context to ignore certificate verification for testing only
ssl_ctx = ssl.create_default_context(cafile=certifi.where())
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# Patch aiohttp globally to ignore SSL
original_request = aiohttp.ClientSession._request
def new_request(self, *args, **kwargs):
    kwargs['ssl'] = ssl_ctx
    return original_request(self, *args, **kwargs)

aiohttp.ClientSession._request = new_request

# Set up Google Sheets API
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)

# Function to append data to Google Sheets
def append_data_to_sheet(username, url):
    try:
        sheet = service.spreadsheets()
        request = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range="Sheet1!A:B",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [[username, url]]}
        )
        request.execute()
        print(f"Successfully logged {username}'s URL to Google Sheets: {url}")
    except Exception as e:
        print("Error logging URL to Google Sheets:", e)

@client.event
async def on_ready():
    print(f'Bot is ready and logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    linkedin_urls = re.findall(r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+|www\.linkedin\.com/in/[a-zA-Z0-9_-]+', message.content)

    for url in linkedin_urls:
        if not url.startswith("http"):
            url = "https://" + url

        author_name = message.author.display_name
        append_data_to_sheet(author_name, url)
        print(f'LinkedIn URL logged: {url} by {author_name}')
```
# Run the Discord bot
client.run(DISCORD_TOKEN)

2. Run the Script

Start the bot:

python discord_google_sheets_bot.py

3. Test the Bot

	•	Send a LinkedIn URL in the designated channel (e.g., #new-channel).
	•	Verify that both the URL and the author’s username appear in your Google Sheet.

Usage

	•	The bot monitors messages for LinkedIn URLs in the specified channel.
	•	It automatically logs each LinkedIn URL and the author’s display name to the Google Sheet.

Troubleshooting

	•	OAuth Consent Screen Errors: Ensure the OAuth consent screen is configured and your app is published if you see warnings.
	•	Permission Denied: Make sure the Google Sheet is shared with the service account email from credentials.json.
	•	Partial URLs: Update the regex pattern in on_message to capture full LinkedIn URLs.
___
___
