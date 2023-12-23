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
if (int.from_bytes(version, byteorder='little')!=6): print("WARNING : Version != 6. This file might have unsupported content.")
rw.write(version)

# Type check
fType = rw.file.read(4)
if (fType.decode()[0]!="T"): raise ValueError("Only Text files are supported.")
if (fType.decode()[1]!="U"): raise ValueError("Compressed headers are not supported.")
if (fType.decode()[2]!="U"): raise ValueError("Compressed body is not supported.")
rw.write("BUUR".encode())

# GBX's class id
mainId = rw.readNextString()
rw.write(int("0x0"+mainId,0).to_bytes(4, 'little'))

# UserDataSize
userDataSize = rw.Int32()
if (userDataSize!=0): raise ValueError("UserDataSize > 0, header chunks are not supported yet. Please open an issue.")

# NumNodes
rw.Int32()

# NumExternalNodes
externalNodes = rw.Int32()
if (externalNodes > 0): raise ValueError("External nodes are not supported yet. Please open an issue.")

c = rw.readNextString()
while (not readChunk(c, rw)):
    c = rw.readNextString()

rw.toFile("B_"+os.path.basename(filepath))