#!/usr/bin/env python
import ecdsa as ec
import hashlib as hl

from freecoin.util.hashlib import b58_encode

DIR_KEY

class Key:
    # Constructor with no kwargs will generate new key
    def __init__(self, addr=None):
        if addr is None:
            self.seckey = ec.SigningKey.generate(curve=ec.SECP256k1)
        
        self.pubkey = self.sk.get_verifying_key()
        self.addr = self._compute_address()
        
        if addr is None:
            self._save()
        
    def _compute_address(self):
        a = hl.sha256(self.pubkey.to_string()).digest()
        b = hl.sha256(a).digest()
        c = hl.sha1(b).digest()
        return b58_encode(int.from_bytes(c + hl.sha1(c).digest()[:4], byteorder='big'))
    
    def _save(self):
        

def _save_key(seckey):
    
def _compute_address(pubkey):
