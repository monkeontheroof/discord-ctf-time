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
        ctf_events = get_ctf_events(limit)
        if ctf_events:
            # Format events into a Markdown table
            headers = ["Title", "Start", "Finish", "URL"]
            table = format_as_markdown_table(ctf_events, headers)
            
            # Send the formatted table to Discord
            await interaction.response.send_message(f"```\n{table}\n```", ephemeral=True)
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

        # Prepare data for Markdown table
        event_data = []
        for event in events:
            title = event['title']
            start = format_datetime(event['start'])
            finish = format_datetime(event['finish'])
            event_url = event['url']
            event_data.append([title, start, finish, event_url])

        return event_data
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return None
    except Exception as err:
        print(f'Error occurred: {err}')
        return None

def format_datetime(datetime_str):
    datetime_obj = parser.isoparse(datetime_str)
    return datetime_obj.strftime("%d-%m-%Y %H:%M:%S")

def format_as_markdown_table(data, headers):
    # Create the table header
    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    
    # Add the data rows
    for row in data:
        table += "| " + " | ".join(str(cell) for cell in row) + " |\n"
    
    return table

bot.run(DISCORD_TOKEN)
