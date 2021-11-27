from struct import unpack
from collections import namedtuple
import os

UTF8 = 'utf-8'

basedir = 'disc/PSP_GAME/USRDIR/'
srcdatalst = os.path.join(basedir, 'data.lst')

# Open file
f_lst = open(srcdatalst, 'rb')

fileSize = unpack('<I', f_lst.read(4))[0]

print(fileSize)

#Initialize extension dictionary
#Extension table is found in data.lst at the beginning
#Any number of extensions up to 3 characters long separated by nulls

ExtDict = {0: ""}
extBlank = b'\x00' * 4

for i in range(1, 256):
	ext = f_lst.read(4)
	#if ext == extBlank: break
	ExtDict[i] = ext.split(b'\x00')[0].decode(UTF8)

dataCount = unpack('<IIII', f_lst.read(0x10))[2]

print(dataCount)

print(f_lst.tell())

paths = []

for i in range(dataCount):
	DataListLine = namedtuple('DataListLine', 'name size lbaext')

	datalistline = DataListLine._make(unpack('<8sII', f_lst.read(0x10)))
	name = datalistline.name.split(b'\x00')[0].decode(UTF8)
	ext = datalistline.lbaext >> 24
	lba = datalistline.lbaext & 0xffffff
	is_folder = False
	is_exists = False

	if len(paths) > 0:
		for j in range(len(paths)):
			paths[j]['size'] -= 1

	if ext == 0:
		is_folder = True
		paths.append({'name': name, 'size': datalistline.size})
	else:
		name += "." + ExtDict[ext]

		if len(paths) > 0:
			names = map(lambda e: e['name'], paths)
			name = os.path.join(*names) + os.path.sep + name

			while len(paths) > 0:
				if paths[-1]['size'] != 0:
					break
				paths.pop()

		fullname = os.path.join(basedir, name)
		is_exists = os.path.exists(fullname)

	print(i, name, is_folder, datalistline.size, lba, is_exists)

print(paths)
print(f_lst.tell(), fileSize)
f_lst.close()
