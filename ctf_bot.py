import discord
import requests
import random
from requests.exceptions import HTTPError
from dateutil import parser
from discord.ext import commands
from discord import app_commands

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent

# Create a bot instance with a command prefix
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    # Register the slash commands when the bot is ready
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
            # Reply with the first message
            await interaction.response.send_message("Here are the upcoming CTF events:", ephemeral=True)

            # Follow up with embeds
            for embed in ctf_events:
                await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message('Could not fetch CTF events.', ephemeral=True)

    except Exception as e:
        # Handle exceptions and send an error message
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
    # Parse the datetime string with timezone information
    datetime_obj = parser.isoparse(datetime_str)
    # Format the datetime object to the desired format
    return datetime_obj.strftime("%d-%m-%Y %H:%M:%S")

bot.run('MTI1ODMxMDIyMTgxODg5MjI5OQ.GMnlgq.d-rejWSWNWgQRik22os9m_egnhO_jspuJKn1_I')
