#!/usr/bin/env python
import os
from binascii import hexlify
from time import time
from hashlib import sha256

import freecoin as fc

class Block(fc.classes.Serializable):
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
        latest = fc.chain.get_highest_chained_block()
        if latest is None:
            fc.logger.error("Failed to generate workblock do to failure to retrieve highest chained block!")
            return None
        
        block = fc.Block()
        block.version     = fc._VERSION_
        block.time        = int(time())
        block.height      = latest.height + 1
        block.prev_hash   = latest.compute_hash()
        block.target      = fc.chain.compute_next_target(latest)
        block.nonce       = 0
        block.tx_count    = 1
        block.txs         = [fc.Tx().generate_coinbase(addr)]
        block.recompute_merkle_root()
        return block
    
    # Only call on pseudo-valid blocks!
    def to_file(self):
        os.makedirs(fc.DIR_BLOCKS, exist_ok=True)
        with open(os.path.join(fc.DIR_BLOCKS,hexlify(self.compute_hash()).decode()), 'wb') as f:
            assert self.to_bytes() == fc.Block.from_bytes(self.to_bytes()).to_bytes()
            f.write(self.to_bytes())
        os.makedirs(fc.DIR_TXINDEX, exist_ok=True)
        with open(os.path.join(fc.DIR_TXINDEX,hexlify(self.compute_hash()).decode()), 'wb') as f:
            for tx in self.txs:
                f.write(tx.compute_hash())

    def delete_file(self):
        os.remove(os.path.join(fc.DIR_BLOCKS,hexlify(self.compute_hash()).decode()))
        os.remove(os.path.join(fc.DIR_TXINDEX,hexlify(self.compute_hash()).decode()))
    
    @staticmethod
    def from_file(hash):
        if type(hash) is not str:
            hash = hexlify(hash).decode()
        if not hash.isalnum():
            return None
        fname = os.path.join(fc.DIR_BLOCKS,hash)
        try:
            with open(fname,'rb') as f:
                bytes = f.read()
                assert Block.from_bytes(bytes).to_bytes() == bytes
                return Block.from_bytes(bytes)
        except FileNotFoundError:
            return None
    
    @staticmethod
    def from_bytes(bytes):
        block = Block()
        block.version     = int.from_bytes(bytes[0:2]  , byteorder='big')
        block.time        = int.from_bytes(bytes[2:6]  , byteorder='big')
        block.height      = int.from_bytes(bytes[6:10] , byteorder='big')
        block.prev_hash   = bytes[10:42]
        block.merkle_root = bytes[42:74]
        block.target      = bytes[74:78]
        block.nonce       = int.from_bytes(bytes[78:82], byteorder='big')
        block.tx_count    = int.from_bytes(bytes[82:86], byteorder='big')
        
        block.txs = []
        i = 86
        for _k in range(block.tx_count):
            tx = fc.Tx.from_bytes(bytes[i:])
            block.txs.append(tx)
            i += tx.compute_raw_size()
        return block
    
    def to_bytes(self):
        assert(len(self.prev_hash) == 32)
        assert(len(self.merkle_root) == 32)
        assert(len(self.target) == 4)
        bytes = b""
        bytes += self.version.to_bytes(2, byteorder='big')
        bytes += self.time.to_bytes(4, byteorder='big')
        bytes += self.height.to_bytes(4, byteorder='big')
        bytes += self.prev_hash
        bytes += self.merkle_root
        bytes += self.target
        bytes += self.nonce.to_bytes(4, byteorder='big')
        bytes += self.tx_count.to_bytes(4, byteorder='big')
        
        for tx in self.txs:
            bytes += tx.to_bytes()
        
        return bytes
    
    def compute_surplus(self):
        return fc.MINING_REWARD + sum(tx.compute_surplus() for tx in self.txs)
    
    def is_pseudo_valid(self):
        raise NotImplementedError
    
    def is_chain_valid(self):
        if self.height == 0:
            if self.compute_hash() == fc.admin.ONE_TRUE_ROOT:
                return True
            else:
                return False
        elif self.height < 0:
            return False
        else:
            prev = fc.Block.from_file(self.prev_hash)
            if prev is None:
                return False
            if self.time <= prev.time:
                return False
            if self.height != (prev.height + 1):
                return False
            if self.target != fc.chain.compute_next_target(prev):
                return False
        for tx in self.txs:
            if not tx.is_chain_valid_wrt(self):
                return False
        return True
        
    def recompute_merkle_root(self):
        leaves = [sha256(tx.to_bytes()).digest() for tx in self.txs]
        while len(leaves) > 2:
            branch = fc.util.divide(leaves, 2)
            leaves = [sha256(b"".join(limb)).digest() for limb in branch]
        self.merkle_root = sha256(b"".join(leaves)).digest()
