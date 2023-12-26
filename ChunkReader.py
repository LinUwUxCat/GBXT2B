import FileRW 

# reads a chunk. Returns true if the current node is over (FACADE01 found), else false.
def readChunk(chunkId:str,rw) -> bool:

    rw.write(int("0x0"+chunkId,0).to_bytes(4, 'little'))
    print("\nReading chunk " + chunkId.upper()+ " ", end="")
    match chunkId.upper():
        # CPlugSolid
        case "9005000":
            rw.Int32()
        case "9005006":
            for _ in range(6): rw.Float()
            rw.Mat3()
        case "9005007":
            rw.Bool()
        case "900500A":
            rw.Bool()
            rw.Bool()
            rw.Int32()
            rw.Bool()
            rw.Bool()
            rw.Node()
        case "900500B":
            for i in range(6): rw.Bool()
            rw.Int32()
        case "900500C":
            for i in range(10): rw.Bool()
            rw.Float()
            rw.Int32()
            for i in range(4): rw.Float()
            rw.Int32()
            rw.Int32()
        case "900500D":
            rw.Bool()
            rw.Bool()
            rw.Node()
        case "900500E":
            for i in range(4): rw.Float()
            rw.Iso4()
        case "900500F":
            rw.Float()
            rw.Float()
        case "9005010":
            rw.Node()
        case "9005011":
            rw.Bool()
            U02 = rw.Bool()
            if (U02): rw.Bool()
            rw.Node() # only if U02 is False?
        case "9005012":
            rw.Byte()
        case "9005017":
            ver = rw.Int32()
            if (ver>=3):
                U09 = rw.Bool()
                if (U09):
                    pass # ??
            else :
                rw.Byte()
                rw.Float()
                rw.Bool()
                rw.Rect()
                rw.Rect()
                rw.Int2()
                if (int(ver)>=1): rw.Box()
            if (int(ver)>=2): rw.FileTime()


        # CPlugTree
        case "904F006":
            rw.Int32()
            listSize = rw.Int32()
            for _ in range(listSize):
                rw.Node()
        case "904F00C":
            rw.Int32()
        case "904F00D":
            rw.LookBackString()
            rw.LookBackString()
        case "904F00E":
            rw.Node()
            rw.Node()
            rw.Node()
        case "904F010":
            rw.rw(4) #? ok
        case "904F011":
            rw.Node()
        case "904F016":
            for _ in range(4): rw.Node()
        case "904F017":
            rw.Node()
        case "904F019":
            rw.rw(4) # Nando forgot to put the int32 as text ig? idk
            rw.Iso4()


        # CPlugVisual
        case "9006001":
            rw.LookBackString()
        case "9006003":
            rw.Bool()
            rw.Bool()
            rw.Int32()
            rw.Int32()
            rw.Int32()
            rw.DataAndBool()
            rw.Int32()
        case "9006004":
            rw.Node()
        case "9006005":
            listSize = rw.Int32()
            for _ in range(int(listSize)): rw.Int3()
        case "9006006":
            rw.Bool()
        case "9006007":
            rw.Bool()
        case "9006009":
            rw.Float()
        case "9006008" | "900600A":
            rw.Bool()
            rw.Bool()
            rw.Int32()
            rw.Int32()
            rw.Int32()
            rw.Int32()#ARRAY - but always empty?
            rw.Int32()#^^^^^^^^^^^^^^^^^^^^^^^^^
            rw.DataAndBool()
            rw.Int32()#Array but always empty ?
        case "900600B":
            siz = rw.Int32()
            if (siz != 0): raise NotImplementedError("None of this shit is supported")
        

        #CPlugVisual3D
        case "902C001":
            rw.DataAndInt()
        case "902C002":
            rw.Node()
        case "902C003": #Note : This is the same as 9006008|A with the boolean after the data except here it's an int32. If this is ever >9 i have no idea how to handle it and it's always been 0 in my files anyways
            rw.DataAndInt()
            rw.Int32()


        #CPlugVisualIndexed
        case "906A000":
            lS = rw.Int32()
            for _ in range(lS): rw.rw(2)
        case "906A001":
            bo = rw.Bool()
            if (bo):
                chunkId = rw.readNextString() # This is more a node than a chunk but it's not really a node cuz it doesn't have a number? idfk anymore...
                readChunk(chunkId, rw) #this should always be 09057000
                rw.write(int("0x0"+rw.readNextString(),0).to_bytes(4, 'little')) #facade01


        #CPlugIndexBuffer
        case "9057000":
            rw.rw(4)
            ls = rw.Int32()
            for _ in range(ls):
                rw.rw(2)


        #CPlugShader
        case "9002005":
            rw.rw(8) # unsure what this is
        case "9002007":
            rw.Node() # This seems to use the ref table, so with my implementation of node this is probably incorrect
            l = rw.Int32()
            for _ in range(l):
                rw.Node()
            rw.Node()
        case "900200E":
            rw.Node()
            a1s = rw.Int32()
            for _ in range(int(a1s)): rw.Node()
            rw.Node()
            a2s = rw.Int32()
            for _ in range(int(a2s)): rw.Node()
        case "9002014":
            rw.rw(8)
            rw.Float()
            rw.Node()
            rw.Int16()

        
        #CPlugShaderGeneric
        case "9004001":
            rw.rw(22*4) #Supposed to be an array of 22 floats but they're already binary so
        case "9004003":
            rw.rw(22*4) #I love double implementations
        

        #CPlugShaderApply
        case "9026000": #????
            rw.Int32()
            rw.Int32()
            rw.Int32()
        case "9063002":
            rw.rw(4)
            rw.Int32()
            for i in range(5): rw.Int32() # fixed array size

        
        #CPlugShaderPass
        case "9067002": # This is most definitely incorrect but this chunk is not documented nor implemented anywhere
            rw.Int32()
            rw.Int32()
            rw.Int32()
            rw.Int32()
            rw.Node()
            rw.Int32()

        #CSystemConfig
        case "B005008":
            rw.Skippable()
            rw.String()
            rw.EndSkippable()
        case "B005009":
            rw.Skippable()
            for _ in range(6): rw.String()
            rw.EndSkippable()
        case "B00500B":
            rw.Skippable()
            for _ in range(4): rw.Int32() # Guessing 
            rw.EndSkippable()
        case "B005012":
            rw.Skippable()
            for _ in range(3): rw.String()
            rw.Bool()
            rw.Int32()
            rw.EndSkippable()
        case "B00501D":
            rw.Skippable()
            rw.Bool()
            rw.Bool()
            rw.EndSkippable()
        case "B005020":
            rw.Skippable()
            rw.Bool()
            while not readChunk(rw.readNextString(), rw): #Headless node
                pass
            rw.EndSkippable()
        case "B005022":
            rw.Skippable()
            rw.Float()
            rw.Float()
            rw.Bool()
            rw.Bool()
            rw.EndSkippable()
        case "B005028":
            rw.Skippable()
            rw.Bool()
            rw.Float()
            rw.Float()
            for _ in range (3): rw.Int32()
            rw.Bool()
            rw.Bool()
            rw.Int32()
            rw.EndSkippable()
        case "B00502B":
            rw.Skippable()
            rw.Int32()
            rw.Bool()
            rw.Float()
            rw.EndSkippable()
        case "B005030":
            rw.Skippable()
            rw.Bool()
            rw.Bool()
            rw.Int32()
            for _ in range(4): rw.Bool()
            rw.String()
            rw.String()
            rw.Bool()
            rw.EndSkippable()
        case "B005034":
            rw.Skippable()
            for _ in range(5): rw.Int32()
            rw.Bool()
            rw.Int32()
            rw.EndSkippable()
        case "B005035":
            rw.Skippable()
            rw.Bool()
            rw.Bool()
            rw.EndSkippable()
        case "B005036":
            rw.Skippable()
            rw.Bool()
            rw.String()
            rw.String()
            for _ in range(4): rw.Int32()
            rw.Bool()
            rw.String()
            rw.Int32()
            rw.Bool()
            rw.EndSkippable()

        #CSystemConfigDisplay
        case "B013001":
            rw.Skippable()
            for _ in range(6): rw.Int32()
            rw.Bool()
            rw.Bool()
            rw.EndSkippable()
        case "B013003":
            rw.Skippable()
            rw.Bool()
            rw.Int32()
            rw.Bool()
            rw.Int32()
            rw.Bool()
            rw.Bool()
            rw.EndSkippable()
        case "B013004":
            rw.Skippable()
            rw.Bool()
            rw.EndSkippable()
        case "B013005":
            rw.Skippable()
            rw.Bool()
            rw.EndSkippable()
        case "B013008":
            rw.Skippable()
            for _ in range(3): rw.Int32()
            rw.EndSkippable()
        case "B013009":
            rw.Skippable()
            rw.Int32()
            rw.Int32()
            rw.Bool()
            rw.Bool()
            rw.EndSkippable()
        case "B01300A":
            rw.Skippable()
            rw.Bool()
            rw.Bool()
            rw.EndSkippable()
        case "B01300B":
            rw.Skippable()
            rw.Bool()
            rw.Float()
            rw.EndSkippable()
        case "B01300D":
            rw.Skippable()
            rw.Int32()
            rw.Bool()
            for _ in range(6): rw.Int32()
            rw.EndSkippable()
        case "B01300E":
            rw.Skippable()
            rw.Bool()
            rw.EndSkippable()
        case "B01300F":
            rw.Skippable()
            rw.Bool()
            rw.EndSkippable()
        case "B013010":
            rw.Skippable()
            rw.Float()
            rw.EndSkippable()


        #CPlugBitmap
        case "9011007":
            rw.Node()
            rw.Int32()
            c = rw.Bool()
            rw.Int32()
            rw.Int32()
            for _ in range(8): rw.Bool()
            rw.Int32()
            rw.Int32()
            if not c:
                rw.Int32()
                rw.Bool()
                rw.Int32()
                rw.Bool()
                rw.Mat3() #
                rw.Mat3() # Might be iso4

        #CPlugSurface
        case "900C000":
            rw.LookBackString()
        

        #CPlugSurfaceGeom
        case "900F001":
            rw.Int32()
            for _ in range(6): rw.Float()


        #Fallbacks
        case "FACADE01":
            return True
        
        case _:
            raise NotImplementedError("Chunk " + chunkId.upper() + " is not implemented. Please open an issue.")

    return False