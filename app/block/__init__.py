import json

from dateutil import parser
from sqlalchemy import Column, String, Integer, DateTime

from app import storage


class Block(storage.Base):
    __tablename__ = 'blocks'

    _id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String)
    prev_block_id = Column(String)
    prev_block_hash = Column(String)
    tx_list = Column(String)
    merkle_root = Column(String)
    time_stamp = Column(DateTime)
    block_id = Column(String)
    block_hash = Column(String)
    nonce = Column(String)
    block_info = Column(String)
    block_miner = Column(Integer)

    def __init__(self):
        self.type = 'B' # Block을 의미

    def __str__(self):
        return self.to_json()

    def to_json(self):
        return json.dumps({
            'type': self.type,
            'time_stamp': self.time_stamp.strftime('%Y%m%d%H%M%S'),
            'prev_block_id': self.prev_block_id,
            'prev_block_hash': self.prev_block_hash,
            'merkle_root': self.merkle_root,
            'block_hash': self.block_hash,
            'nonce': self.nonce,
            'block_id': self.block_id
        })

    def from_json(self, dictionary):
        """Constructor"""
        for key in dictionary:
            setattr(self, key, dictionary[key])

        self.time_stamp = parser.parse(self.time_stamp)
        return self


class GenesisBlock(object):
    def __init__(self):
        self.type = 'B'
        self.prev_block_id = 'B000000000000'
        self.prev_block_hash = 'block_hash'
        self.tx_list = 'woorichain'
        self.timp_stamp = '0000-00-00-00-00-00'
        self.block_id = 'B000000000000'
        self.merkle_root = 'connecdotsroot'
        self.block_hash = 'connecdotshash'
        self.nonce = 2010101010


def create_block(block):
    storage.insert(block)


def get_my_block():
    return 0


def count():
    return storage.count(Block)


def get_all_block():
    return storage.get_all(Block)


def get_genesis_block():
    b = Block()
    b.prev_block_id = 'B000000000000'
    b.prev_block_hash = '0'
    b.block_id = 'B000000000000'
    b.merkle_root = 'woorichain'
    b.block_hash = 'woorichain'
    b.nonce = 2010101010

    return b


def get_last_block():
    if count() == 0:
        return get_genesis_block()
    else:
        return get_all_block()[-1]


if __name__ == '__main__':

    t = GenesisBlock()
    temp = json.dumps(t, indent=4, default=lambda o: o.__dict__, sort_keys=True)
    temps = json.loads(temp)
    print(type(temps['nonce']))
