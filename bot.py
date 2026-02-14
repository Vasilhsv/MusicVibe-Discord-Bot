# (c) 2024 Vasilhs Vartholomaios. All Rights Reserved.
# Unauthorized copying and modification is strictly prohibited.
import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
import traceback

load_dotenv()
app = Flask('')

@app.route('/')
def home():
    return "MusicVibe is alive!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Ρυθμίσεις Intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Επιλογές YoutubeDL
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'socket_timeout': 10,
    'cookiefile': 'cookies.txt',
    'extract_flat': False,
    'force_generic_extractor': False
}

# Επιλογές FFMPEG
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f'--------------------------------')
    print(f'{bot.user} is online! MusicVibe ready.')
    # Συγχρονισμός των Slash Commands για να εμφανιστούν στο Discord
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print(f'--------------------------------')

# --- SLASH COMMANDS ---

@bot.tree.command(name="join", description="Join your voice channel")
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect()
        await interaction.response.send_message(f'👍 Joined **{channel}**!')
    else:
        await interaction.response.send_message('❌ You need to be in a voice channel first.', ephemeral=True)

@bot.tree.command(name="leave", description="Disconnect from the voice channel")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message('👋 Disconnected!')
    else:
        await interaction.response.send_message('❌ I am not in a voice channel.', ephemeral=True)

@bot.tree.command(name="play", description="Play a song from YouTube")
@app_commands.describe(search="The name or URL of the song")
async def play(interaction: discord.Interaction, search: str):
    # Χρησιμοποιούμε defer γιατί η αναζήτηση μπορεί να πάρει χρόνο
    await interaction.response.defer()

    if not interaction.guild.voice_client:
        if interaction.user.voice:
            await interaction.user.voice.channel.connect()
        else:
            await interaction.followup.send("❌ You are not in a voice channel.")
            return

    await interaction.followup.send(f'🔎 Searching for **{search}**...')

    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            url = info['url']
            title = info['title']
            voice_client = interaction.guild.voice_client

            if voice_client.is_playing():
                voice_client.stop()

            ffmpeg_executable = os.path.join(os.getcwd(), 'ffmpeg') # Ή απλά 'ffmpeg' αν είναι στο PATH
            
            # Σημείωση: Αν τρέχεις σε Linux/Container ίσως χρειαστεί σκέτο 'ffmpeg' χωρίς path
            voice_client.play(discord.FFmpegPCMAudio(executable='ffmpeg', source=url, **FFMPEG_OPTIONS))
            
            await interaction.followup.send(f'🎶 Now Playing: **{title}**')   
        except Exception as e:
            await interaction.followup.send("❌ An error occurred. Try another song.")
            print(f"Error: {e}")

@bot.tree.command(name="pause", description="Pause the current song")
async def pause(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await interaction.response.send_message("⏸️ Music paused.")
    else:
        await interaction.response.send_message("❌ Nothing is playing right now.", ephemeral=True)

@bot.tree.command(name="resume", description="Resume the paused song")
async def resume(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await interaction.response.send_message("▶️ Music resumed.")
    else:
        await interaction.response.send_message("❌ The music is not paused.", ephemeral=True)

@bot.tree.command(name="stop", description="Stop the music")
async def stop(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client:
        voice_client.stop()
        await interaction.response.send_message("⏹️ Music stopped.")
    else:
        await interaction.response.send_message("❌ I am not playing anything.", ephemeral=True)

if __name__ == "__main__":
    keep_alive() 
    bot.run(os.getenv('DISCORD_TOKEN'))