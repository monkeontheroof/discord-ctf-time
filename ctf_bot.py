import discord
import requests
import random
from requests.exceptions import HTTPError
from dateutil import parser
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the bot token from environment variables
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

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
        if not ctf_events:
            await interaction.response.send_message('Could not fetch CTF events.', ephemeral=True)
            return

        # Initialize pagination
        page_size = 5
        num_pages = (len(ctf_events) + page_size - 1) // page_size

        # Initial page
        page = 0
        embed = create_event_embed(ctf_events, page, page_size, num_pages)
        view = create_pagination_view(page, num_pages, interaction, limit)

        await interaction.response.send_message(embed=embed, view=view)

    except Exception as e:
        await interaction.response.send_message(f'An error occurred: {e}', ephemeral=True)

def create_event_embed(events, page, page_size, num_pages):
    start = page * page_size
    end = min(start + page_size, len(events))

    embed = discord.Embed(title="Upcoming CTF Events", color=random.randint(0, 0xFFFFFF))
    for event in events[start:end]:
        title = event['title']
        start_time = format_datetime(event['start'])
        finish_time = format_datetime(event['finish'])
        event_url = event['url']
        color = random.randint(0, 0xFFFFFF)
        icon = random.choice(["🔥", "🚀", "✨", "🏆", "🔍"])

        embed.add_field(name=f"{icon} {title}", value=f"**Start:** {start_time}\n**Finish:** {finish_time}\n[Link]({event_url})", inline=False)
    
    embed.set_footer(text=f"Page {page + 1}/{num_pages}")
    return embed

def create_pagination_view(current_page, total_pages, interaction, limit):
    view = View()

    async def button_callback(interaction):
        nonlocal current_page

        if interaction.custom_id == "prev":
            current_page -= 1
        elif interaction.custom_id == "next":
            current_page += 1

        # Update embed and buttons
        embed = create_event_embed(get_ctf_events(limit), current_page, page_size, total_pages)
        view = create_pagination_view(current_page, total_pages, interaction, limit)

        await interaction.response.edit_message(embed=embed, view=view)

    if current_page > 0:
        prev_button = Button(label="Previous", style=discord.ButtonStyle.primary, custom_id="prev")
        prev_button.callback = button_callback
        view.add_item(prev_button)

    if current_page < total_pages - 1:
        next_button = Button(label="Next", style=discord.ButtonStyle.primary, custom_id="next")
        next_button.callback = button_callback
        view.add_item(next_button)

    return view

def get_ctf_events(limit=5):
    url = f'https://ctftime.org/api/v1/events/?limit={limit}'
    headers = {
        'User-Agent': 'DiscordBot (your-email@example.com)'  # Replace with your email
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        events = response.json()
        return events
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return []
    except Exception as err:
        print(f'Error occurred: {err}')
        return []

def format_datetime(datetime_str):
    datetime_obj = parser.isoparse(datetime_str)
    return datetime_obj.strftime("%d-%m-%Y %H:%M:%S")

bot.run(DISCORD_TOKEN)
