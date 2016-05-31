import os

if os.name is 'nt':
    DIR_STORAGE = os.path.join(os.getenv('APPDATA'), "freecoin/")
else:
    DIR_STORAGE = os.path.join(os.getenv('HOME'), ".freecoin/")
