#!/usr/bin/env python

import freecoin as fc
from freecoin.util import _VERSION_

DIR_BLOCKS = os.path.join(DIR_STORAGE, "blocks/")
DIR_TXINDEX = os.path.join(DIR_STORAGE, "txindex/")

class Block:
    def __init__(self):
        self.version     = None
        self.time        = None
        self.height      = None
        self.prev_hash   = None
        self.merkle_root = None
        self.target      = None
        self.nonce       = None
        self.tx_count    = None
        self.txs         = None
    
    def generate_workblock(addr):
        latest = fc.get_highest_chained_block()
        block = Block()
        block.version     = _VERSION_
        block.time        = time()
        block.height      = latest.height + 1
        block.prev_hash   = latest.compute_hash()
        block.recompute_merkle_root()
        block.target      = fc.chain.compute_next_target(latest)
        block.nonce       = 0
        block.tx_count    = 1
        block.txs         = [fc.Tx().generate_coinbase(addr)]
        return block
    
    # Only call on valid blocks!
    def save(self):
        os.makedirs(DIR_BLOCKS, exist_ok=True)
        with open(os.path.join(DIR_BLOCKS,self.compute_hash()), 'wb') as f:
            f.write(self.serialize())
        os.makedirs(DIR_TXINDEX, exist_ok=True)
        with open(os.path.join(DIR_TXINDEX,self.compute_hash()), 'wb') as f:
            for tx in self.txs:
                f.write(tx.serialize())
    
    @staticmethod
    def load(hash):
        block = Block()
        fname = os.path,join(DIR_BLOCKS,hash)
        if not os.path.isfile(fname):
            return None
        with open(fname,'rb') as f:
            block.deserialize(f.read())
        return block
        
    def deserialize(self, bytes):
        self.version     = int.from_bytes(bytes[0:2]  , byteorder='big')
        self.time        = int.from_bytes(bytes[2:6]  , byteorder='big')
        self.height      = int.from_bytes(bytes[6:10] , byteorder='big')
        self.prev_hash   = bytes[10:42]
        self.merkle_root = bytes[42:74]
        self.target      = int.from_bytes(bytes[74:76], byteorder='big')
        self.nonce       = int.from_bytes(bytes[76:80], byteorder='big')
        self.tx_count    = int.from_bytes(bytes[80:84], byteorder='big')
        
        self.txs = []
        c = 84
        for tx in self.txs:
            tx = Tx()
            tx.deserialize(bytes[84:])
            txs.append(tx)
            c += tx.compute_size()
    
    def serialize(self):
        bytes = b""
        bytes +=  self.version.to_bytes(2, byteorder='big')
        bytes +=     self.time.to_bytes(4, byteorder='big')
        bytes +=   self.height.to_bytes(4, byteorder='big')
        bytes +=  self.prev_hash
        bytes +=  self.merkle_root
        bytes +=   self.target.to_bytes(2, byteorder='big')
        bytes +=    self.nonce.to_bytes(4, byteorder='big')
        bytes += self.tx_count.to_bytes(4, byteorder='big')
        
        for tx in self.txs:
            bytes += tx.serialize()
        
        return bytes
