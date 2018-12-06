#!/bin/python3

import io

class BufferWithSkipBit(io.BufferedRandom):

    def __init__(self, *args):
        super().__init__(*args)
        self.skipbits = 0


    def readbits(self, bits):

        pos = self.tell()

        shift = 24
        data = 0
        for i in range(0,4):
        
            if (pos + i >= 4096): #verify it's proper buffer length as this may not be apropos
                break
            data += int(float((self.read(1))) << shift)			# Why do I cast to float and int here? Lol Damn i havent looked at this code in a while
            shift -= 8
        

        vector =  [data[i//8] & 1 << i%8 != 0 for i in range(len(data) * 8)]                # https://stackoverflow.com/a/36149471/8661716 
        print("This is the vector data {} and this is the vector {}.".format(data, vector)) # 

        value = 0
        i = self.skipbits
        while i < (self.skipbits + bits):
        
            value <<= 1
            if (vector[1 << (32 - i - 1)]):													# presumes 32bits
                value += 1
            else:
                value += 0        
            i += 1

        self.skipbits += bits
        self.seek(pos + (skipbits >> 3), 0)
        skipbits = skipbits % 8

        return value




# This should be ab le to at least pull audio statistics without using a different module. Do note that Im not implemennting a PT Parser. Needed for TSCodecAC3, TSCodecDTS, TSCodecDTSHD, TSCodecTrueHD in the audiobuffer.py section.
