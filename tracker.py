import datetime
import sqlite3
import msgpack
import discord

class Tracker(object):

    def __init__(self, client):
        self.client = client
        self.data = {'self' : {'Uptime' : 0}}
        self.INTERVAL = 20

        try:
            with open('USER_DATA', 'rb') as f:
                self.data = msgpack.unpack(f, encoding='utf8')
        except FileNotFoundError:
            with open('USER_DATA', 'wb') as f:
                msgpack.pack(self.data, f)

    async def Update(self):
        with open('USER_DATA-backup', 'wb') as f:
            msgpack.pack(self.data, f)

        self.clear()

        self.data['self']['Uptime'] += 1

        members = []
        member_ids = []
        patrons = self.client.get_patrons()
        for member in self.client.get_all_members():
            if member.id in member_ids:
                continue
            else:
                members.append(member)
                member_ids.append(member.id)

        for member in members:

            if member.bot or (member not in patrons and member not in self.client.get_guild(398546681618104323).members):
                continue

            if member.id in self.client.no_track:
                self.data[member.id] = {'Online' : 0, 'Idle' : 0, 'DnD' : 0}
                continue

            if member.id not in self.data.keys():
                self.data[member.id] = {'Online' : 0, 'Idle' : 0, 'DnD' : 0}

            if member.game == None:
                if member.status == discord.Status.online:
                    self.data[member.id]['Online'] += 1
                elif member.status == discord.Status.idle:
                    self.data[member.id]['Idle'] += 1
                elif member.status == discord.Status.dnd:
                    self.data[member.id]['DnD'] += 1
                continue

            if member.game.name not in self.data[member.id].keys():
                self.data[member.id][member.game.name] = 0

            self.data[member.id][member.game.name] += 1

        with open('USER_DATA', 'wb') as f:
            msgpack.pack(self.data, f)

    def getUser(self, id : int):
        if id not in self.data.keys():
            return None
        else:
            e = {x : y for x, y in self.data[id].items() if y > 0}
            offline = self.data['self']['Uptime'] - sum(e.values())
            if offline > 0:
                e['Offline'] = offline
            return e

    def clear(self):
        if datetime.datetime.now().strftime('%A-%H-%M') == 'Monday-20-00':
            self.data = {'self' : {'Uptime' : 0}}
