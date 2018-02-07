import msgpack

class Tracker(object):

  def __init__(self, client):
    self.client = client
    self.data = {}

    #with open('USER_DATA', 'rb') as f:
    #  self.data = msgpack.unpackb(f)

  async def Update(self):
    async for user, data in self.data.items():
      user_obj = self.client.get_user(user)

      if user_obj == None or user_obj.bot:
        pass

      print(user_obj.game)
