from tracker import Tracker
import discord
import asyncio
import sys
import os
import json
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
import itertools


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
            with open('USER_TRACKED.json', 'r') as f:
                self.no_track = json.load(f)
        except FileNotFoundError:
            with open('USER_TRACKED.json', 'w') as f:
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
        t = message.created_at.timestamp()
        e = await message.channel.send('pong')
        delta = e.created_at.timestamp() - t
        await e.edit(content='Pong! {}ms round trip'.format(round(delta * 1000)))

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
                await message.channel.send('Couldn\'t find user tagged. Are you sure they\'re real and a patron?')
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
`chart [ignore="Offline,Online,GameName..."]` : Generate a pie chart of your activities
            '''
        ))

    async def chart(self, message):
        user = self.tracker.getUser(message.author.id)

        ignore_list = []
        listing = False
        for i in message.content.split(' '):
            if i.startswith('ignore="'):
                ignore_list.append(i)
                listing = True
            elif listing:
                ignore_list.append(i)
            elif i[-1] == '"':
                ignore_list.append(i)
                listing = False
                break

        if len(ignore_list) > 0:
            ignore_list = ' '.join(ignore_list)
            listed = ignore_list.split('"')[1].replace('"', '').split(',')
            listed = [i.strip().lower() for i in listed]
            print(listed)
            user = {k: v for k, v in user.items() if k.lower() not in listed}

        pyplot.clf()
        pyplot.axis('equal')
        t = sum(user.values())
        pyplot.pie(user.values(), labels=user.keys(), autopct=lambda x: '{}mins'.format(int((((x * t) / 100) * self.tracker.INTERVAL) / 60)))
        pyplot.savefig('curr.png')

        f = open('curr.png', 'rb')
        await message.channel.send(file=discord.File(f, 'chart.png'))
        f.close()

    async def Update(self):
        await client.wait_until_ready()
        while not client.is_closed():
            await self.tracker.Update()

            await asyncio.sleep(self.tracker.INTERVAL)

    def get_patrons(self):
        p_server = self.get_guild(350391364896161793)
        p_server2 = self.get_guild(366542432671760396)
        p_roles = [discord.utils.get(p_server.roles, name='Donor'), discord.utils.get(p_server2.roles, name='Premium!')]
        premiums = [user for user in itertools.chain(p_server.members, p_server2.members) if any([p in user.roles for p in p_roles])]

        return premiums


try: ## token grabbing code
    with open('token', 'r') as token_f:
        token = token_f.read().strip('\n')

except:
    print('no token/s provided')
    sys.exit(-1)

client = TrackerClient()
client.loop.create_task(client.Update())
client.run(token)
