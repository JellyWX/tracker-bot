import msgpack

class Tracker(object):

  def __init__(self, client):
    self.client = client
    self.data = {}
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

    members = []
    member_ids = []
    for member in self.client.get_all_members():
      if member.id in member_ids:
        continue
      else:
        members.append(member)
        member_ids.append(member.id)

    for member in members:

      if member.bot:
        continue

      if member.id not in self.data.keys():
        self.data[member.id] = {'None' : 0}

      if member.game == None:
        self.data[member.id]['None'] += self.INTERVAL
        continue

      if member.game.name not in self.data[member.id].keys():
        self.data[member.id][member.game.name] = 0

      self.data[member.id][member.game.name] += self.INTERVAL


    with open('USER_DATA', 'wb') as f:
      msgpack.pack(self.data, f)
