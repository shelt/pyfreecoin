import os,sys
from time import time
import shutil

import freecoin as fc

# Hash of the only legitimate genesis block 
ONE_TRUE_ROOT  = b',\xecr> \xf9\xee\xc2\x04|\xe5\xc8c\x91\xbe\x87\xfa\xe5%\xe0\xbe_&\xdf\x92\xa3\xac\xa0\x94\xca\xc0+'
# A hash of the verifying key of the admin_key
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
    block.target      = b"\x00\x20"
    block.nonce       = 0
    block.tx_count    = 1
    tx = fc.Tx(lock_time=0)
    tx.outs.append(fc.TxOutput.generate("2rF5NCyatob3WuuAqJ7od3oqwASU3jAjt", 1))
    block.txs         = [tx]
    block.recompute_merkle_root()
    
    hash = block.compute_hash()
    if hash != ONE_TRUE_ROOT:
        fc.logger.error("Please set ONE_TRUE_ROOT literal to the following before calling init_blockchain(): %s" % hash)
        sys.exit()
    
    fc.chain.enchain(block)