#!/usr/bin/env python
import os
import ecdsa as ec
import hashlib as hl

from freecoin.util import DIR_STORAGE
from freecoin.util.hashlib import b58_encode

DIR_KEYS = os.path.join(DIR_STORAGE, "private/")

class Key:
    # Constructor with no kwargs will generate new key
    def __init__(self):
        self.secret = None
        self.public = None
        self.addr   = None

    def generate(self):
        self.secret = ec.SigningKey.generate(curve=ec.SECP256k1)
        self.public = self.secret.get_verifying_key()
        self.addr = self._compute_address()
        self.save()
        return self
    
    def save(self):
        os.makedirs(DIR_KEYS, exist_ok=True)
        with open(os.path.join(DIR_KEYS, self.addr), 'w') as f:
            f.write(self.public.to_pem().decode())
    
    def load(self, addr):
        retval = ec.SigningKey()
        os.makedirs(DIR_KEYS, exist_ok=True)
        with open(os.path.join(DIR_KEYS, addr)) as f:
            return retval.from_pem(f.read())
        return self

    def _compute_address(self):
        a = hl.sha256(self.public.to_string()).digest()
        b = hl.sha256(a).digest()
        c = hl.sha1(b).digest()
        return b58_encode(int.from_bytes(c + (hl.sha1(c).digest())[:4], byteorder='big'))
