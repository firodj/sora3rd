#MASTER data.lst update tool. Works for all Falcom PSP games!
#Tagline: All Falcom games. All files. One tool.
#v2 - Add UMDgen file list update
#v1.1 Fix regarding root directory data.lst file
#v1 - Initial version

#How to use
#1) Create your "production folder" with a dump from UMDgen (or other tool) with all
#   game files
#2) Modify files as needed
#3) Drop exported filelist from UMDgen with filename 'filelist.txt'
#4) Drop this tool into the USRDIR folder and run
#5) Insert modified data.lst with UMDgen and other files, import new file list, and test!

#Non-basic uses
#You can run the script into interactive mode from the command prompt:
#Python -i script.py
#Or run from IDLE
#If you do this, after the program is finished running:
#Type updatelist to see a list of the filenames whose sizes were updated
#Type missingfiles to see a list of missing files
#Type LBAfiles to see a list of files that required LBA expansion

#Limitations
#1) Can't modify LBAs for EBOOT.BIN

import os
import struct

dirname = 'Updated'        #Directory into which the updated data.lst goes
UTF8 = 'utf-8'
srcdatalst = 'disc/PSP_GAME/USRDIR/data.lst'
usrdir = 'disc/PSP_GAME/USRDIR/'
filelisttxt = 'original/filelist.txt'

def get_data(filename):     #Gets data
    totalbytes = os.path.getsize(filename)
    infile = open(filename, 'rb')
    totalfiledata = infile.read(totalbytes)
    infile.close()
    return totalfiledata

def ensure_dir(directory):  #Check if directory exists and create if necessary
    if not os.path.exists(directory):
        os.mkdir(directory)

def replacestr(origstr,replacestr,startpos,replacelen):
    '''Returns a string with a replaced sub-string'''
#origstr - the original string, replacestr = the string to replace
#startpos - where the replacement string should go
#replacelen - how many characters of the original string to replace
    return origstr[:startpos] + replacestr + origstr[startpos+replacelen:]


#Initialize extension dictionary
#Extension table is found in data.lst at the beginning
#Any number of extensions up to 3 characters long separated by nulls
ExtDict = {0: ""}
with open(srcdatalst,'rb') as f:
    size = struct.unpack('<I',f.read(4))[0]
    print('data.lst size=%d' % (size,))
    i = 1
    while True:
        ext = f.read(4)
        if ext == b'\x00'*4:
            break
        ExtDict[i] = ext.split(b'\x00')[0].decode(UTF8)
        i += 1

#My try at object-oriented programming
class DataListLine:
    def __init__(self, f, pos):         #Reads a 'data line' from data.lst
        self.Addr = pos
        origpos = f.tell()
        f.seek(pos)                     #Move to start of line
        self.Name = f.read(8).split(b'\x00')[0].decode(UTF8) #Get the name, null end string
        self.Size = struct.unpack('<I',f.read(4))[0]    #Get the file size
        self.LBA = struct.unpack('<I',f.read(3) + b'\x00')[0]    #Get the LBA
        self.ExtByte = int.from_bytes(f.read(1), byteorder='big')    #Get the extension byte
        self.IsFolder = False           #Folders have 00 as their ext. byte
        if self.ExtByte == 0:
            self.IsFolder = True
        self.Ext = '.' + ExtDict[self.ExtByte]  #Get the ext. name from the dictionary
        self.FileName = self.Name + self.Ext    #The filename is name + ext
        f.seek(origpos)
    def binary(self):                   #Converts object data back into a line for data.lst
        name = self.Name.encode(UTF8)
        return name + b'\x00'*(8-len(name)) + \
               struct.pack('<I',self.Size) + \
               struct.pack('<I',self.LBA)[:3] + \
               (self.ExtByte).to_bytes(1, byteorder='big')
    def __repr__(self):
        return 'DataListLine(0x%x %s %d)' % (self.LBA, self.PathName, self.Size)

