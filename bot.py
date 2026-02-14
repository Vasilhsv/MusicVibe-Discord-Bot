# (c) 2024 Vasilhs Vartholomaios. All Rights Reserved.
# Unauthorized copying and modification is strictly prohibited.
import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv
import traceback
load_dotenv()
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'socket_timeout': 10,
    'extract_flat': False,
    'force_generic_extractor': False
}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
}
@bot.event
async def on_ready():
    print(f'--------------------------------')
    print(f'{bot.user} is online! MusicVibe ready.')
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")
    print(f'--------------------------------')
@bot.tree.command(name="join", description="Join your voice channel")
@bot.event
async def on_guild_join(guild):
    owner = guild.owner
    welcome_msg = (
        f"👋 **Hi {owner.name}! Thanks for inviting MusicVibe to `{guild.name}`!**\n\n"
        "I'm here to bring the best music to your voice channels. 🎶\n"
        "To get started, simply type `/join` in a voice channel and then `/play` your favorite song.\n\n"
        "🔗 **Useful Links:**\n"
        "• [Terms of Service](https://github.com/Vasilhsv/MusicVibe-Discord-Bot/blob/main/TOS.md)\n"
        "• [Privacy Policy](https://github.com/Vasilhsv/MusicVibe-Discord-Bot/blob/main/PRIVACY.md)\n"
        "• [Support Server](https://discord.com/channels/1472248087354540237/1472260062419620106)\n\n"
        "Enjoy the music! 🎧"
    )

    try:
        await owner.send(welcome_msg)
        print(f"Sent welcome DM to the owner of {guild.name}.")
    except Exception as e:
        print(f"Could not send DM to {owner.name}: {e}")
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
    bot.run(os.getenv('DISCORD_TOKEN'))