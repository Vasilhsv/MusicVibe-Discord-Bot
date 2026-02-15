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
intents.members = True 
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
current_song = {}
@bot.tree.command(name="queue", description="Show the current music queue")
async def show_queue(interaction: discord.Interaction):
    guild_id = interaction.guild.id
    if guild_id in queues and queues[guild_id]:
        song_list = "\n".join([f"{i+1}. {song['title']}" for i, song in enumerate(queues[guild_id][:10])])
        
        embed = discord.Embed(
            title="🎶 Current Queue",
            description=song_list,
            color=discord.Color.blue()
        )
        if len(queues[guild_id]) > 10:
            embed.set_footer(text=f"And {len(queues[guild_id]) - 10} more songs...")
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("📁 The queue is currently empty.")
@bot.tree.command(name="next", description="Skip to the next song in the queue")
async def next_song(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if voice_client and (voice_client.is_playing() or voice_client.is_paused()):
        voice_client.stop()
        await interaction.response.send_message("⏭️ Skipped to the next song!")
    else:
        await interaction.response.send_message("❌ There is no song playing to skip.", ephemeral=True)
@bot.tree.command(name="nowplaying", description="Show details of the song currently playing")
async def nowplaying(interaction: discord.Interaction):
    voice_client = interaction.guild.voice_client
    if not voice_client or not voice_client.is_playing():
        await interaction.response.send_message("❌ Nothing is playing right now.", ephemeral=True)
        return
    info = current_song.get(interaction.guild.id)
    if info:
        title = info.get('title', 'Unknown Title')
        url = info.get('webpage_url', '')
        thumbnail = info.get('thumbnail', '')
        duration = info.get('duration_string', 'Unknown')
        uploader = info.get('uploader', 'Unknown')
        embed = discord.Embed(
            title="🎶 Now Playing",
            description=f"[{title}]({url})",
            color=discord.Color.green()
        )
        embed.add_field(name="Duration", value=duration, inline=True)
        embed.add_field(name="Uploader", value=uploader, inline=True)
        if thumbnail:
            embed.set_image(url=thumbnail)     
        embed.set_footer(text=f"Requested by {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("❌ Could not retrieve song info.")
@bot.tree.command(name="commands", description="Explore all MusicVibe features and commands")
async def commands_list(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎵 MusicVibe - Command Guide",
        description="Master the rhythm with these available commands:",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="📡 Connection", 
        value=(
            "`/join` - Summons the bot to your voice channel.\n"
            "`/leave` - Dismisses the bot from the channel."
        ), 
        inline=False
    )
    embed.add_field(
        name="▶️ Music Playback", 
        value=(
            "`/play [search]` - Plays a song or YouTube link.\n"
            "`/nowplaying` - Shows details of the current song.\n"
            "`/next` - Play next song from queue\n"
            "`/queue` - You can which song is next\n"
            "`/pause` - Temporarily stops the music.\n"
            "`/resume` - Continues playing from where it stopped.\n"
            "`/stop` - Ends the music and clears the player."
        ), 
        inline=False
    )
    embed.add_field(
        name="🛠️ Support & Info", 
        value=(
            "`/invite` - Get the link to add me to other servers.\n"
            "`/commands` - Opens this menu."
        ), 
        inline=False
    )
    if bot.user.avatar:
        embed.set_thumbnail(url=bot.user.avatar.url)
   
    embed.set_footer(text="MusicVibe | Created with ❤️ by Vasilhs Vartholomaios")
    await interaction.response.send_message(embed=embed)
@bot.tree.command(name="invite", description="Get the invite link for MusicVibe")
async def invite(interaction: discord.Interaction):
    client_id = bot.user.id
    invite_link = f"https://discord.com/api/oauth2/authorize?client_id={client_id}&permissions=8&scope=bot%20applications.commands"
    embed = discord.Embed(
        title="🎵 Invite MusicVibe",
        description=f"Click [here]({invite_link}) to invite me to your server!",
        color=discord.Color.blue()
    )
    embed.set_footer(text="Thanks for using MusicVibe!")
    await interaction.response.send_message(embed=embed)
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
@bot.event
async def on_guild_join(guild):
    owner = guild.owner
    if owner:
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
queues = {}
def check_queue(interaction, guild_id):
    if guild_id in queues and queues[guild_id]:
        info = queues[guild_id].pop(0)
        current_song[guild_id] = info
        url = info['url']
        voice_client = interaction.guild.voice_client
        voice_client.play(
            discord.FFmpegPCMAudio(source=url, **FFMPEG_OPTIONS), 
            after=lambda e: check_queue(interaction, guild_id)
        )
    else:
        if guild_id in current_song:
            del current_song[guild_id]
@bot.tree.command(name="play", description="Play a song or add it to the queue")
@app_commands.describe(search="The name or URL of the song")
async def play(interaction: discord.Interaction, search: str):
    await interaction.response.defer()
    if not interaction.guild.voice_client:
        if interaction.user.voice:
            await interaction.user.voice.channel.connect()
        else:
            return await interaction.followup.send("❌ Join a voice channel first.")
    voice_client = interaction.guild.voice_client
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            guild_id = interaction.guild.id

            if voice_client.is_playing() or voice_client.is_paused():
                if guild_id not in queues:
                    queues[guild_id] = []
                queues[guild_id].append(info)
                await interaction.followup.send(f"✅ Added to queue: **{info['title']}**")
            else:
                current_song[guild_id] = info
                voice_client.play(
                    discord.FFmpegPCMAudio(source=info['url'], **FFMPEG_OPTIONS), 
                    after=lambda e: check_queue(interaction, guild_id)
                )
                await interaction.followup.send(f"🎶 Now Playing: **{info['title']}**")
        except Exception as e:
            print(f"Play error: {e}")
            await interaction.followup.send("❌ Could not play the song.")
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
app = Flask('')
@app.route('/')
def home():
    return "I am alive!"
def run():
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()
keep_alive()
if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))