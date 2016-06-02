#!/usr/bin/env python
from time import time

from freecoin import net


class Miner:
    def __init__(self, network):
        self.network = network
    
    def slow_mine(self, key):
        while True:
            workblock = Block.generate_workblock()
            target = chain.compute_next_target(workblock)
            success = False
            while not success:
                if get_highest_chained_hash() != workblock.prev_hash:
                    break
                for hash,tx in self.network.mempool.items():
                    if tx not in workblock.txs and tx.is_chain_valid_wrt(workblock):
                        workblock.txs.append(tx)
                workblock.recompute_merkle_root()
                period = time()
                while True:
                    if time() - period >= 5:
                        break
                    block.nonce += 1
                    hash = block.compute_hash()
                    if int.from_bytes(hash, byteorder='big') <= target:
                        block.save()
                        for peer in self.network.peers:
                            peer.send_inv([hash])
                        break
                        success = True