class FileListLine:                     #For files in the UMD but not present in data.lst
    def __init__(self, LBA, PathName):
        self.LBA = LBA
        self.PathName = PathName
        try:
            self.Size = os.path.getsize(PathName)
        except:
            self.Size = 0
    def __repr__(self):
        return 'FileListLine(0x%x, %s)' % (self.LBA, self.PathName,)

#Wow, so many variables
pos = 0x410         #A magic number. The first line in data.lst.
updates = 0         #Keep track of # of updates to data.lst sizes
updatelist = []     #Keep track of filenames whose size was updated
#Names and counts is a little more complicated
#When the program gets to a folder entry, it pushes the name of the folder onto
#the name stack (to capture path name information) and pushes the number of
#files + folders in that folder (incl. subfolders) onto the counts stack.
#Each time the program processes a line, it subtracts 1 from each number on the
#counts stack. After this, new values are pushed onto the stack if the current
#line is a folder.
#If the last entry on the counts stack is 0, then that counts entry and the
#corresponding name are popped off of each stack.
#I hope that made some sense
names = []
counts = []
lines = []          #For storage of line data for writing a new file later
missingfiles = []   #Keep track of files that couldn't be updated because they
                    #are missing
with open(srcdatalst,'rb') as f:
    datalstbase = f.read(0x410)                 #For making a new file later
    while pos < os.path.getsize(srcdatalst):    #Main loop
        line = DataListLine(f, pos)             #Initialize line data
        pos += 0x10                             #Increment position counter
        #Has to be done in this order-
        #Update counts, process line, pop counts (if applicable)
        #Folder counts include subfolders, and exclude the line itself is on
        for i, count in enumerate(counts):      #Subtract one from each count
            counts[i] -= 1                      #on the counts stack
        if line.IsFolder:                       #If current entry is a folder
            counts.append(line.Size)            #push new values to the count
            names.append(line.Name)             #and name stacks
        else:                                   #Current entry is a file
            if len(names) > 0:                  #Form the file path
                line.PathName = os.sep.join(names) + os.sep
            else:
                line.PathName = ''
            line.PathName += line.FileName
            ##print(line.PathName, line.Size, hex(line.LBA))  #Uncomment for printing
#os.path.getsize can fail if the file doesn't exist (WindowsError in that case)
            try:
                fileSize = os.path.getsize(usrdir+line.PathName)
                if fileSize != line.Size:  #Update required
                    updates += 1                            #Increment counter
                    updatelist.append(line.PathName)        #Add to list of updated entries
                    line.Size = fileSize   #Update object with new size
            except:                            #File doesn't exist
                missingfiles.append(line.PathName)          #Update list of missing files
        #Has to be done in this order
        while len(counts) != 0:     #As long as the counts stack isn't empty
            if counts[-1] != 0:     #and the last entry isn't zero, pop off the
                break               #last count and name entries
            if counts[-1] == 0:
                del names[-1]
                del counts[-1]
        lines.append(line)

