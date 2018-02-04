#!/bin/env python3

import sys                              # St&ard. Also good for platform values
import os                                # Portability module
import iso_639_2map         # Converting language codes ISO-639-2 
import ts_streamtypeclass
from ts_attrconst import StreamType
from os.path import basename as basename



def clipfilescan(cpath,cliplists):
    clipfilescanresults = {}
    for target in cliplists:
        fullpath = os.path.join(cpath, target)
        try:
            f = open(fullpath, 'rb')                                    # opening the file for BINARY reading
            binreadfile = bytes(f.read())                       # I believe we mirror BDINFO itselff and read the whole file into the variable. Hence why we only sliced to the 8th bit in the next line.
            if (binreadfile[:8] != b"HDMV0100") and (binreadfile[:8] != b"HDMV0200") and (binreadfile[:8] != b"HDMV0300"):   
                raise Exception("Exception: CPLI file {} has an unknown filetype {}!".format(fullpath, binreadfile[:8]))    # Because we dont know the file type
            
            allstreams = {}
            allstreams["FILE"] = fullpath
            
            clipIndex = (binreadfile[12] << 24) + (binreadfile[13] << 16) + (binreadfile[14] << 8) + (binreadfile[15])
            cliplength = (binreadfile[clipIndex] << 24) + (binreadfile[clipIndex + 1] << 16) + (binreadfile[clipIndex + 2] << 8) + (binreadfile[clipIndex + 3])

            clipdata = bytes(cliplength)                                 
            clipdata = binreadfile[(clipIndex+4):]    #Altered Here because the Csharp version uses Array.Copy and one parameter is length but its cumulative. Since I dont know how they arrived exactly at how many more cumulative bytes to copy I'll just copy the entire rest of the array. So it's different from the Csharp here. I suppose I could do the len(array + math) but nah.

            streamscount = clipdata[8]
            streamoffset = 10
            streamindex = 0
            
            while streamindex < streamscount:
                
                streamPID = ((clipdata[streamoffset] << 8) +  clipdata[streamoffset + 1])

                streamoffset += 2

                streamtype = clipdata[streamoffset + 1]

                #<Figuring Out How To Convert The Switch Statement Here >#  //It looks like I need to reference TSStream.cs for the class that was created and to get the mappings of the hex bytes to ascii names.
                if (streamtype == StreamType.MVC_VIDEO):
                    stream = ts_streamtypeclass.Stream()
                elif (streamtype == StreamType.AVC_VIDEO or streamtype == StreamType.MPEG1_VIDEO or streamtype == StreamType.MPEG2_VIDEO or streamtype == StreamType.VC1_VIDEO):              
                    
                    # Considering the next section this may be redundant but does make it easier to read
                    videoFormat = (clipdata[streamoffset + 2] >> 4);
                    frameRate = (clipdata[streamoffset + 2] & 0xF);
                    aspectRatio = (clipdata[streamoffset + 3] >> 4);
                    
                    # Setting the values for the instance of Stream class for this loop iteration
                    stream = ts_streamtypeclass.TSVideoStream()
                    stream.videoformat = videoFormat
                    stream.aspectratio = aspectRatio
                    stream.framerate = frameRate

                    # Run this streamtype's specific methods to internally modify some data
                    stream.convertvidformat()
                    stream.convertframerate()
                    
                
                elif (streamtype == StreamType.AC3_AUDIO or streamtype == StreamType.AC3_PLUS_AUDIO or streamtype == StreamType.AC3_PLUS_SECONDARY_AUDIO or streamtype == StreamType.AC3_TRUE_HD_AUDIO or streamtype == StreamType.DTS_AUDIO or streamtype == StreamType.DTS_HD_AUDIO or streamtype == StreamType.DTS_HD_MASTER_AUDIO or streamtype == StreamType.DTS_HD_SECONDARY_AUDIO or streamtype == StreamType.LPCM_AUDIO or streamtype == StreamType.MPEG1_AUDIO or streamtype == StreamType.MPEG2_AUDIO):

                    # Pull the data into variables
                    languagebytes = clipdata[streamoffset + 3:((streamoffset + 3) + 3)]
                    languagecode = languagebytes.decode("ascii")
                    channellayout = (clipdata[streamoffset + 2] >> 4)           
                    samplerate = (clipdata[streamoffset + 2] & 0xF)
                    
                    # Saving data into Audiostream. 
                    stream = ts_streamtypeclass.TSAudioStream()
                    stream.languagecode = languagecode
                    stream.channellayout = channellayout
                    stream.samplerate = stream.convertsamplerate(samplerate)
                    stream.streamtype = streamtype

 
                elif (streamtype == StreamType.INTERACTIVE_GRAPHICS or streamtype == StreamType.PRESENTATION_GRAPHICS):

                    stream = ts_streamtypeclass.TSGraphicsStream()
                    languagebytes = clipdata[(streamoffset + 2):3]
                    languagecode = languagebytes.decode("ascii")
                    stream.languagecode = languagecode
 
                
                elif (streamtype == StreamType.SUBTITLE):

                    stream = ts_streamtypeclass.TSTextStream()
                    languagebytes = clipdata[streamoffset + 3:((streamoffset + 3) + 3)]
                    languagecode = languagebytes.decode("ascii")
                    stream.languagecode = languagecode
                    
                    
                if stream != None:
                    stream.PID = streamPID
                    stream.streamtype = streamtype
                    allstreams[streamindex] = stream
                    
                streamindex +=1
                streamoffset += clipdata[streamoffset] + 1
            clipfilescanresults[target] = allstreams

        except(IOError, FileNotFoundError):
            print("Exception: Error Opening File for Reading: ", fullpath)
        finally:
            '''## Remove After Testing ##
                for item in allstreams:
                print("This is allstreams item/key value of: ", item)
                print(allstreams[item])
                '''
            f.close()
    return clipfilescanresults




