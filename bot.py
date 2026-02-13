import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread
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
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'noplaylist': 'True',
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
    'options': '-vn'
}
@bot.event
async def on_ready():
    print(f'--------------------------------')
    print(f'{bot.user} is online! MusicVibe ready.')
    print(f'--------------------------------')
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f'👍 Joined **{channel}**!')
    else:
        await ctx.send('❌ You need to be in a voice channel first.')
@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send('👋 Disconnected!')
    else:
        await ctx.send('❌ I am not in a voice channel.')
@bot.command()
async def play(ctx, *, search):
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("❌ You are not in a voice channel.")
            return
    await ctx.send(f'🔎 Searching for **{search}**...')
    with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            url = info['url']
            title = info['title']
            voice_client = ctx.voice_client
            if voice_client.is_playing():
                voice_client.stop()
            ffmpeg_executable = os.path.join(os.getcwd(), 'ffmpeg')
            ctx.voice_client.play(discord.FFmpegPCMAudio(executable=ffmpeg_executable, source=url, **FFMPEG_OPTIONS))
            await ctx.send(f'🎶 Now Playing: **{title}**')   
        except Exception as e:
            await ctx.send("❌ An error occurred. Try another song.")
            print(f"Error: {e}")
@bot.command()
async def pause(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Music paused.")
    else:
        await ctx.send("❌ Nothing is playing right now.")
@bot.command()
async def resume(ctx):
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Music resumed.")
    else:
        await ctx.send("❌ The music is not paused.")
@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        await ctx.send("⏹️ Music stopped.")
    else:
        await ctx.send("❌ I am not playing anything.")
from flask import Flask
from threading import Thread
app = Flask('')
@app.route('/')
def home():
    return "I'm alive"
def run():
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()
keep_alive()
bot.run(os.getenv('DISCORD_TOKEN'))