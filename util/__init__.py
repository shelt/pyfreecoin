import os

# Divide l into groups of g
def divide(l, g):
    return [l[i:i+g] for i in range(0, len(l), g)]