import struct
from ChunkReader import readChunk
# File read and write operations. Init with an infile name.
class FileRW:

    file = None
    out = bytearray()
    lookbackStringEncountered = False
    readNodes = dict()
    skippedSizePos = -1

    def __init__(self, filename):
        self.file = open(filename, "rb")
        

    # Reads next data. Stops at 0x0A0D aka \r\n
    def readNextData(self) -> bytearray:
        a = bytearray()
        finished = False
        while not finished:
            a.extend(self.file.read(1))
            if (int.from_bytes(a[-2:], 'little') == 0x0A0D): #\r\n but i wanna use hex
                return a[:-2]
    
    # Reads next string. Same as readNextData but decodes the result for convenience.
    def readNextString(self) -> str:
        return self.readNextData().decode()
    
    # Writes data to the out bytes.
    def write(self, bIn:bytearray):
        self.out += bIn
    
    def rw(self, n:int):
        self.out += self.file.read(n)

    def Int16(self) -> int:
        i16 = int(self.readNextString())
        self.out += i16.to_bytes(2, 'little')
        return i16
    
    def Int32(self) -> int:
        i32 = int(self.readNextString())
        self.out += i32.to_bytes(4, 'little')
        return i32
    
    def Int64(self) -> int:
        i64 = int(self.readNextString())
        self.out += i64.to_bytes(8, 'little')
        return i64

    def Bool(self) -> bool :
        b = bool(self.readNextString())
        self.out += int(b).to_bytes(4, "little")
        return b

    def Float(self) -> float:
        f = float(self.readNextString())
        self.out += bytearray(struct.pack('f', f))
        return f
    
    def String(self):
        s = self.readNextString()
        self.out += len(s).to_bytes(4, "little")
        self.out += s.encode()

    def Iso4(self):
        for _ in range(12):
            self.Float()
        
    def Byte(self) -> int:
        b = int("0x0"+self.readNextString(),0)
        self.out += b.to_bytes(1, 'little')
        return b
    
    def Int2(self):
        raise NotImplementedError()
    
    def Int3(self):
        raise NotImplementedError()
    
    def Rect(self):
        raise NotImplementedError()
    
    def Box(self):
        raise NotImplementedError()
    
    def FileTime(self):
        raise NotImplementedError()
    
    def Mat3(self):
        raise NotImplementedError()
    
    def LookBackString(self):
        if not self.lookbackStringEncountered:
            self.Int32()
            self.lookbackStringEncountered = True
        lbIndex = self.readNextString()
        if (lbIndex == "4294967295" or lbIndex.lower() == "ffffffff"):
            lbIndex = "4294967295"
            self.out += int(lbIndex).to_bytes(4, 'little')
            return
        if (lbIndex != "40000000"):
            raise NotImplementedError("TODO : Implement lookbackstring")
        self.out += int("0x"+lbIndex,0).to_bytes(4, 'little')
        self.String()

    def Node(self):
        nodeNum = self.Int32()
        if (nodeNum == 4294967295):
            return 
        if (nodeNum in self.readNodes.keys()):
            return #I don't know how this works
        start = len(self.out)-1
        id = self.readNextString()
        self.out += int("0x0"+id,0).to_bytes(4, 'little')
        l = self.readNextString()
        while not readChunk(l, self): 
            l = self.readNextString()

        self.readNodes[nodeNum] = self.out[start:]
    
    def Folder(self):
        self.String()
        numSubFolders = self.Int32()
        for _ in range(numSubFolders):
            self.Folder()


    def Skippable(self):
        if (self.skippedSizePos != -1): raise LookupError("Skippable called but EndSkippable wasn't")
        skip = self.Int32()
        if (skip != 1397442896): raise ValueError("Chunk is not actually skippable!") # 1397442896 = SKIP
        self.skippedSizePos = len(self.out)
        self.Int32()

    def EndSkippable(self):
        if (self.skippedSizePos ==- 1): raise LookupError("EndSkippable called but Skippable wasn't")
        self.out[self.skippedSizePos:self.skippedSizePos+4] = (len(self.out)-self.skippedSizePos).to_bytes(4, "little")
        self.skippedSizePos = -1

    def toFile(self, filename):
        with open(filename, "wb") as outFile:
            outFile.write(self.out)