def playlistscan(ppath, playlists, cliplists, streamlists):
    playlistscanresults = {}

    for target in playlists:
        fullpath = os.path.join(ppath, target)
        try:
            f = open(fullpath, 'rb')                                    # opening the file for BINARY reading
            binfiledatas = bytes(f.read())                       # I believe we mirror BDINFO itselff and read the whole file into the variable. Hence why we only slice to the 8 bit in the next line.
            if (binfiledatas[:8] != b"MPLS0100") and (binfiledatas[:8] != b"MPLS0200") and (binfiledatas[:8] != b"MPLS0300"):   
                raise Exception("Exception: MPLS file {} is of an unsupported playlist type {}!".format(fullpath, binfiledatas[:8]))    # Because we dont know the file type

            
            def createplayliststream(data, pos):
                
                stream = None
                start = pos[0]
                headerlength = data[pos[0]+1]
                headerposition = pos[0]
                headertype = data[pos[0] + 1]
                
                pid = 0
                subpathpid = 0
                subclipid = 0
                
                if headertype == 1:
                    pid = readint16(data, pos)
                    
                elif headertype == 2: 
                    subpathid = data[pos[0] + 1]
                    subclipid = data[pos[0] + 1]
                    pid = readint16(data, pos)
                
                elif headertype == 3: 
                    subpathid = data[pos[0] + 1]
                    pid = readint16(data, pos)
                
                elif headertype == 4:
                    subpathid = data[pos[0] + 1]
                    subclipid = data[pos[0] + 1]
                    pid = readint16(data, pos)
                
                else:
                    print("Variable 'headertype' value not recognized. The value is: ", headertype)
                
                pos[0] = headerposition + headerlength
                streamlength = data[pos[0] + 1];
                streampos = pos[0]
                
                streamtype = data[pos[0] + 1]
                
                # Basically everything below is a slightly modified copy+paste of the CLIPNF portion.
                if (streamtype == StreamType.MVC_VIDEO):
                    stream = ts_streamtypeclass.Stream()
                elif (streamtype == StreamType.AVC_VIDEO or streamtype == StreamType.MPEG1_VIDEO or streamtype == StreamType.MPEG2_VIDEO or streamtype == StreamType.VC1_VIDEO):              
                                        
                    videoFormat = (data[pos[0]] >> 4);
                    frameRate = (data[pos[0]] & 0xF);
                    aspectRatio = (data[pos[0] +1] >> 4);
                    
                    stream = ts_streamtypeclass.TSVideoStream()
                    stream.videoformat = videoFormat
                    stream.aspectratio = aspectRatio
                    stream.framerate = frameRate
                    
                elif (streamtype == StreamType.AC3_AUDIO or streamtype == StreamType.AC3_PLUS_AUDIO or streamtype == StreamType.AC3_PLUS_SECONDARY_AUDIO or streamtype == StreamType.AC3_TRUE_HD_AUDIO or streamtype == StreamType.DTS_AUDIO or streamtype == StreamType.DTS_HD_AUDIO or streamtype == StreamType.DTS_HD_MASTER_AUDIO or streamtype == StreamType.DTS_HD_SECONDARY_AUDIO or streamtype == StreamType.LPCM_AUDIO or streamtype == StreamType.MPEG1_AUDIO or streamtype == StreamType.MPEG2_AUDIO):

                    audioFormat = readbyte(data, pos)
                    channellayout = (audioFormat >> 4)
                    samplerate = (audioFormat & 0xF)
                    languagecode = readstring(data, pos, 3)
                    
                    stream = ts_streamtypeclass.TSAudioStream()
                    stream.languagecode = languagecode
                    stream.channellayout = channellayout
                    stream.samplerate = stream.convertsamplerate(samplerate)
                    
                elif (streamtype == StreamType.INTERACTIVE_GRAPHICS or streamtype == StreamType.PRESENTATION_GRAPHICS):

                    stream = ts_streamtypeclass.TSGraphicsStream()
                    languagecode = readstring(data, pos, 3)
                    stream.languagecode = languagecode
                    
                elif (streamtype == StreamType.SUBTITLE):

                    stream = ts_streamtypeclass.TSTextStream()
                    languagecode = readbyte(data, pos, 3)
                    stream.languagecode = languagecode
                    
                else:
                    pass
                    
                    
                pos = [streampos + streamlength]

                if stream:
                    stream.PID = pid
                    stream.streamtype = streamtype
                    
                return stream
        
        
            def readint32(data, pos):
                val = (data[pos[0]] << 24) + (data[pos[0] + 1] << 16) + (data[pos[0] + 2] << 8) + (data[pos[0] + 3])
                pos[0] += 4
                return val


            def readint16(data, pos):
                val = (data[pos[0]] << 8) + (data[pos[0] + 1])
                pos[0] += 2
                return val


            def readbyte(data, pos):
                return data[pos[0]+1]


            def readstring(data, pos, count):
                val =  data[pos[0]:(pos[0]+count)]
                pos[0] += count
                return val.decode(encoding="utf-8")
                

            pos = [0]
            filetype = readstring(binfiledatas, pos, 8)

            playlistoffset = readint32(binfiledatas, pos)
            chaptersoffset = readint32(binfiledatas, pos)
            extensionoffset = readint32(binfiledatas, pos)


            pos = [playlistoffset]
            playlistlength = readint32(binfiledatas, pos)
            playlistreserved = readint16(binfiledatas, pos)


            itemcount = readint16(binfiledatas, pos)
            subitemcount = readint16(binfiledatas,pos)
            itemindex = 0
            
            GenPlaylist = ts_streamtypeclass.MPLS()
            
            for itemindex in range(itemcount):
                itemstart = pos[0]
                itemlength = readint16(binfiledatas, pos)
                itemname = readstring(binfiledatas, pos, 5)
                itemtype = readstring(binfiledatas, pos, 4)

                streamfilename = itemname + ".m2ts"
                if streamfilename in streamlists:               # This suite might be totally useless for Python
                                      streeeemFile = streamlists.index(streamfilename)      # clever me using the index method lol
                if streeeemFile == None:
                        print("Debug Error. Missing file in reference:", streamfilename)

                streamclipname = itemname + ".clpi" 
                if streamclipname in cliplists:               # This suite might be totally useless for Python
                                      streeeemClipFile = cliplists.index(streamclipname)      # clever me using the index method lol
                if streeeemClipFile == None:
                        print("Debug Error. Playlist referenced missing CLPI file in reference:", streamfilename, streamclipname)

                pos[0] += 1
                multiangle = (binfiledatas[pos[0]] >> 4) & 0x01
                condition = (binfiledatas[pos[0]] & 0x0F)
                pos[0] += 2

                intime = readint32(binfiledatas, pos)
                if intime < 0:
                        intime &= 0x7FFFFFFF
                else:
                        pass
                        
                timein = intime / 45000 # Should I float()?
                outtime = readint32(binfiledatas, pos)
                
                if outtime < 0:
                        outtime &= 0x7FFFFFFF
                else:
                        pass
                timeout = outtime / 45000 # Should I float()?

                streamClip = ts_streamtypeclass.StreamClip()
                streamClip.streamfilename = streeeemFile
                streamClip.streamclipfile = streeeemClipFile
                streamClip.name = streamfilename
                streamClip.timein = timein
                streamClip.timeout = timeout
                streamClip.length = timeout - timein
                streamClip.relativetimein = GenPlaylist.totallength     
                streamClip.relativetimeout = streamClip.relativetimein + streamClip.length

                # The naming is so confusing and I dont know how to add this junk yet so. On-The-Fly Variable !
                GenPlaylist.streamclips.append(streamClip)
                GenPlaylist.chapterclips.append(streamClip)

                
                pos[0] += 12
                if multiangle > 0:
                        angles  = data[pos[0]]
                        pos[0] += 2
                        angle = 0

                        while angle < angles - 1:
                                anglename = readstring(data, pos, 5)
                                angletype = readstring(data, pos, 4)
                                pos[0] +=1

                                
                                anglefilename = anglename + ".m2ts"
                                if anglefilename in streamlists:               # This suite might be totally useless for Python
                                                      angleeeeFile = streamlists.index(anglefilename)      # clever me using the index method lol
                                if angleeeeFile == None:
                                        print("Debug Error. Missing M2TS ANGLE file in reference:", anglefilename)

                                angleclipname= anglename + ".clpi"
                                if angleclipname in cliplists:               # This suite might be totally useless for Python
                                        anglestreeeemClipFile = cliplists.index(angleclipname)      # clever me using the index method lol

                                if anglestreeeemClipFile == None:
                                        print("Debug Error. Playlist referenced missing for ANGLE CLPI file in reference:", anglefilename, angleclipname)
                                
                                angleClip = ts_streamtypeclass.StreamClip()
                                angleClip.angleindex = angle + 1
                                angleClip.timein = streamClip.timein
                                angleClip.timeout = streamClip.timeout
                                angleClip.length = streamClip.length
                                angleClip.relativetimein = streamClip.relativetimein
                                angleClip.relativetimeout = streamClip.relativetimeout
                                GenPlaylist.streamclips.append(angleClip)
                                
                                angle += 1

                        if (angles - 1) > anglecount:    # I HATE THESE ANGLES. Few BDMVs even support them. Still make sure this is accurate though
                                anglecount = angles - 1

                
                streaminfolength = readint16(binfiledatas, pos)
                pos[0] += 2
                streamcountvideo = binfiledatas[pos[0]+1]
                streamcountaudio = binfiledatas[pos[0]+1]
                streamcountpg = binfiledatas[pos[0]+1]
                streamcountig = binfiledatas[pos[0]+1]
                streamcountsecondaryaudio = binfiledatas[pos[0]+1]
                streamcountsecondaryvideo = binfiledatas[pos[0]+1]
                streamcountpip = binfiledatas[pos[0]+1]
                pos[0] += 5
                
                print("{0}:{1} -> V:{2} A:{3} PG:{4} IG:{5} 2A:{6} 2V:{7} PIP:{8}".format(basename(f.name),streamfilename, streamcountvideo, streamcountaudio, streamcountpg, streamcountig, streamcountsecondaryaudio, streamcountsecondaryvideo, streamcountpip))
                pos[0]+= itemlength - (pos[0] - itemstart) + 2
                
                
                for a in range(0,streamcountvideo):
                    debug_stream =  createplayliststream(binfiledatas, pos)
                    if debug_stream:
                        GenPlaylist.playliststreams[stream.PID] = debug_stream
                                                        
                for a in range(0,streamcountaudio):
                    debug_stream =  createplayliststream(binfiledatas, pos)
                    if debug_stream:
                        GenPlaylist.playliststreams[stream.PID] = debug_stream
                
                for a in range(0,streamcountpg):
                    debug_stream =  createplayliststream(binfiledatas, pos)
                    if debug_stream:
                        GenPlaylist.playliststreams[stream.PID] = debug_stream
                
                for a in range(0,streamcountig):
                    debug_stream =  createplayliststream(binfiledatas, pos)
                    if debug_stream:
                        GenPlaylist.playliststreams[stream.PID] = debug_stream
                
                for a in range(0,streamcountsecondaryaudio):
                    debug_stream =  createplayliststream(binfiledatas, pos)
                    if debug_stream:
                        GenPlaylist.playliststreams[stream.PID] = debug_stream
                    pos[0] += 2
                
                for a in range(0,streamcountsecondaryvideo):
                    debug_stream =  createplayliststream(binfiledatas, pos)
                    if debug_stream:
                        GenPlaylist.playliststreams[stream.PID] = debug_stream
                
                
                pos[0] += 6
            
                pos[0] += itemlength - (pos[0] - itemstart) + 2
                
            
            # End for-range Loop - Do the variable (esp streamclip and xxStreamClipsxx still exist            
            
            pos[0] = chaptersoffset + 4
            chaptercount = readint16(binfiledatas, pos)
            
            for chapterindex in range(chaptercount):
                
                chaptertype = binfiledatas[pos[0] + 1]
                
                if chaptertype == 1:
                    streamfileindex = (binfiledatas[pos[0] + 2] << 8) + (binfiledatas[pos[0] + 3])
                    chaptertime = (binfiledatas[pos[0] + 4] << 24) + (binfiledatas[pos[0] + 5] << 16) + (binfiledatas[pos[0] + 6] << 8) + (binfiledatas[pos[0] + 7])
                    
                    streamClip = GenPlaylist.chapterclips[streamfileindex]
                    
                    chaptersecs = chaptertime / 45000
                    
                    relativesecs = chaptersecs - streamClip.timein + streamClip.relativetimein
                    
                    if (GenPlaylist.totallength - relativesecs > 1.0):
                        streamClip.chapters.append(chaptersecs)
                        GenPlaylist.playlistchapters.append(relativesecs)         # this differs from source originally name is temporary work around
                    else:
                        pass
                    
                    pos[0] += 14
                                        
            playlistscanresults[target] = GenPlaylist
            
        except(IOError, FileNotFoundError):
            print("Exception: Error Opening File for Reading: ", fullpath)
        finally:
            f.close()

    return playlistscanresults
        
