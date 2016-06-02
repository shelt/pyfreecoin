#!/usr/bin/env python
import os
from operator import attrgetter
from binascii import hexlify,unhexlify

import freecoin as fc

# TODO move to classes/
class Head(fc.classes.Hashable):
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
        os.makedirs(fc.DIR_HEADS, exist_ok=True)
        with open(os.path.join(fc.DIR_HEADS,hexlify(self.compute_hash()).decode()), 'wb') as f:
            f.write(self.to_bytes())
    
    @staticmethod
    def from_file(hash):
        if type(hash) is str:
            fname = os.path.join(fc.DIR_HEADS,hash)
        else:
            fname = os.path.join(fc.DIR_HEADS,hexlify(hash).decode())
        with open(fname,'rb') as f:
            return Head.from_bytes(f.read())
    
    @staticmethod
    def from_bytes(bytes):
        head = Head()
        head.height   = int.from_bytes(bytes[0:4],  byteorder='big')
        head.ref_hash = bytes[4:36]
        head.chained  = bool(int.from_bytes(bytes[36:37], byteorder='big'))
        return head
    
    def to_bytes(self):
        bytes = b""
        bytes += self.height.to_bytes(4, byteorder='big')
        bytes += self.ref_hash
        bytes += int(self.chained).to_bytes(1, byteorder='big')
        return bytes
    
    def fast_forward(self, block):
        assert block.prev_hash == self.ref_hash
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
    block.to_file()
    # Ensure the block isn't already enchained
    if is_enchained(block.compute_hash()):
        return
    
    # Check if we can fast-forward a head
    enchained = False
    heads = [Head.from_file(fname) for fname in os.listdir(fc.DIR_HEADS)]
    for head in heads:
        if block.prev_hash == head.ref_hash:
            head.fast_forward(block)
            enchained = True
            break
    # If all else failed, make a new head
    if not enchained:
        new = Head().point_to(block)
    
    clean()

def is_enchained(block_hash):
    heads = [Head.from_file(fname) for fname in os.listdir(fc.DIR_HEADS)]
    for head in heads:
        curr = fc.Block.from_file(head.ref_hash)
        while curr is not None and curr.height is not 0:
            if block.compute_hash() == block_hash:
                return True
            curr = Block.from_file(curr.prev_hash)
    return False

def clean():
    heads = [Head.from_file(fname) for fname in os.listdir(fc.DIR_HEADS)]
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
            else:
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
    blocklist = [unhexlify(hash) for hash in os.listdir(fc.DIR_BLOCKS)]
    for head in heads:
        blocklist.remove(head.ref_hash)
        curr = fc.Block.from_file(head.ref_hash)
        while curr is not None and curr.height is not 0:
            blocklist.remove(curr.prev_hash)
            curr = fc.Block.from_file(curr.prev_hash)
    for block_hash in blocklist:
        fc.Block.from_file(block_hash).delete()
    
def get_highest_chained_block():
    hash = get_highest_chained_hash()
    if hash is None:
        return None
    else:
        return fc.Block.from_file(hash)

def get_highest_chained_hash():
    heads = [Head.from_file(fname) for fname in os.listdir(fc.DIR_HEADS)]
    if len(heads) == 0:
        fc.logger.error("Failed to retrieve the highest chain hash because no heads exist! Please call network.update()!")
        return None
    return max(heads, key=attrgetter('height')).ref_hash

def compute_next_target(block):
    if block.height < fc.net.CHAIN_RECALC_INTERVAL or \
       (block.height % fc.net.CHAIN_RECALC_INTERVAL) != 0:
        return block.target
    else:
        historic = n_blocks_ago(block, fc.net.CHAIN_RECALC_INTERVAL)
        
        diff = block.time - historic.time
        
        # Upper bound (4x)
        if (diff > SECONDS_IN_8_WEEKS):
            diff = SECONDS_IN_8_WEEKS
        elif (diff < SECONDS_IN_HALF_WEEK):
            diff = SECONDS_IN_HALF_WEEK
        
        return num_to_target((diff * target_to_num(block.target)) / 2)

def n_blocks_ago(block, n):
    curr = block
    dest = block.height - n
    while curr.height is not dest:
        curr = Block.load(block.prev_hash)
        if curr is None:
            break
    return curr

def target_to_num(t):
    return t[0] << 8*t[1]

def num_to_target(num):
    b1 = int(num.bit_length()/8 - 1)
    b0 = num >> 8*b1
    return bytes([b0,b1])