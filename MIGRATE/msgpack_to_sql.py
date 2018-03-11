import msgpack
import sqlite3

with open('../DATA/USER_DATA', 'rb') as f:
    data = msgpack.unpack(f, encoding='utf8')

connection = sqlite3.connect('../DATA/data.db')
cursor = connection.cursor()

for user, values in data.items():
    command = '''CREATE TABLE u{user} (
    game VARCHAR(50),
    time INT
    )
    '''.format(user=user)

    cursor.execute(command)

    for game, time in values.items():
        command = '''INSERT INTO u{user} (game, time)
        VALUES (?, ?);'''.format(user=user)
        cursor.execute(command, (game, time))

connection.commit()
connection.close()
