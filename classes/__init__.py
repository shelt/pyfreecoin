
from hashlib import sha256

class Serializable:
    def compute_hash(self):
        return sha256(self.to_bytes()).digest()
    
    def compute_size(self):
        return len(self.to_bytes())