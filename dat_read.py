import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from struct import unpack
from collections import namedtuple
from tools.falcom_decompress_v2 import decompress_FALCOM2, decompress_FALCOM3
import os

datfile = 'disc/PSP_GAME/USRDIR/data_3rd/start.dat'

f_dat = open(datfile, 'rb')

d =  unpack('<IIII', f_dat.read(0x10))
fileCount = d[0]

Item = namedtuple('Item', 'name offset compressed size unk')

for i in range(fileCount):
  item = Item._make(unpack('<16sIIII', f_dat.read(0x20)))

  name = item.name.split(b'\0')[0]
  print(name, item)

  oldpos = f_dat.tell()

  f_dat.seek(item.offset)
  comp = f_dat.read(item.compressed)

  if item.size > 0:
    output = decompress_FALCOM3(comp)
    print("decompress", len(output))
  else:
    print("uncompress")

  f_dat.seek(oldpos)


f_dat.close()