#!/bin/env python3

import sys                              # St&ard. Also good for platform values
import os                                # Portability module
import ts_streamtypeclass
from ts_attrconst import StreamType
from os.path import basename
from iso_639_2map import isolangfunc         # Converting language codes ISO-639-2
from datetime import timedelta

def clipfilescan(cpath,cliplists):
    clipfilescanresults = {}
    for target in cliplists:
        fullpath = os.path.join(cpath, target)
        try:
            f = open(fullpath, 'rb')
            binreadfile = bytes(f.read())
            if (binreadfile[:8] != b"HDMV0100") and (binreadfile[:8] != b"HDMV0200") and (binreadfile[:8] != b"HDMV0300"):   
                raise Exception("Exception: CPLI file {} has an unknown filetype {}!".format(fullpath, binreadfile[:8]))
            
            allstreams = {}
            allstreams["FILE"] = fullpath
            
            clipIndex = (binreadfile[12] << 24) + (binreadfile[13] << 16) + (binreadfile[14] << 8) + (binreadfile[15])
            cliplength = (binreadfile[clipIndex] << 24) + (binreadfile[clipIndex + 1] << 16) + (binreadfile[clipIndex + 2] << 8) + (binreadfile[clipIndex + 3])

            # Copy only relevant streams data from CLPI and delete bindata                                 
            clipdata = binreadfile[(clipIndex+4):]
            del binreadfile

            # Get num of streams and their offset
            streamscount = clipdata[8]
            streamoffset = 10
            streamindex = 0
            
            while streamindex < streamscount:
                
                streamPID = ((clipdata[streamoffset] << 8) +  clipdata[streamoffset + 1])

                # Moves offset marker to sit on the length of the StreamCodingInfo section
                streamoffset += 2

                streamtype = clipdata[streamoffset + 1]

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
                    languagebytes = clipdata[(streamoffset + 3):(streamoffset + 6)]
                    languagecode = languagebytes.decode("ascii")
                    channellayout = (clipdata[streamoffset + 2] >> 4)           
                    samplerate = (clipdata[streamoffset + 2] & 0xF)
                    
                    # Saving data into Audiostream. 
                    stream = ts_streamtypeclass.TSAudioStream()
                    stream.languagecode = languagecode
                    stream.channellayout = channellayout
                    stream.samplerate = stream.convertsamplerate(samplerate)
                    stream.streamtype = streamtype
                    stream.languagename = isolangfunc(stream.languagecode)

                elif (streamtype == StreamType.INTERACTIVE_GRAPHICS or streamtype == StreamType.PRESENTATION_GRAPHICS):
                    stream = ts_streamtypeclass.TSGraphicsStream()
                    languagebytes = clipdata[(streamoffset + 2):(streamoffset + 5)]
                    languagecode = languagebytes.decode("ascii")
                    stream.languagecode = languagecode
                    stream.languagename = isolangfunc(stream.languagecode)

                elif (streamtype == StreamType.SUBTITLE):

                    stream = ts_streamtypeclass.TSTextStream()
                    languagebytes = clipdata[(streamoffset + 3):(streamoffset + 6)]
                    languagecode = languagebytes.decode("ascii")
                    stream.languagecode = languagecode
                    stream.languagename = isolangfunc(stream.languagecode)
                    
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
            f.close()
    return clipfilescanresults



