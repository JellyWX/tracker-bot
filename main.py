from tracker import Tracker
import discord
import asyncio
import sys
import os

class TrackerClient(discord.Client):
  def __init__(self, *args, **kwargs):
    super(TrackerClient, self).__init__(*args, **kwargs)
    self.tracker = Tracker(self)
    self.commands = {
      'ping' : self.ping,
      'stats' : self.stats
    }

  async def on_ready(self):
    print('Online now!')

  async def on_message(self, message):
    if not await self.get_cmd(message):
      pass

  async def get_cmd(self, message):
    if self.user.id in map(lambda x: x.id, message.mentions):
      if message.content.split(' ')[1] in self.commands.keys():
        await self.commands[message.content.split(' ')[1]](message)
        return True

      return False

  async def ping(self, message):
    await message.channel.send('pong')

  async def stats(self, message):
    target = [x for x in message.content.split(' ')[1:] if x.startswith('<@')]

    if len(target) > 0:
      target = target[0][1:-1]
      while target[0] not in '0123456789':
        try:
          target = target[1:]
        except IndexError:
          await message.channel.send('Error deciphering user tagged. Make sure it\'s formatted correctly!')
          return

      target = self.get_user(int(target))
      if target == None:
        await message.channel.send('Couldn\'t find user tagged. Are you sure they\'re real?')
        return

    em = discord.Embed(title='{} stats'.format(target.name))
    for key, data in self.tracker.data[target.id].items():
      em.add_field(name=key, value='{} minutes'.format(round(data/60)))
    await message.channel.send(embed=em)

  async def Update(self):
    await client.wait_until_ready()
    while not client.is_closed():
      await self.tracker.Update()

      await asyncio.sleep(self.tracker.INTERVAL)


try: ## token grabbing code
  with open('token','r') as token_f:
    token = token_f.read().strip('\n')

except:
  print('no token provided')
  sys.exit(-1)

client = TrackerClient()
client.loop.create_task(client.Update())
client.run(token)
