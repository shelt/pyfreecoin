import os,sys
from time import time
import shutil

import freecoin as fc

# Hash of the only legitimate genesis block 
ONE_TRUE_ROOT  = b'\x00\x00\x00\x1b\xb2\x90\xcf;\xb2\x04G\x91]\xfa\xe8Ep\xfe\x97\xf2U\xed\x82fc\xc9\xa1t<J,\x07'
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
    block.target      = b"\xff\xff\xff\x1a"
    block.nonce       = 34513722
    block.tx_count    = 1
    tx = fc.Tx(lock_time=0)
    tx.outs.append(fc.TxOutput.generate("2rF5NCyatob3WuuAqJ7od3oqwASU3jAjt", 1))
    block.txs         = [tx]
    block.recompute_merkle_root()
    
    target = fc.chain.target_to_num(block.target)
    hash = block.compute_hash()
    if int.from_bytes(hash, byteorder='big') > target or hash != ONE_TRUE_ROOT:
        fc.logger.info("Genesis block is not configured. Please wait while a valid nonce is found...")
        while int.from_bytes(block.compute_hash(), byteorder='big') > target:
            block.nonce += 1
        fc.logger.info("Found valid nonce. Please update the following source literals before continuing:")
        fc.logger.info("Nonce        : %d" % block.nonce)
        fc.logger.info("ONE_TRUE_ROOT: %s" % block.compute_hash())
        sys.exit()
    else:
        fc.chain.enchain(block)