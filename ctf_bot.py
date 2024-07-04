import discord
import requests
import random
from requests.exceptions import HTTPError
from dateutil import parser
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the bot token from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await bot.tree.sync()

@bot.tree.command(name="upcoming", description="Get upcoming CTF events")
@app_commands.describe(limit="Number of events to retrieve")
async def upcoming(interaction: discord.Interaction, limit: int):
    if limit <= 0:
        await interaction.response.send_message("Please enter a positive integer for the limit.", ephemeral=True)
        return

    try:
        ctf_events_table = get_ctf_events(limit)
        if ctf_events_table:
            # Send the table wrapped in quotes
            await interaction.response.send_message(f"```\n{ctf_events_table}\n```", ephemeral=True)
        else:
            await interaction.response.send_message('Could not fetch CTF events.', ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f'An error occurred: {e}', ephemeral=True)

def get_ctf_events(limit=5):
    url = f'https://ctftime.org/api/v1/events/?limit={limit}'
    headers = {
        'User-Agent': 'DiscordBot (your-email@example.com)'  # Replace with your email
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        events = response.json()

        # Create a table header
        table = f"{'Title':<30} {'Start':<20} {'Finish':<20} {'URL':<30}\n"
        table += "-" * 100 + "\n"

        for event in events:
            title = event['title']
            start = format_datetime(event['start'])
            finish = format_datetime(event['finish'])
            event_url = event['url']

            # Format each row of the table
            table += f"{title:<30} {start:<20} {finish:<20} {event_url:<30}\n"

        return table
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return None
    except Exception as err:
        print(f'Error occurred: {err}')
        return None

def format_datetime(datetime_str):
    datetime_obj = parser.isoparse(datetime_str)
    return datetime_obj.strftime("%d-%m-%Y %H:%M:%S")

bot.run(DISCORD_TOKEN)
