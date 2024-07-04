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
            await interaction.response.send_message("Here are the upcoming CTF events:", ephemeral=True)

            for embed in ctf_events:
                await interaction.followup.send(embed=embed)
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

        embeds = []
        for event in events:
            title = event['title']
            start = format_datetime(event['start'])
            finish = format_datetime(event['finish'])
            event_url = event['url']
            color = random.randint(0, 0xFFFFFF)
            icon = random.choice(["🔥", "🚀", "✨", "🏆", "🔍"])

            embed = discord.Embed(title=f"{icon} {title}", color=color)
            embed.add_field(name="Start", value=start, inline=False)
            embed.add_field(name="Finish", value=finish, inline=False)
            embed.add_field(name="URL", value=f"[Link]({event_url})", inline=False)
            embeds.append(embed)

        return embeds
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
