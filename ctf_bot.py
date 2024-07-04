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
        view = PaginationView(ctf_events, page_size, num_pages, limit)

        # Send the initial message
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
        icon = random.choice(["🔥", "🚀", "✨", "🏆", "🔍"])

        # Format each field with a clean look
        embed.add_field(
            name=f"{icon} {title}",
            value=f"**Start:** {start_time}\n**Finish:** {finish_time}\n[Link to Event]({event_url})",
            inline=False
        )
    
    embed.set_footer(text=f"Page {page + 1}/{num_pages}")
    return embed

class PaginationView(View):
    def __init__(self, events, page_size, num_pages, limit):
        super().__init__()
        self.events = events
        self.page_size = page_size
        self.num_pages = num_pages
        self.limit = limit
        self.current_page = 0

        # Initialize buttons
        self.prev_button = Button(label="Previous", style=discord.ButtonStyle.primary, disabled=True)
        self.next_button = Button(label="Next", style=discord.ButtonStyle.primary, disabled=num_pages <= 1)
        self.add_item(self.prev_button)
        self.add_item(self.next_button)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, disabled=True)
    async def prev_button(self, button: Button, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, disabled=True)
    async def next_button(self, button: Button, interaction: discord.Interaction):
        if self.current_page < self.num_pages - 1:
            self.current_page += 1
            await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        embed = create_event_embed(self.events, self.current_page, self.page_size, self.num_pages)
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= self.num_pages - 1
        await interaction.response.edit_message(embed=embed, view=self)

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
