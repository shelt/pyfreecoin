#!/usr/bin/env python
import os
from operator import attrgetter

DIR_HEADS = os.path.join(DIR_STORAGE, "heads/")

class Head:
    def __init__(self, block=None):
        height   = None
        ref_hash = None
        chained  = False
        if block:
            self.point_to(block)
    
    def point_to(self, block):
        self.height = block.height
        self.ref_hash = block.compute_hash()
        self.chained = False # chain should always be cleaned after this
        self.to_file()
    
    def to_file(self):
        os.makedirs(DIR_HEADS, exist_ok=True)
        with open(os.path.join(DIR_HEADS,self.compute_hash()), 'wb') as f:f
            f.write(self.to_bytes())
    
    @staticmethod
    def from_file(hash):
        fname = os.path,join(DIR_HEADS,hash)
        if not os.path.isfile(fname):
            return None
        with open(fname,'rb') as f:
            return Head.from_bytes(f.read())
    
    @staticmethod
    def from_bytes(self, bytes):
	    tx = Tx()
        tx.height   = int.from_bytes(bytes[0:4],  byteorder='big')
        tx.ref_hash = bytes[4:36]
        tx.chained  = bool(int.from_bytes(bytes[36], byteorder='big')
        return tx
    
    def to_bytes(self):
        bytes = b""
        bytes += self.height.to_bytes(4, byteorder='big')
        bytes += ref_hash
        bytes += int(self.chained).to_bytes(1, byteorder='big')
        return bytes
    
    def fast_forward(self, block):
        assert block.prev_hash == self.ref_hash:
            self.height += 1
            self.ref_hash = block.compute_hash()
        self.to_file()
    
    def recompute_chained(self):
        curr = fc.Block.from_file(self.ref_hash)
        retval = False
        while curr is not None:
            if curr.height == 0:
                retval = True
                break
            curr = Block.from_file(curr.prev_hash)
        
        self.chained = retval
        self.to_file()
        return retval
        
        

def enchain(block):
    # Ensure the block isn't already enchained
    block_hash = block.compute_hash()
    enchained = is_enchained(block_hash):
    
    # Check if we can fast-forward a head
    if not enchained: 
        heads = [Head.from_file(fname) for fname in os.listdir(DIR_HEADS)]
        for head in heads:
            if block.prev_hash == head.ref_hash:
                head.fast_forward(block)
                enchained = True
                break
    # Finally, make a new head
    if not enchained:
        new = Head().generate(block)
    
    clean()

def is_enchained(block_hash):
    heads = [Head.from_file(fname) for fname in os.listdir(DIR_HEADS)]
    for head in heads:
        curr = fc.Block.from_file(head.ref_hash)
        while curr is not None and curr.height is not 0:
            if block.compute_hash() == block_hash:
                return True
            curr = Block.from_file(curr.prev_hash)
    return False

def clean():
    heads = [Head.from_file(fname) for fname in os.listdir(DIR_HEADS)]
    # Remove dead heads
    bad_heads = []
    for head in heads:
        curr = fc.Block.from_file(head.ref_hash)
        while curr is not None and curr.height is not 0:
            for trial_head in heads:
                if curr.prev_hash == trial_head.ref_hash:
                    bad_heads.append(trial_head)
            curr = Block.from_file(curr.prev_hash)
    for head in bad_heads:
        heads.remove(head)
        head.delete()
    
    # Update chained status
    for head in heads:
        head.recompute_chained()
    
    # Remove invalid blocks
    for head in [head for head in heads if head.chained]:
        curr = fc.Block.from_file(head.ref_hash)
        while True:
            if not block.is_chain_valid():
                block.blacklist()
                block.delete()
            if block.height == 0:
                break
            else
                curr = Block.from_file(curr.prev_hash)
    
    # Update chained status
    for head in heads:
        head.recompute_chained()
    
    # Remove stale heads
    grand_height = max(head.height for head in heads)
    bad_heads = []
    for head in heads:
        if (grand_height - head.height) >= 6:
            bad_heads.append(head)
    for head in bad_heads:
        heads.remove(head)
        head.delete()
    
    # Delete unreferenced blocks
    blocklist = os.listdir(DIR_BLOCKS)
    for head in heads:
        blocklist.remove(head.ref_hash)
        curr = fc.Block.from_file(head.ref_hash)
        while curr is not None and curr.height is not 0:
            blocklist.remove(curr.prev_hash)
            curr = fc.Block.from_file(curr.prev_hash)
    for block_hash in blocklist:
        fc.Block.from_file(block_hash).delete()
    
def get_highest_chained_block():
    return Block.from_file(get_highest_chained_hash())

def get_highest_chained_hash():
    heads = [Head.from_file(fname) for fname in os.listdir(DIR_HEADS)]
    return max(heads, key=attrgetter('height')).ref_hash

def compute_next_target(block):
    if self.height < CHAIN_RECALC_INTERVAL:
        return self.target
    elif (self.height % CHAIN_RECALC_INTERVAL) is 0:
        historic = n_blocks_ago(block, CHAIN_RECALC_INTERVAL)

def n_blocks_ago(block, n):
    curr = block
    dest = block.height - n
    while curr.height is not dest:
        curr = Block.load(block.prev_hash)
        if curr is None:
            break
    return curr
    while
