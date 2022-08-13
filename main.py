import discord
import os
import json
from dotenv import load_dotenv
from mysqltw import MySQLTW
from twitch import Twitch
from discord.ext import tasks, commands


mysql = MySQLTW('192.168.0.4', 'bot', 'botdiscord3321', 'discord_bot', 3306)
mysql.connect()

twitch = Twitch(mysql)
load_dotenv()

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$Damian to...'):
        await message.channel.send('Kolega!')

    if message.content.startswith('Cześć'):
        await message.channel.send('Witaj!')
    
    if message.content.startswith('Elo'):
        await message.channel.send('Siemka Sushi!')
    
    if message.content.startswith('JF'):
        await message.channel.send('Zgadzam się 😈')

    if message.content.startswith('twitch add '):
        streamer = str(message.content[11:])
        twitch.twitch_check(f"https://api.twitch.tv/helix/streams?user_login={streamer}&first=1")

    
@tasks.loop(seconds=5.0)
async def live():
    await message.channel.send("Cześć")

live.start()
twitch.check_live()

twitch.check_token()


client.run(os.getenv('TOKEN'))