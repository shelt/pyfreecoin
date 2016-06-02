import os
from time import time
import freecoin as fc

# This is a hash of the verifying key of the admin_key
ROOT_PREV_HASH = b"\x0b\x97|2\xd5\xfax\xfc\xde\x13\x11;\x19d\xa3\xb3{\xbfu\xe9\xac\xcb+\xb4V\xaa\x0c\xe8\xbfM\x83\xac"

def init_blockchain():
    if len(os.listdir(fc.DIR_HEADS)) > 0:
        fc.logger.error("Failed to initialize blockchain: blockchain is not headless!")
        return
    block = fc.Block()
    block.version     = fc._VERSION_
    block.time        = int(time())
    block.height      = 0
    block.prev_hash   = ROOT_PREV_HASH
    block.target      = b"\xff\x80"
    block.nonce       = 0
    block.tx_count    = 1
    block.txs         = [fc.Tx(lock_time=0, ins=[], outs=[fc.TxOutput.generate("2rF5NCyatob3WuuAqJ7od3oqwASU3jAjt", 1)])]
    block.recompute_merkle_root()
    
    fc.chain.enchain(block)