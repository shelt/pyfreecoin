import hashlib as hl
from freecoin.util.hashlib import b58_encode

def compute_address(pubkey_bytes):
    a = hl.sha256(pubkey_bytes).digest()
    b = hl.sha256(a).digest()
    c = hl.sha1(b).digest()
    return b58_encode(int.from_bytes(c + (hl.sha1(c).digest())[:4], byteorder='big'))