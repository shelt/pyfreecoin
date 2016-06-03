import os,sys
from time import time
import shutil

import freecoin as fc

# This is a hash of the verifying key of the admin_key
ONE_TRUE_ROOT  = b'\x19+\x10\x1e\x13\x1c\xbf+\xe3\xe7?\xe7A\xe5\x90\x8a\xe7\xc3\xfdp\xa3kaT\x11h\xab0L\xca\xdc\xaf'
ROOT_PREV_HASH = b"\x0b\x97|2\xd5\xfax\xfc\xde\x13\x11;\x19d\xa3\xb3{\xbfu\xe9\xac\xcb+\xb4V\xaa\x0c\xe8\xbfM\x83\xac"

def init_blockchain():
    if len(os.listdir(fc.DIR_HEADS)) > 0:
        rsp = fc.util.query("Blockchain is not headless! Delete existing chain data? (key data will be preserved)", default='no')
        if not rsp:
           sys.exit(1)
        else:
            for dir in [fc.DIR_BLOCKS, fc.DIR_TXINDEX, fc.DIR_HEADS]:
                shutil.rmtree(dir, ignore_errors=True)
            fc.init()
    block = fc.Block()
    block.version     = fc._VERSION_
    block.time        = 1464860000
    block.height      = 0
    block.prev_hash   = ROOT_PREV_HASH
    block.target      = b"\x01\x20"
    block.nonce       = 0
    block.tx_count    = 1
    tx = fc.Tx(lock_time=0)
    tx.outs.append(fc.TxOutput.generate("2rF5NCyatob3WuuAqJ7od3oqwASU3jAjt", 1))
    block.txs         = [tx]
    block.recompute_merkle_root()
    
    hash = block.compute_hash()
    if hash != ONE_TRUE_ROOT:
        fc.logger.error("Invalid ONE_TRUE_ROOT! Expected:", hash)
        sys.exit()
    
    fc.chain.enchain(block)