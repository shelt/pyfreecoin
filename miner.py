#!/usr/bin/env python

from freecoin import net


class Miner:
    def __init__(self, network):
        self.network = network
    
    def mine(self, key):
        