def playlistscan(ppath, playlists, cliplists, streamlists):
    playlistscanresults = {}

    for target in playlists:
        fullpath = os.path.join(ppath, target)
        try:
            f = open(fullpath, 'rb')
            binfiledatas = bytes(f.read())
            if (binfiledatas[:8] != b"MPLS0100") and (binfiledatas[:8] != b"MPLS0200") and (binfiledatas[:8] != b"MPLS0300"):   
                raise Exception("Exception: MPLS file {} is of an unsupported playlist type {}!".format(fullpath, binfiledatas[:8]))

            
            def createplayliststream(data, pos):
                
                stream = None
                #start = pos[0]  # Super unnecessary
                
                pos[0] += 1
                headerlength = readbyte(data, pos)

                headerposition = pos[0]
                headertype = readbyte(data, pos)

                #print("Headerposition ===>", headerposition, "\n Headerlength ====>", headerlength)
                
                pid = 0
                subpathpid = 0
                subclipid = 0
                
                if headertype == 1:
                    pid = readint16(data, pos)
                    
                elif headertype == 2: 
                    subpathid = readbyte(data, pos)
                    subclipid = readbyte(data, pos)
                    pid = readint16(data, pos)
                
                elif headertype == 3: 
                    subpathid = readbyte(data, pos)
                    pid = readint16(data, pos)
                
                elif headertype == 4:
                    subpathid = readbyte(data, pos)
                    subclipid = readbyte(data, pos)
                    pid = readint16(data, pos)
                
                else:
                        print("Variable 'headertype' value not recognized. The value is: ", headertype)
                
                pos[0] = headerposition + headerlength
                
                # Reordered ahead in order retrieve the byte before current pos variable is increased by 1
                streampos = pos[0]                    
                
                streamlength = readbyte(data, pos)
                streamtype = readbyte(data, pos)


                # Slightly modified CLIPNF portion for STN Stream Attributes Table.
                if (streamtype == StreamType.MVC_VIDEO):
                    stream = ts_streamtypeclass.Stream()
                elif (streamtype == StreamType.AVC_VIDEO or streamtype == StreamType.MPEG1_VIDEO or streamtype == StreamType.MPEG2_VIDEO or streamtype == StreamType.VC1_VIDEO or streamtype == StreamType.HEVC_VIDEO):              
                    videobyte = readbyte(data, pos)
                    videoFormat = (videobyte >> 4);
                    frameRate = (videobyte & 0xF);
                                        
                    stream = ts_streamtypeclass.TSVideoStream()
                    stream.videoformat = videoFormat
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
                    #char_code =readbyte(data,pos)   #Scala implemenation has this but really appears unnecessary
                    languagecode = readbyte(data, pos, 3)
                    stream.languagecode = languagecode
                    
                else:
                    raise Exception("Can't determine StreamType in CreatePlaylist Fuction.")
                    
                pos[0] = streampos + streamlength
                
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
                # tempvar created here because we return the data while increasing the position afterwards since we dont have ++
                tempvar = data[pos[0]]
                pos[0] += 1

                return tempvar 
                

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
                                      streeeemFile = streamlists.index(streamfilename)      # Using index method returns integer
                if streeeemFile == None:
                        print("Debug Error. Missing file in reference:", streamfilename)

                streamclipname = itemname + ".clpi" 
                if streamclipname in cliplists:               # This suite might be totally useless for Python
                                      streeeemClipFile = cliplists.index(streamclipname)      # Using index method returns integer
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

                # GenPlaylist needs a better name
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

                                angleclipname = anglename + ".clpi"
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

                        if (angles - 1) > anglecount:    # Abhor ANGLES. Few BDMVs even support them. Still need to ensure this is accurate though
                                anglecount = angles - 1

                streaminfolength = readint16(binfiledatas, pos)
                pos[0] += 2                                                     #Move position ahead over 2 reserved bytes
                streamcountvideo = binfiledatas[pos[0]]
                pos[0] += 1
                streamcountaudio = binfiledatas[pos[0]]
                pos[0] += 1
                streamcountpg = binfiledatas[pos[0]]
                pos[0] += 1
                streamcountig = binfiledatas[pos[0]]
                pos[0] += 1
                streamcountsecondaryaudio = binfiledatas[pos[0]]
                pos[0] += 1
                streamcountsecondaryvideo = binfiledatas[pos[0]]
                pos[0] += 1
                streamcountpip = binfiledatas[pos[0]]
                pos[0] += 5
                
                GenPlaylist.summary = { 'playlist': basename(f.name),
                                        'streamfile' : streamfilename,
                                        'V': streamcountvideo,
                                        'A':streamcountaudio,
                                        'PG': streamcountpg,
                                        'IG': streamcountig,
                                        '2A' :streamcountsecondaryaudio,
                                        '2V': streamcountsecondaryvideo,
                                        'PIP': streamcountpip,
                                        'duration': GenPlaylist.totallength,
                                        'hduration': ts_streamtypeclass.MPLS.convertchaptersecs(timedelta(seconds=GenPlaylist.totallength))
                                        }
                
                print(GenPlaylist)
                
                for a in range(0,streamcountvideo):
                    debug_stream =  createplayliststream(binfiledatas, pos)
                    if debug_stream:
                        GenPlaylist.playliststreams[debug_stream.PID] = debug_stream
                                                        
                for a in range(0,streamcountaudio):
                    debug_stream =  createplayliststream(binfiledatas, pos)
                    if debug_stream:
                        GenPlaylist.playliststreams[debug_stream.PID] = debug_stream
                
                for a in range(0,streamcountpg):
                    debug_stream =  createplayliststream(binfiledatas, pos)
                    if debug_stream:
                        GenPlaylist.playliststreams[debug_stream.PID] = debug_stream
                
                for a in range(0,streamcountig):
                    debug_stream =  createplayliststream(binfiledatas, pos)
                    if debug_stream:
                        GenPlaylist.playliststreams[debug_stream.PID] = debug_stream
                
                for a in range(0,streamcountsecondaryaudio):
                    debug_stream =  createplayliststream(binfiledatas, pos)
                    if debug_stream:
                        GenPlaylist.playliststreams[debug_stream.PID] = debug_stream
                        pos[0] += 2
                
                for a in range(0,streamcountsecondaryvideo):
                    debug_stream =  createplayliststream(binfiledatas, pos)
                    if debug_stream:
                        GenPlaylist.playliststreams[debug_stream.PID] = debug_stream
                        pos[0] += 6


                pos[0] += itemlength - (pos[0] - itemstart) + 2
                
            # End of for-range Loops            
            
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
