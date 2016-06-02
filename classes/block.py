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
    
    @staticmethod
    def generate_workblock(addr):
        latest = fc.get_highest_chained_block()
        block = Block()
        block.version     = _VERSION_
        block.time        = time()
        block.height      = latest.height + 1
        block.prev_hash   = latest.compute_hash()
        block.target      = fc.chain.compute_next_target(latest)
        block.nonce       = 0
        block.tx_count    = 1
        block.txs         = [fc.Tx().generate_coinbase(addr)]
        block.recompute_merkle_root()
        return block
    
    # Only call on valid blocks!
    def to_file(self):
        os.makedirs(DIR_BLOCKS, exist_ok=True)
        with open(os.path.join(DIR_BLOCKS,self.compute_hash()), 'wb') as f:
            f.write(self.to_bytes())
        os.makedirs(DIR_TXINDEX, exist_ok=True)
        with open(os.path.join(DIR_TXINDEX,self.compute_hash()), 'wb') as f:
            for tx in self.txs:
                f.write(tx.compute_hash())
    
    @staticmethod
    def from_file(hash):
        fname = os.path,join(DIR_BLOCKS,hash)
        if not os.path.isfile(fname):
            return None
        with open(fname,'rb') as f:
            return Block.from_bytes(f.read())
    
    @staticmethod
    def from_bytes(bytes):
        block = Block()
        block.version     = int.from_bytes(bytes[0:2]  , byteorder='big')
        block.time        = int.from_bytes(bytes[2:6]  , byteorder='big')
        block.height      = int.from_bytes(bytes[6:10] , byteorder='big')
        block.prev_hash   = bytes[10:42]
        block.merkle_root = bytes[42:74]
        block.target      = bytes[74:76]
        block.nonce       = int.from_bytes(bytes[76:80], byteorder='big')
        block.tx_count    = int.from_bytes(bytes[80:84], byteorder='big')
        
        # WILDLY BROKEN TODO FIX
        block.txs = []
        c = 84
        for tx in block.txs:
            tx = Tx.from_bytes(bytes[84:])
            if tx is None:
                return None
            txs.append(tx)
            c += tx.compute_size()
    
    def to_bytes(self):
        bytes = b""
        bytes +=  self.version.to_bytes(2, byteorder='big')
        bytes +=     self.time.to_bytes(4, byteorder='big')
        bytes +=   self.height.to_bytes(4, byteorder='big')
        bytes +=  self.prev_hash
        bytes +=  self.merkle_root
        bytes +=  self.target
        bytes +=    self.nonce.to_bytes(4, byteorder='big')
        bytes += self.tx_count.to_bytes(4, byteorder='big')
        
        for tx in self.txs:
            bytes += tx.to_bytes()
        
        return bytes
    
    def is_chain_valid(self):
        if self.height is 0:
            if self.compute_hash() == ONE_TRUE_ROOT:
                return True
            else
                return False
        elif height < 0:
            return False
        else
            prev = fc.Block.from_file(self.prev_hash)
            if prev is None:
                return False
            if self.time <= prev.time:
                return False
            if self.height != (prev.height + 1):
                return False
            if self.target() != fc.chain.compute_next_target(prev):
                return False
        for tx in self.txs:
            if not tx.is_chain_valid():
                return False
