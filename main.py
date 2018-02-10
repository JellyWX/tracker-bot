from tracker import Tracker
import discord
import asyncio
import sys
import os
import json
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot

class TrackerClient(discord.Client):
  def __init__(self, *args, **kwargs):
    super(TrackerClient, self).__init__(*args, **kwargs)
    self.tracker = Tracker(self)
    self.no_track = []
    self.commands = {
      'ping' : self.ping,
      'stats' : self.stats,
      'track' : self.track,
      'help' : self.help,
      'chart' : self.chart
    }

    try:
      with open('USER_tracked.json', 'r') as f:
        self.no_track = json.load(f)
    except FileNotFoundError:
      with open('USER_tracked.json', 'w') as f:
        json.dump([], f)

  async def on_ready(self):
    print('Online now!')
    await client.change_presence(game=discord.Game(name='@TrackerBot help'))

  async def on_message(self, message):
    if not await self.get_cmd(message):
      pass

  async def get_cmd(self, message):
    if self.user.id in map(lambda x: x.id, message.mentions) and len(message.content.split(' ')) > 1:
      if message.content.split(' ')[1] in self.commands.keys():
        await self.commands[message.content.split(' ')[1]](message)
        return True

      return False

    elif isinstance(message.channel, discord.DMChannel):
      if message.content.split(' ')[0] in self.commands.keys():
        await self.commands[message.content.split(' ')[0]](message)
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

    else:
      target = message.author

    em = discord.Embed(title='{}\'s stats'.format(target.name))
    for key, data in self.tracker.getUser(target.id).items():
      em.add_field(name=key, value='{} minutes'.format(round((data * self.tracker.INTERVAL)/60)))
    await message.channel.send(embed=em)

  async def track(self, message):
    if 'disable' in message.content:
      await message.channel.send('Disabled tracking :thumbsup:')
      self.no_track.append(message.author.id)
    elif message.author.id in self.no_track:
      await message.channel.send('Enabled tracking :thumbsup:')
      self.no_track.remove(message.author.id)
    else:
      await message.channel.send('Tracking is currently enabled for you. Use `track disable` to disable tracking')

    with open('USER_TRACKED.json', 'w') as f:
      json.dump(self.no_track, f)

  async def help(self, message):
    await message.channel.send(embed=discord.Embed(
      description='''
`help` : Show this page
`stats [mention]` : Get online stats for a user
`track [disable]` : Enable or disable tracking for yourself
      '''
    ))

  async def chart(self, message):
    pyplot.clf()
    pyplot.axis('equal')
    pyplot.pie(self.tracker.getUser(message.author.id).values(), labels=self.tracker.getUser(message.author.id).keys(), autopct=lambda x: '{}mins'.format(round((x * self.tracker.INTERVAL)/60)))
    pyplot.savefig('curr.png')
    with open('curr.png', 'rb') as f:
      await message.channel.send(file=discord.File(f, 'chart.png'))

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
