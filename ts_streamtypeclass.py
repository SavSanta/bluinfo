from iso_639_2map import codecnamefunc, altcodecfunc, isolangfunc
from ts_attrconst import StreamType, VideoFormat, FrameRate, ChannelLayout, SampleRate, AspectRate, AudioMode

class Stream(object):
    def __init__(self):
        self.PID = None
        self.streamtype = None
        self.descriptors = None
        self.bitrate = 0
        self.activebitrate = 0
        self.isVBR = False
        self.isInitialized = False
        self.languagename = "Unknown"                 
        self.isHidden = False
        self.isAudio = False
        self.isVideo = False
        self.isGraphic = False
        self.isText = False
        self.payloadbytes = 0
        self.packetcount = 0
        self.packetseconds = 0
        self.angleindex = 0
        self.packetsize = 0

              
class TSVideoStream(Stream):
           
    def __init__(self):
       super().__init__()
       self.width = "--UNKNOWN--"
       self.height = "--UKNOWN--"
       self.isInterlaced = "--UNKNOWN--"
       self.frame_rate_enumerator = "--UNKNOWN--"
       self.frame_rate_denominator = "--UNKNOWN--"
       self.aspectratio = "--UNKNOWN--"
       self.encoding_profile = "--UNKNOWN--"
       self.videoformat = "--UNKNOWN--"
       self.framerate = "--UNKNOWN--"
       self.isVideo = True

    def convertvidformat(self):
        
        if (self.videoformat == VideoFormat.VIDEOFORMAT_480i):
            self.height = 480
            self.isInterlaced = True
        elif (self.videoformat == VideoFormat.VIDEOFORMAT_480p):
            self.height = 480
            self.isInterlaced = False
        elif (self.videoformat == VideoFormat.VIDEOFORMAT_576i):
            self.height = 576
            self.isInterlaced = True
        elif (self.videoformat == VideoFormat.VIDEOFORMAT_576p):
            self.height = 576
            self.isInterlaced = False
        elif (self.videoformat == VideoFormat.VIDEOFORMAT_720p):
            self.height = 720
            self.isInterlaced = False
        elif (self.videoformat == VideoFormat.VIDEOFORMAT_1080i):
            self.height = 1080
            self.isInterlaced = True
        elif (self.videoformat == VideoFormat.VIDEOFORMAT_1080p):
            self.height = 1080
            self.isInterlaced = False
        elif (self.videoformat == VideoFormat.VIDEOFORMAT_2160p):
            self.height = 2160
            self.isInterlaced = False


    def convertframerate(self):
                
        if (self.framerate == FrameRate.FRAMERATE_23_976): 
            self.frame_rate_enumerator = 24000
            self.frame_rate_denominator = 1001
        elif (self.framerate == FrameRate.FRAMERATE_24): 
            self.frame_rate_enumerator = 24000
            self.frame_rate_denominator = 1000
        elif (self.framerate == FrameRate.FRAMERATE_25): 
            self.frame_rate_enumerator = 25000
            self.frame_rate_denominator = 1000
        elif (self.framerate == FrameRate.FRAMERATE_29_97): 
            self.frame_rate_enumerator = 30000
            self.frame_rate_denominator = 1001
        elif (self.framerate == FrameRate.FRAMERATE_50): 
            self.frame_rate_enumerator = 50000
            self.frame_rate_denominator = 1000
        elif (self.framerate == FrameRate.FRAMERATE_59_94): 
            self.frame_rate_enumerator = 60000
            self.frame_rate_denominator = 1001

    @property
    def desc(self):
        description = ""         
        if self.height > 0:
            description += "{0}{1} / ".format(self.height, "i" if self.isInterlaced else "p") # Note ternary conditional
        if (self.frame_rate_enumerator > 0 and self.frame_rate_denominator > 0):                
            if (self.frame_rate_enumerator % self.frame_rate_denominator == 0):                    
                description += "{0:d} fps / ".format( (self.frame_rate_enumerator / self.frame_rate_denominator))                    
            else:                    
                description += "{0:.2f} fps / ".format( (self.frame_rate_enumerator / self.frame_rate_denominator))
        if self.aspectratio == AspectRate.ASPECT_4_3:                
            description += "4:3 / "                
        elif self.aspectratio == AspectRate.ASPECT_16_9:                
            description += "16:9 / "
        elif self.aspectratio == AspectRate.ASPECT_2_21:                
            description += "2:21 / "
        if self.encoding_profile != None:                
            description += self.encoding_profile + " / "
        if description.endswith(' / '): # Why the fuck is this in here I have no idea. Maybe if it somethow has to remove a stray " / " ending. Seems odd, but whatever
            description = description[:(description.__len__() - 3)]                
        return description
    

    def __str__(self):
        return "The ID is {}, the codec type is {}, and the general description is {}. The stream/track number will hopefully be added here".format(self.PID, altcodecfunc(self.streamtype), self.desc())


