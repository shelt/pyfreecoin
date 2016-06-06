#!/usr/bin/env python
import os
from operator import attrgetter
from binascii import hexlify,unhexlify

import freecoin as fc

# TODO move to classes/
class Head(fc.classes.Serializable):
    def __init__(self):
        height   = None
        ref_hash = None
        chained  = None
    
    @staticmethod
    def point(block):
        fc.logger.verbose("Creating new head at [%s]" % hexlify(block.compute_hash()).decode())
        head = Head()
        head.height = block.height
        head.ref_hash = block.compute_hash()
        head.chained = False # chain should always be cleaned after this
        head.to_file()
        return head
    
    def to_file(self):
        os.makedirs(fc.DIR_HEADS, exist_ok=True)
        with open(os.path.join(fc.DIR_HEADS,hexlify(self.ref_hash).decode()), 'wb') as f:
            f.write(self.to_bytes())

    def delete_file(self):
        os.remove(os.path.join(fc.DIR_HEADS,hexlify(self.ref_hash).decode()))
    
    @staticmethod
    def from_file(hash):
        if type(hash) is str:
            fname = os.path.join(fc.DIR_HEADS,hash)
        else:
            fname = os.path.join(fc.DIR_HEADS,hexlify(hash).decode())
        try:
            with open(fname,'rb') as f:
                return Head.from_bytes(f.read())
        except FileNotFoundError:
            return None
    
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
        self.delete_file()
        fc.logger.verbose("Fast forwarding head [%s]->[%s]" %
            (hexlify(self.ref_hash).decode(), hexlify(block.compute_hash()).decode()))
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
            curr = fc.Block.from_file(curr.prev_hash)
        
        self.chained = retval
        self.to_file()
        return retval
    
    def get_lowest_parent_hash(self):
        curr = fc.Block.from_file(self.ref_hash)
        last = curr
        while curr is not None:
            if curr.height == 0:
                return None
            last = curr
            curr = fc.Block.from_file(curr.prev_hash)
        
        return last.compute_hash()
        
        
#todo make method
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
        new = Head.point(block)
    
    clean()

def is_enchained(block_hash):
    heads = [Head.from_file(fname) for fname in os.listdir(fc.DIR_HEADS)]
    for head in heads:
        curr = fc.Block.from_file(head.ref_hash)
        while curr is not None and curr.height != 0:
            if curr.compute_hash() == block_hash:
                return True
            curr = fc.Block.from_file(curr.prev_hash)
    return False

def clean():
    heads = [Head.from_file(fname) for fname in os.listdir(fc.DIR_HEADS)]
    # Remove dead heads
    bad_heads = []
    for head in heads:
        curr = fc.Block.from_file(head.ref_hash)
        while curr is not None and curr.height != 0:
            for trial_head in heads:
                if curr.prev_hash == trial_head.ref_hash:
                    fc.logger.verbose("Removing dead head [%s]" % hexlify(head.ref_hash).decode())
                    trial_head.delete_file()
            curr = fc.Block.from_file(curr.prev_hash)
    
    heads = [Head.from_file(fname) for fname in os.listdir(fc.DIR_HEADS)]
    # Update chained status
    for head in heads:
        head.recompute_chained()
    
    heads = [Head.from_file(fname) for fname in os.listdir(fc.DIR_HEADS)]
    # Remove invalid blocks
    for head in [head for head in heads if head.chained]:
        curr = fc.Block.from_file(head.ref_hash)
        while True:
            if not curr.is_chain_valid():
                #curr.blacklist() TODO
                fc.logger.verbose("Removing invalid block [%s]" % hexlify(curr.compute_hash()).decode())
                fc.logger.verbose("Rewinding head [%s]->[%s]" % (hexlify(head.ref_hash).decode(), hexlify(curr.prev_hash).decode()))
                curr.delete_file() #TODO rewind method instead of just calling point()
                head.delete_file()
                Head.point(fc.Block.from_file(curr.prev_hash))
            if curr.height == 0:
                break
            else:
                curr = fc.Block.from_file(curr.prev_hash)
    
    heads = [Head.from_file(fname) for fname in os.listdir(fc.DIR_HEADS)]
    # Update chained status
    for head in heads:
        head.recompute_chained()
    
    heads = [Head.from_file(fname) for fname in os.listdir(fc.DIR_HEADS)]
    # Remove stale heads
    
    chained_heights = [head.height for head in heads if head.chained]
    if len(chained_heights) > 0:
        grand_height = max(chained_heights)
        bad_heads = []
        for head in heads:
            if (grand_height - head.height) >= 6:
                fc.logger.verbose("Removing stale head [%s]" % hexlify(head.ref_hash).decode())
                head.delete_file()
    
    heads = [Head.from_file(fname) for fname in os.listdir(fc.DIR_HEADS)]
    blocklist = [unhexlify(hash) for hash in os.listdir(fc.DIR_BLOCKS)]
    # Delete unreferenced blocks
    for head in heads:
        blocklist.remove(head.ref_hash)
        curr = fc.Block.from_file(head.ref_hash)
        while curr is not None and curr.height != 0:
            try:
                blocklist.remove(curr.prev_hash)
            except ValueError:
                pass
            curr = fc.Block.from_file(curr.prev_hash)
    for block_hash in blocklist:
        fc.logger.verbose("Removing unreferenced block [%s]" % hexlify(block_hash).decode())
        fc.Block.from_file(block_hash).delete_file()
    
def get_highest_block(chained_only=False):
    hash = get_highest_hash(chained_only=chained_only)
    if hash is None:
        return None
    else:
        return fc.Block.from_file(hash)

def get_highest_hash(chained_only=False):
    head = get_highest_head(chained_only=chained_only)
    if head is None:
        return None
    return head.ref_hash

def get_highest_head(chained_only=False):
    heads = [Head.from_file(fname) for fname in os.listdir(fc.DIR_HEADS)]
    if chained_only:
        heads = [head for head in heads if head.chained]
    if len(heads) == 0:
        return None
    return max(heads, key=attrgetter('height'))

#todo make method
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
    while curr.height != dest:
        curr = Block.load(block.prev_hash)
        if curr is None:
            break
    return curr

def target_to_num(t):
    return (t[0] << (8*(t[3]+2))) | (t[1] << (8*(t[3]+1))) | (t[2] << (8*t[3]))

def num_to_target(num):
    blen = math.ceil(num.bit_length()/8)
    b0 = num >> 8*(blen-1)
    b1 = num >> 8*(blen-2) & 0xff
    b2 = num >> 8*(blen-3) & 0xff
    return bytes([b0,b1,b2,blen-2])
