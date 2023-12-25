from FileRW import FileRW
from ChunkReader import readChunk
import sys
import os

filepath = sys.argv[1]
rw = FileRW(filepath)

# GBX check
magic = rw.file.read(3) 
if (magic.decode()!="GBX"): raise ValueError("Not a GBX file!")
rw.write(magic)

# Version check
version = rw.file.read(2)
rw.write(version)
rw.setVersion(int.from_bytes(version, "little"))

# Type check
fType = rw.file.read(4) if (int.from_bytes(version, byteorder='little') >= 4) else rw.file.read(3)
if (fType.decode()[0]!="T"): raise ValueError("Only Text files are supported.")
if (fType.decode()[1]!="U"): raise ValueError("Compressed headers are not supported.")
if (fType.decode()[2]!="U"): raise ValueError("Compressed body is not supported.")
sFType = list(fType.decode())
sFType[0]="B"
fType=''.join(sFType).encode()
rw.write(fType)

# GBX's class id
mainId = rw.readNextString()
rw.write(int("0x0"+mainId,0).to_bytes(4, 'little'))

# UserDataSize
if (int.from_bytes(version, byteorder='little') >= 6):
    userDataSize = rw.Int32()
    if (userDataSize!=0): raise ValueError("UserDataSize > 0, header chunks are not supported yet. Please open an issue.")

# NumNodes
rw.Int32()

# NumExternalNodes
externalNodes = rw.Int32()
if (externalNodes > 0): 
    rw.Int32() # ancestorLevel
    numSubFolders = rw.Int32()
    for _ in range(numSubFolders):
        rw.Folder()
    for _ in range(externalNodes):
        flags = rw.Int32()
        if (flags & 4 == 0):
            rw.String()
        else:
            rw.Int32()
        rw.Int32()
        if (flags & 4 == 0): rw.Int32()

c = rw.readNextString()
while (not readChunk(c, rw)):
    c = rw.readNextString()

print("\nDone!")
rw.toFile((os.path.dirname(filepath)+os.path.sep if os.path.dirname(filepath)!="" else "") +"B_"+os.path.basename(filepath))