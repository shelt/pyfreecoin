#!/usr/bin/env python

DIR_HEADS = os.path.join(DIR_STORAGE, "heads/")

class Node:
    def __init__(self):
        height   = None
        chained  = False
        ref_hash = None
    
    def generate(self, block):
        self.height = block.height
        self.chained = False # chain should always be cleaned after this
        self.ref_hash = block.compute_hash()
    
    def save(self):
        os.makedirs(DIR_HEADS, exist_ok=True)
        with open(os.path.join(DIR_HEADS,self.compute_hash()), 'wb') as f:f
            f.write(self.serialize())
    
    def load(self, hash):
    
    def deserialize(self, bytes):
        
    
    def serialize(self):
        
    
    def fast_forward(self, block):
        

def enchain(block):
    # Ensure the block isn't already enchained
    block_hash = block.compute_hash()
    enchained = is_enchained(block_hash):
    
    # Check if we can fast-forward a head
    if not enchained:
        for fname in os.listdir(DIR_HEADS):
            node = Node().load(fname)
            if block.prev_hash == node.ref_hash:
                node.fast_forward(block)
                enchained = True
    # Finally, make a new head
    if not enchained:
        new = Node().generate(block)
        new.save()
    
    chain_clean()

def is_enchained(block_hash):
    for fname in os.listdir(DIR_HEADS):
        curr_hash = Node.load(fname).ref_hash
        while chain.block_exists(curr_hash):
            curr = fc.Block().load(curr_hash)
            if curr.height is 0:
                break
            if curr_hash == block_hash:
                return True
            curr_hash = curr.prev_hash
    return False
