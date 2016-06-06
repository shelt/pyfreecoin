#!/usr/bin/env python
from time import time

import freecoin as fc
from binascii import hexlify
from freecoin import net


class Miner:
    def __init__(self, network):
        self.network = network
    
    def slow_mine(self, addr):
        while True:
            fc.logger.verbose("Miner: starting new workblock")
            workblock = fc.Block.generate_workblock(addr)
            target_num = fc.chain.target_to_num(workblock.target)
            success = False
            while not success:
                if fc.chain.get_highest_hash(chained_only=True) != workblock.prev_hash:
                    break
                for hash,tx in self.network.mempool.items():
                    if tx not in workblock.txs and tx.is_chain_valid_wrt(workblock):
                        workblock.txs.append(tx) #TODO if we receive txs with surpluses, increase our reward ie use block.calculate_surplus()
                workblock.recompute_merkle_root()
                period = int(time())
                while True:
                    if int(time()) - period >= 5:
                        break
                    workblock.nonce += 1
                    hash = workblock.compute_hash()
                    if int.from_bytes(hash, byteorder='big') <= target_num:
                        fc.logger.info("Block found! [%s]" % hexlify(hash).decode())
                        fc.chain.enchain(workblock)
                        for peer in self.network.peers:
                            peer.send_inv(fc.net.DTYPE_BLOCK,[hash])
                        success = True
                        break