class TSAudioStream(Stream):

    def __init__(self):
        super().__init__()
        self.samplerate = 0
        self.channelcount = 0
        self.bitdepth = 0
        self.lfe = 0
        self.dialnorm = 0
        self.audiomode = None
        self.corestream =  None
        self.channellayout = None
        self.isAudio = True


    def convertsamplerate(self, extsamplerate):                        # This is confusing and interesting. I have a Stream object in the main code. It will get set by this function call in the main code. Though, if it is undefined then later on it could mess up the other code (like method function desc())
        if extsamplerate == SampleRate.SAMPLERATE_48:
            return 48000
        elif extsamplerate == SampleRate.SAMPLERATE_96 or extsamplerate == SampleRate.SAMPLERATE_48_96 :
            return 96000
        elif extsamplerate == SampleRate.SAMPLERATE_192 or extsamplerate == SampleRate.SAMPLERATE_48_192 :
            return 192000
        else:
            return 0


    def channeldesc(self):
        if ( self.channellayout == ChannelLayout.CHANNELLAYOUT_MONO and self.channelcount == 2 ):
            pass

        description = ""
        if self.channelcount > 0:
            description += "{0:D}.{1:d}".format(self.channelcount, self.lfe)
        elif ChannelLayout.CHANNELLAYOUT_MONO:
            description += "2.0"
        elif ChannelLayout.CHANNELLAYOUT_STEREO:
            description += "3.1"
        elif ChannelLayout.CHANNELLAYOUT_MULTI:
            description += "1.0"

        if self.audiomode == AudioMode.Extended:
            description += "-EX"
        if (self.streamtype == StreamType.DTS_AUDIO or self.streamtype == StreamType.DTS_HD_AUDIO or self.streamtype == StreamType.DTS_HD_MASTER_AUDIO):
            description += "-ES"

        return description

    @property
    def desc(self):
        description = self.channeldesc()   # I wonder if I will need to change this to TSAudioStream.channeldesc(). However this is just to mimic the C Sharp since using accessors in Python is complicated

        if self.samplerate > 0:
            description += " / {0} kHz".format((self.samplerate / 1000))
        if self.bitrate > 0:
            description += "/ {0} kbps".format((self.bitrate / 1000)) # Original source uses a round() func, but I think may not need for Python math
        if self.bitdepth > 0:
            description += "/ {0}-bit".format(self.bitdepth)
        if self.dialnorm !=0:
            description += "/ DN {0}db".format(self.dialnorm)
        if self.channelcount == 2:
            if self.audiomode == AudioMode.DualMono:
                description += " /Dual Mono"
            elif self.audiomode == AudioMode.Surround:
                description += " / Dolby Surround"
        if description.endswith(' / '): # Why the heck is this in here I have no idea. Maybe if it somehow has to remove a stray " / " ending. Seems odd, but whatever
            description = description[:(description.__len__() - 3)]
        if self.corestream != None:                                                                         # Here I may need to investigate where Csharp source Corestream information actually got passed.
            corecodec = ""
            if self.corecodec == StreamType.AC3_Audio :
                    corecodec = "AC3 Embedded"
            elif self.corecodec == StreamType.DTS_Audio:
                    corecodec = "DTS Core"
                    
        return description


    def __str__(self):
        return "The ID is {}, the language code is {} (most likely references {}), the codec type is {}, the channel description is {}, and the general description is {}".format(self.PID, self.languagecode, isolangfunc(self.languagecode), altcodecfunc(self.streamtype), self.channeldesc(), self.desc())

class TSTextStream(Stream):
    def __init__(self):
        self.isVBR = True
        self.isInitialized = True
        self.isText = True

    def __str__(self):        
        return "The ID is {}, the language code is {} (most likely references {}) and the  codec is {}".format(self.PID, self.languagecode, isolangfunc(self.languagecode), altcodecfunc(self.streamtype))
        

class TSGraphicsStream(Stream):
    def __init__(self):
        self.isVBR = True
        self.isInitialized = True
        self.isGraphic = True

    def __str__(self):        
       return "The ID is {}, the language code is {} (most likely references {}) and the codec is {}".format(self.PID, self.languagecode, isolangfunc(self.languagecode), altcodecfunc(self.streamtype))
        

# Playlist Class Structure

class MPLS(object):
    
    def __init__(self):
        self.filepath = None
        self.filetype = None  # move to function most likely
        self.isInitialized = False
        self.isCustom = False
        self.isLooped = False
        self.HiddenTracks = False
        
        self.chapterclips = []
        self.streamclips = []
        
        self.playlistchapters = []  # The chapters here already have their "relative values" calculated. What orig BDInfo puts out too.
        
        self.streams = {}           
        self.playliststreams = {}
        self.anglestreams = {}
        self.angleclips = []
        self.anglecount = 0
        
        self.sortedstreams = []
        self.videostreams = []
        self.audiostreams = []
        self.textstreams = []
        self.graphicsstreams = []
        
    @property
    def totallength(self):
        val = 0
        for clip in self.streamclips:
            val += clip.length
        return val
    

class StreamClip(object):
    def __init__(self):
        self.chapters = []

    

    
    
    
    
            
    
        
        
    
