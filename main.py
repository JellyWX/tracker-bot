from tracker import Tracker
import discord
import asyncio
import sys
import os

class TrackerClient(discord.Client):
  def __init__(self, *args, **kwargs):
    super(TrackerClient, self).__init__(*args, **kwargs)
    self.tracker = Tracker(self)

  async def on_ready(self):
    print('Online now!')
    self.commands = {
      'ping' : self.ping,
    }

  async def on_message(self, message):
    if not await self.get_cmd(message):
      pass

  async def get_cmd(self, message):
    if message.content.split(' ')[0] in self.commands.keys():
      await self.commands[message.content.split(' ')[0]](message)
      return True

    return False

  async def ping(self, message):
    await message.channel.send('pong')

  async def Update(self):
    await client.wait_until_ready()
    while not client.is_closed():
      await self.tracker.Update()

      await asyncio.sleep(20)


try: ## token grabbing code
  with open('token','r') as token_f:
    token = token_f.read().strip('\n')

except:
  print('no token provided')
  sys.exit(-1)

client = TrackerClient()
client.loop.create_task(client.Update())
client.run(token)
