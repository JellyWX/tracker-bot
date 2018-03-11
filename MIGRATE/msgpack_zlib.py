import zlib
import msgpack

with open('../DATA/USER_DATA', 'rb') as f:
    data = msgpack.unpack(f, encoding='utf8')

with open('../DATA/USER_DATA', 'wb') as f:
    f.write(zlib.compress(msgpack.packb(data)))
