import os, sys
sys.path.append(os.path.dirname(os.getcwd()))

from pyrubymarshal import Marshal
from pyrubymarshal.rgss import RGSS_PARSERS

m = Marshal()
m.register_user_parsers(RGSS_PARSERS)
with open(input("File location? "), "rb") as f:
    res = m.unmarshal(f.read())

print("Done parsing.")
res.pprint()
# d:\steam\steamapps\common\oneshot\data\Map014.rxdata
