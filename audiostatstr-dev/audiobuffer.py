import io
from ts_attrconst import StreamType

def ac3scan(stream, fd, tag):
    
    buffer = io.FileIO(fd, "rb")
    buffer = io.BufferedRandom(fd, 4096)

    sync = buffer.ReadBytes(2)
    if ((not sync) or (sync[0] != 0x0B) or (sync[1] != 0x77)):    
        return
    
    sr_code = 0
    frame_size = 0
    frame_size_code = 0
    channel_mode = 0
    lfe_on = 0
    dial_norm = 0
    num_blocks = 0

    hdr = buffer.peek(4)
    bsid = (hdr[3] & 0xF8) >> 3
    if (bsid <= 10)
    
        crc = buffer.ReadBytes(2)
        sr_code = buffer.ReadBits(2)
        frame_size_code = buffer.ReadBits(6)
        bsid = buffer.ReadBits(5)
        bsmod = buffer.ReadBits(3)

        channel_mode = buffer.ReadBits(3)
        cmixlev = 0
        if (((channel_mode & 0x1) > 0) and (channel_mode != 0x1))
        
            cmixlev = buffer.ReadBits(2)
        
        surmixlev = 0
        if ((channel_mode & 0x4) > 0)
        
            surmixlev = buffer.ReadBits(2)
        
        dsurmod = 0
        if (channel_mode == 0x2)
        
            dsurmod = buffer.ReadBits(2)
            if (dsurmod == 0x2)
            
                stream.audiomode = StreamType.AudioMode.Surround
            
        
        lfe_on = buffer.ReadBits(1)
        dial_norm = buffer.ReadBits(5)
        compr = 0
        if (1 == buffer.ReadBits(1))
        
            compr = buffer.ReadBits(8)
        
        langcod = 0
        if (1 == buffer.ReadBits(1))
        
            langcod = buffer.ReadBits(8)
        
        mixlevel = 0
        roomtyp = 0
        if (1 == buffer.ReadBits(1))
        
            mixlevel = buffer.ReadBits(5)
            roomtyp = buffer.ReadBits(2)
        
        if (channel_mode == 0)
        
            dialnorm2 = buffer.ReadBits(5)
            compr2 = 0
            if (1 == buffer.ReadBits(1))
            
                compr2 = buffer.ReadBits(8)
            
            langcod2 = 0
            if (1 == buffer.ReadBits(1))
            
                langcod2 = buffer.ReadBits(8)
            
            mixlevel2 = 0
            roomtyp2 = 0
            if (1 == buffer.ReadBits(1))
            
                mixlevel2 = buffer.ReadBits(5)
                roomtyp2 = buffer.ReadBits(2)
            
        
        copyrightb = buffer.ReadBits(1)
        origbs = buffer.ReadBits(1)
        if (bsid == 6)
        
            if (1 == buffer.ReadBits(1))
            
                dmixmod = buffer.ReadBits(2)
                ltrtcmixlev = buffer.ReadBits(3)
                ltrtsurmixlev = buffer.ReadBits(3)
                lorocmixlev = buffer.ReadBits(3)
                lorosurmixlev = buffer.ReadBits(3)
            
            if (1 == buffer.ReadBits(1))
            
                dsurexmod = buffer.ReadBits(2)
                dheadphonmod = buffer.ReadBits(2)
                if (dheadphonmod == 0x2)
                
                    # UnFinished
                
                adconvtyp = buffer.ReadBits(1)
                xbsi2 = buffer.ReadBits(8)
                encinfo = buffer.ReadBits(1)
                if (dsurexmod == 2)
                
                    stream.audiomode = StreamType.AudioMode.Extended
                
    else
    
        frame_type = buffer.ReadBits(2)
        substreamid = buffer.ReadBits(3)
        frame_size = (buffer.ReadBits(11) + 1) << 1

        sr_code = buffer.ReadBits(2)
        if (sr_code == 3)
        
            sr_code = buffer.ReadBits(2)
        
        else
        
            num_blocks = buffer.ReadBits(2)
        
        channel_mode = buffer.ReadBits(3)
        lfe_on = buffer.ReadBits(1)
    

    if (channel_mode == 0) 
        stream.channelcount = 2
        if (stream.audiomode == StreamType.AudioMode.Unknown) 
            stream.audiomode = StreamType.AudioMode.DualMono
    elif (channel_mode == 1) 
        stream.channelcount = 1
    elif (channel_mode == 2) 
        stream.channelcount = 2
        if (stream.audiomode == StreamType.AudioMode.Unknown) 
            stream.audiomode = StreamType.AudioMode.Stereo
        
    elif (channel_mode == 3) 
        stream.channelcount = 3
    elif (channel_mode == 4) 
        stream.channelcount = 3
    elif (channel_mode == 5) 
        stream.channelcount = 4
    elif (channel_mode == 6) 
        stream.channelcount = 4
    elif (channel_mode == 7) 
        stream.channelcount = 5
    else 
        stream.channelcount = 0
    
    
# Remove Due To Being Redundant
    if (sr_code == 0) 
        stream.SampleRate = 48000
    elif (sr_code == 1) 
        stream.SampleRate = 44100
    elif (sr_code == 2) 
        stream.SampleRate = 32000
    else 
        stream.SampleRate = 0
    

    if (bsid <= 10)
    
        if (frame_size_code >> 1 == 18) 
            stream.bitrate = 640000
        elif (frame_size_code >> 1 == 17) 
            stream.bitrate = 576000
        elif (frame_size_code >> 1 == 16) 
            stream.bitrate = 512000
        elif (frame_size_code >> 1 == 15) 
            stream.bitrate = 448000
        elif (frame_size_code >> 1 == 14) 
            stream.bitrate = 384000
        elif (frame_size_code >> 1 == 13) 
            stream.bitrate = 320000
        elif (frame_size_code >> 1 == 12) 
            stream.bitrate = 256000
        elif (frame_size_code >> 1 == 11) 
            stream.bitrate = 224000
        elif (frame_size_code >> 1 == 10) 
            stream.bitrate = 192000
        elif (frame_size_code >> 1 == 9) 
            stream.bitrate = 160000
        elif (frame_size_code >> 1 == 8) 
            stream.bitrate = 128000
        elif (frame_size_code >> 1 == 7) 
            stream.bitrate = 112000
        elif (frame_size_code >> 1 == 6) 
            stream.bitrate = 96000
        elif (frame_size_code >> 1 == 5) 
            stream.bitrate = 80000
        elif (frame_size_code >> 1 == 4) 
            stream.bitrate = 64000
        elif (frame_size_code >> 1 == 3) 
            stream.bitrate = 56000
        elif (frame_size_code >> 1 == 2) 
            stream.bitrate = 48000
        elif (frame_size_code >> 1 == 1) 
            stream.bitrate = 40000
        elif (frame_size_code >> 1 == 0) 
            stream.bitrate = 32000
        else 
            stream.bitrate = 0
        
    
    else
    
        stream.bitrate = (4.0 * frame_size * stream.SampleRate / (num_blocks * 256))
    

    stream.lfe = lfe_on
    if (stream.StreamType != StreamType.AC3_PLUS_AUDIO and stream.StreamType != StreamType.AC3_PLUS_SECONDARY_AUDIO)
    
        stream.dialnorm = dial_norm - 31
    
    stream.isVBR = False
    stream.isInitialized = True


