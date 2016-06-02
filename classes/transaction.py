#!/usr/bin/env python
import os
from hashlib import sha256

import freecoin as fc

SIZE_TX_HEADER = 10
SIZE_TX_INPUT  = 130
SIZE_TX_OUTPUT = 37

class Tx(fc.classes.Hashable):
    def __init__(self, lock_time=0, ins=[], outs=[]):
        self.version   = fc._VERSION_
        self.lock_time = lock_time
        self.ins       = ins
        self.outs      = outs
    
    @staticmethod
    def generate_coinbase(addr, lock_time=0):
        #todo
        
        
    @staticmethod
    def from_file(tx=None, block=None, index=None):
        # Only specify (tx) or (block and index)
        
        if (tx != None and (block == None and index == None)):
            # Get by transaction hash
            for fname in os.listdir(DIR_TXINDEX):
                with open(os.path.join(DIR_TXINDEX,fname), 'rb') as f:
                    bytes  = f.read()
                    hashes = [bytes[i:i+32] for i in range(0, len(bytes), 32)]
                    for i,hash in enumerate(hashes):
                        if hash == tx:
                            return from_file(block=fname, index=i)
        
        elif (tx == None and (block != None and index != None)):
            # Get by position within a block
            block = Block.from_file(block)
            return lock.txs[i]
        else:
            raise AssertionError("Only specify (tx) or (block and index)")
    
    @staticmethod
    def from_bytes(bytes):
        tx = Tx()
        tx.version   = int.from_bytes(bytes[0:2]  , byteorder='big')
        in_count     = int.from_bytes(bytes[2:4]  , byteorder='big')
        out_count    = int.from_bytes(bytes[4:6]  , byteorder='big')
        tx.lock_time = int.from_bytes(bytes[6:10] , byteorder='big')
        ins_bytes  = bytes[10:10+SIZE_TX_INPUT*in_count]
        outs_bytes = bytes[10+SIZE_TX_INPUT*in_count:SIZE_TX_OUTPUT*out_count]
        for in_bytes in fc.util.divide(ins_bytes, SIZE_TX_INPUT):
            tx.ins.append(TxInput.from_bytes(in_bytes))
        for out_bytes in fc.util.divide(outs_bytes, SIZE_TX_OUTPUT):
            tx.outs.append(TxOutput.from_bytes(out_bytes))
        return tx
    
    def to_bytes(self):
        bytes = b""
        bytes +=  self.version.to_bytes(2, byteorder='big')
        bytes +=  len(self.ins).to_bytes(2, byteorder='big')
        bytes +=  len(self.outs).to_bytes(2, byteorder='big')
        bytes +=     self.lock_time.to_bytes(4, byteorder='big')
        
        for input in self.ins:
            bytes += input.to_bytes()
        for output in self.outs:
            bytes += output.to_bytes()
        
        return bytes
    
    def compute_raw_size(self):
        return SIZE_TX_HEADER + (SIZE_TX_INPUT*len(self.ins)) + (SIZE_TX_OUTPUT*len(self.outs))
    
    def is_chain_valid_wrt(self, block):
        pass #TODO

class TxInput:
    def __init__(self):
        self.out_index = None
        self.ref_tx    = None
        self.pubkey    = None
        self.sig       = None
    
    @staticmethod
    def generate(index, ref_tx_hash, key):
        input = TxInput()
        input.out_index   = index
        input.ref_tx_hash = ref_tx_hash
        input.pubkey      = key.public.to_string()
        input.sig = key.secret.sign(Tx.from_file(tx=ref_tx_hash).txs[index].get_signable_hash())
        return input
    
    @staticmethod
    def from_bytes(bytes):
        input = TxInput()
        input.out_index = int.from_bytes(bytes[0:2], byteorder='big')
        input.ref_tx = bytes[2:34]
        input.pubkey = bytes[34:82]
        input.sig    = bytes[82:130]
        return input
    
    def to_bytes(self):
        bytes = b""
        bytes += self.out_index.to_bytes(2, byteorder='big')
        bytes += self.ref_tx
        bytes += self.pubkey
        bytes += self.sig
        return bytes

class TxOutput:
    def __init__(self):
        self.out_addr = None
        self.amount   = None
    
    @staticmethod
    def generate(out_addr, amount):
        if type(out_addr) == str:
            out_addr = out_addr.encode("ascii")
        output = TxOutput()
        output.out_addr = out_addr
        output.amount   = amount
        return output
    
    @staticmethod
    def from_bytes(bytes):
        output = TxOutput()
        output.out_addr = bytes[0:33]
        output.amount = int.from_bytes(bytes[33:37], byteorder='big')
        return output
    
    def to_bytes(self):
        bytes = b""
        bytes += self.out_addr
        bytes += self.amount.to_bytes(4, byteorder='big')
        return bytes