#Updating LBAs portion of the program
if os.path.isfile(filelisttxt):  #Original file list
    #Sort "file lines" (not folder lines) by LBA
    filelines = sorted([l for l in lines if l.IsFolder == False], key= lambda x: x.LBA)
    #Read original filelist file
    filelistheader = []                 #Read header from file list
    filelistother = []
    flag = True                         #For marking the header
    pathlist = [x.PathName for x in filelines]
    filelistlines = []                  #Container for file list line objects
    with open(filelisttxt) as f:
        for line in f:
            lba, pathname = [x.strip() for x in line.rstrip().split(',')]
            if pathname[:17] == '\\PSP_GAME\\USRDIR\\':  #Determine if line is in data.lst or not
                #If the line is not in data.lst, create FileListLine object for it
                if pathname[17:] not in pathlist:    #Removes '\PSP_GAME\USRDIR\' text
                    filelistlines.append(FileListLine(int(lba), pathname[17:]))
            else:
                filelistheader.append(FileListLine(int(lba), pathname[1:])) #Add line to header

    #Integrate and sort lines by LBA
    filelines = sorted(filelines + filelistlines, key= lambda x: x.LBA)
    firstpass = True
    LBAfiles = []   #List of files that needed updated LBAs
    LBAcount = 0    #Count of files that needed updated LBAs
    for i in range(len(filelines)):     #Loop and...
        if firstpass:                   #From the 2nd pass onward...
            firstpass = False
        else:
            avail_blocks = (filelines[i].LBA - filelines[i-1].LBA)    #Blocks available based on LBAs
            blocks_needed = filelines[i-1].Size / 2048
            required_blocks = int(blocks_needed)
            if not blocks_needed.is_integer():
                required_blocks += 1                                    #Blocks needed based on file size
            if required_blocks > avail_blocks:                          #Insufficient blocks
                LBAcount += 1                                           #Increment counter
                LBAfiles.append(filelines[i-1].PathName)                #Add name of file needing LBAs
                #User messages
                print('Insufficient LBAs at position {}, {}.'.format(hex(filelines[i-1].Addr),filelines[i-1].FileName))
                print('LBA: {}, Required blocks {}, available blocks {}.'.format(filelines[i-1].LBA, required_blocks, avail_blocks))
                raise RuntimeError
                for j, l in enumerate(filelines):   #Update LBAs for current file and everything after it
                    if j >= i:
                        l.LBA += (required_blocks - avail_blocks) * 0x10
    ##        In case you want to know about files that have too many LBAs
    ##        elif required_blocks < avail_blocks:
    ##            print 'Extra LBAs at position {}, {}.'.format(hex(filelines[i-1].Addr),filelines[i-1].FileName)
    ##            print 'Required blocks {}, available blocks {}.'.format(required_blocks, avail_blocks)

    ensure_dir(dirname)                 #Create directory if it doesn't exist
    with open(dirname + os.sep + 'filelist.txt','w') as f: #Open new file list file for writing
        #Write the header
        for line in filelistheader:
            f.write('{:0>7d}'.format(line.LBA))     #The LBA, zero-padded to 7 digits
            f.write(' , \\')                          #Separator
            f.write(line.PathName + '\n')           #Path and file name
        #File lines (not folder lines) sorted by LBA
        i=0
        for line in sorted([l for l in lines if l.IsFolder == False] + filelistlines, key= lambda x: x.LBA):
            if i > 0:
                f.write('\n')
            f.write('{:0>7d}'.format(line.LBA))     #The LBA, zero-padded to 7 digits
            f.write(' , \\PSP_GAME\\USRDIR\\')      #Separator
            f.write(line.PathName) #Path and file name
            i += 1
    print('Updated {} entries in data.lst for additional LBAs.'.format(LBAcount))

    with open(dirname + os.sep + '.ppsspp-index.lst','w') as f: #Open new file list file for writing
        allfiles = [(l.LBA, 'PSP_GAME/USRDIR/' + l.PathName.replace('\\', '/')) for l in ([l for l in lines if l.IsFolder == False] + filelistlines)]
        allfiles += [(l.LBA, l.PathName.replace('\\', '/')) for l in filelistheader]
        allfiles = sorted(allfiles , key= lambda l: l[1])
        for l in allfiles:
            f.write('0x{:0>8x}'.format(l[0]))     #The LBA, zero-padded to 7 digits
            f.write(' ' + l[1] + '\n')           #Path and file name

else:
    print('filelist.txt not found in %s. LBAs not updated.' % (filelisttxt,))

ensure_dir(dirname)                 #Create directory if it doesn't exist
with open(dirname + os.sep + 'data.lst','wb') as f:
    f.write(datalstbase)            #Write first 0x410 of file
    for line in lines:              #Write data for each line
        f.write(line.binary())
#User messages
print('Updated {} entries in data.lst for file size.'.format(updates))
print("There were {} missing files that couldn't be updated.".format(len(missingfiles)))
print(missingfiles)