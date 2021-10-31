#!/bin/python3
import os
import discord
from discord.ext import tasks
import asyncio
import sqlite3

# set values :
token = ""
channel_id = 0




class Watcher:
    def __init__(self, filename):
        self.filename = filename
        self.__timestamp = os.path.getmtime(self.filename)

    def check(self):
        timestamp = os.path.getmtime(self.filename)
        if not self.__timestamp == timestamp:
            self.__timestamp = timestamp
            return timestamp
        else:
            return False


watcher = Watcher("/var/lib/jellyfin/data/jellyfin.db")
client = discord.Client()
channel = None
message_cache = None

@client.event
async def on_ready():
    global channel
    print(f'{client.user} has connected to Discord!')
    channel = client.get_channel(channel_id)

@tasks.loop(seconds=10)
async def alert_loop():
    global message_cache
    if channel:
        timer = watcher.check()
        if timer:
            con = sqlite3.connect('/var/lib/jellyfin/data/jellyfin.db')
            cur = con.cursor()
            cur.execute(str("select name from activitylogs where datecreated > datetime({}, 'unixepoch') order by datecreated asc limit 100;".format(timer-10)))
            results = cur.fetchall()
            con.close()
            if message_cache == results:
                return
            for result in results:
                if message_cache == result[0]:
                    continue
                if "online" in result[0]:
                    continue
                elif "disconnected" in result[0]:
                    continue
                await channel.send(result[0])
                message_cache = result[0]

alert_loop.start()
client.run(token)


