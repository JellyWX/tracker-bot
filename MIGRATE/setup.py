import msgpack
import sqlite3
import json

with open('../DATA/USER_TRACKED.json', 'w') as f:
    json.dump([], f)

connection = sqlite3.connect('../DATA/data.db')
cursor = connection.cursor()

command = '''CREATE TABLE self
uptime INTEGER
'''
cursor.execute(command)

connection.commit()
connection.close()
