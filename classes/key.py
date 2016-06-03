#!/usr/bin/env python
import os
import ecdsa as ec
import hashlib as hl

import freecoin as fc
from freecoin.keys import *
from freecoin.util.hashlib import b58_encode

class Key:
    def __init__(self, secret=None):
        if secret:
            self.secret = secret
        else:
            self.secret = ec.SigningKey.generate(curve=ec.SECP256k1)
        self.public = self.secret.get_verifying_key()
        self.addr = compute_address(public.to_string())
    
    def to_file(self):
        os.makedirs(fc.DIR_KEYS, exist_ok=True)
        with open(os.path.join(fc.DIR_KEYS, self.addr), 'w') as f:
            f.write(self.secret.to_pem().decode())
    
    @staticmethod
    def from_file(addr):
        secret = ec.SigningKey.generate()
        os.makedirs(fc.DIR_KEYS, exist_ok=True)
        try:
            with open(os.path.join(fc.DIR_KEYS, addr)) as f:
                secret.from_pem(f.read())
            return Key(secret=secret)
        except FileNotFoundError:
            return None
