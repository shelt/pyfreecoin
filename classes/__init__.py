
from hashlib import sha256

class Hashable:
    def compute_hash(self):
        return sha256(self.to_bytes()).digest()