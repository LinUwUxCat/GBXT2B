import struct
from ChunkReader import readChunk
# File read and write operations. Init with an infile name.
class FileRW:

    file = None
    version=6
    out = bytearray()
    lookbackStringVersion = -1
    readNodes = dict()
    skippedSizePos = []

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

    #useful for some quirks
    def setVersion(self, ver:int):
        self.version = ver

    #Convenience methods
        
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
        for _ in range(9): self.Float()
    
    #############################
    # LookBackString reference
    # v2:
    #   int32 version
    #   if version != 4294967295 (0xFFFFFFFF)
    #       int32 index
    #       string string
    #
    # v3:
    #   int32 version (only the first time encountering a LookBackString)
    #   int32 index
    #   if bits 0-29 of index are 0
    #       string string
    #
    # Note that most of the time everything is decimal but sometimes stuff is stored as hex without 0x prefix for some reason so i double check shit
    #############################
    def LookBackString(self):

        if self.lookbackStringVersion < 3: #version check. Entered only the first time on lbstring v3 and everytime on v2 to check for empty strings
            possibleVersion = self.readNextString()
            if (possibleVersion == "4294967295" or possibleVersion.lower() == "ffffffff"): 
                self.out += (4294967295).to_bytes(4, 'little')
                return
            else: 
                self.lookbackStringVersion = int(possibleVersion)
                self.out += int(possibleVersion).to_bytes(4, 'little')
        
        lbIndex = self.readNextString()
        if (lbIndex=="4294967295" or lbIndex.lower() == "ffffffff"): #for convenience, if string is empty just yeet out. This part specifically seems to be inconsistent with hex or dec
            lbIndex = "4294967295"
            self.out += int(lbIndex).to_bytes(4, 'little')
            return
        
        intIndex=int(lbIndex) 
        if (self.lookbackStringVersion == 3): intIndex=int("0x"+lbIndex, 16) # ???? unsure of this
        self.out += intIndex.to_bytes(4, 'little')

        if (self.lookbackStringVersion == 2): self.String()
        elif (self.lookbackStringVersion == 3):
            if (intIndex & 0x3fffffff == 0): self.String()

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
    
    def DataAndBool(self):
        raw = self.readNextData() #Explanation here : These chunks do not have any \r\n after the data so i have to extract the bool manually since True and 
        b = raw[-4:].decode()
        if (b=="True"):
            self.write(raw[:-4])
            self.write(int(bool(b)).to_bytes(4, "little"))
        else:
            self.write(raw[:-5])
            self.write(int(bool(raw[-5:].decode())).to_bytes(4, "little"))

    def DataAndInt(self):
        raw = self.readNextData()
        self.write(raw[:-1])
        addedInt=int(raw[-1:].decode())
        if (addedInt>9): raise NotImplementedError("I hate nadeo (pls open an issue ty)")
        self.write(addedInt.to_bytes(4, "little"))

    def Skippable(self):
        print("[Skippable] ", end="")
        skip = self.Int32()
        if (skip != 1397442896): raise ValueError("Chunk is not actually skippable!") # 1397442896 = SKIP
        self.skippedSizePos.append(len(self.out))
        self.Int32() # dummy chunk size

    def EndSkippable(self):
        if (len(self.skippedSizePos) == 0): raise LookupError("EndSkippable called but Skippable wasn't")
        skippedPos = self.skippedSizePos.pop()
        self.out[skippedPos:skippedPos+4] = (len(self.out)-skippedPos - 4).to_bytes(4, "little") # -4 because i get the position before writing the dummy chunk size

    def toFile(self, filename):
        with open(filename, "wb") as outFile:
            outFile.write(self.out)