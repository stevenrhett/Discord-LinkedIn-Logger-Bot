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

# Custom SSL context for testing only
ssl_ctx = ssl.create_default_context(cafile=certifi.where())
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

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
        print(f"Logged {username}'s URL: {url}")
    except Exception as e:
        print("Error logging URL:", e)


@client.event
async def on_ready():
    print(f'Bot is ready and logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    linkedin_urls = re.findall(
        r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+|www\.linkedin\.com/in/[a-zA-Z0-9_-]+', message.content)

    for url in linkedin_urls:
        if not url.startswith("http"):
            url = "https://" + url
        author_name = message.author.display_name
        append_data_to_sheet(author_name, url)


client.run(DISCORD_TOKEN)
