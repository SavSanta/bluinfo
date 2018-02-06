#!/bin/env python3

import sys                              # St&ard. Also good for platform values
import os                                # Portability module
import time                         # sleep calls mainly
import iso_639_2map         # Converting language codes ISO-639-2 
import argparse                 # For commandline parsing. ( may need to look into other solutions).
import tkinter                   # For the GUI that some will say is undoubtedbly ugly.
import ts_scanner as ScanTask
from datetime import timedelta                     # date and date conversions for logs

__version__ = "0.4"
__author__ = "SavSanta"

sysplatform =  sys.platform                     # For future bug testing on Windows primarily

class BDROM():

    def __init__(self):

       self.dir_root = None
       self.dir_bdmv = None
       
       self.dir_bdjo = None
       self.dir_clip = None
       self.dir_playlist = None
       self.dir_snp = None
       self.dir_ssif = None
       self.dir_stream = None

       self.bd_plus = False
       self.bd_java = False
       self.bd_dbox = False
       self.bd_psp = False
       self.bd_3d = False
       self.bd_50Hz = False
       self.bd_size = 0


    def checkBDMV(self, filepath):
        if not os.path.exists(filepath):
            raise IOError("Ensure the path exists: ", filepath)    # Write exception handler (IOError, NotADirectory, etc)
        else:
            pass
               
        filepath = os.path.join((os.path.expanduser(filepath)), "")   # This will add a trailing / incase it's not already added. Notation in case this breaks something. Especially across different platforms. Although, if Im not mistaken Windows platform can handle double forward slash as well as Unix platforms to some degree. # SideThought: Should I check the os.path.supports_unicode_filenames variable for certain filesystems? Being that the os.path.walk documentation says depending on path supplied it could be byte strings or unicode strings.
        print("Attempting to utilize path \' %s \' as the root directory." % filepath)
                                                               
        if "BDMV" in [x for x in os.listdir(filepath) if os.path.isdir(os.path.join(filepath, x))]:                                              # On Unix systems we have to be wary aboout the case sensitivity?  Testing for "BDMV" versus "bdmv". Most BDMVs are caps ime. May implement a solution using re module or fnmatch
            self.dir_root = filepath                                                    # Should note when using the os.path.join() methods later, basically only the first string can use an absolute path without deleting the rest. See help(os.path.join) for what I mean
            self.dir_bdmv = os.path.join(filepath, "BDMV", "")          # I explicitly join and set the path to it's BDMV variable here. Maybe I should convert it to an absolute path to make extra clear?

            listcomp = os.listdir(self.dir_bdmv)
            if ("CLIPINF" in listcomp) and ("PLAYLIST" in listcomp) and ("STREAM" in listcomp):   
                self.dir_stream = os.path.join(self.dir_bdmv, "STREAM", "")
                self.dir_clip = os.path.join(self.dir_bdmv, "CLIPINF", "")
                self.dir_playlist = os.path.join(self.dir_bdmv, "PLAYLIST", "")
                return
            else:
                raise RunTimeError("Error: Couldnt find CLIPINF, PLAYLIST, and STREAM directories.")
        else:
            raise RuntimeError("Error: BDMV directory structure could not be found. Are you certain the BluRay ROOT path exists (i.e. /mnt/ not /mnt/BDMV/)?")


    def sizeBDMV(self):
        
        size = 0
        for root, dirs, files in os.walk(self.dir_root):
            while files:
                popfiles = files.pop()                                     # I decided to pop the files outside of the list here, as it makes it easier to go with the implicit BOOLEAN check of the lists existence/emptyness in the start of the while loop.
                print("Joined {} and {} for filesize calculation".format(root, popfiles))
                print("Added {} to the size value calculation".format(os.path.getsize(os.path.join(root,popfiles))))
                size += os.path.getsize(os.path.join(root,popfiles))
        self.bd_size = size
        print("Total size of BluRay on {} is {:,} : ".format( self.dir_root, self.bd_size)) # The {:,} forces the comma seperator since {n} didt work on my Linux Machine
        return

    def cryptBDMV(self):
        for _, dirs, _ in os.walk(self.dir_bdmv):
            if "BDSVM" in dirs:
                self.bd_plus = True            
            if "SLYVM" in dirs:
                self.bd_plus = True
            if "ANYVM" in dirs:
                self.bd_plus = True
        return

    def specialBDMV(self):
        if (self.dir_root): 
            
            if os.path.exists(os.path.join(self.dir_bdmv, "FilmIndex.xml")):
                self.bd_dbox = True

            if os.path.exists((os.path.join(self.dir_bdmv, "BDJO", ""))):
                self.dir_bdjo = os.path.join(self.dir_bdmv, "BDJO", "")           
                k = os.walk(self.dir_bdjo).__next__()
                if k[2].__len__():          # NotSoPythonicNote: Test if the files value of generator is True (ie is greater than 0, as False is 0 ie no files).  Also this is slower than calling built-in len()
                        self.bd_java = True
                        del k

            if os.path.exists((os.path.join(self.dir_bdmv, "SNP", ""))):
                self.dir_snp = os.path.join(self.dir_bdmv, "SNP", "")
                s = os.walk(self.dir_snp).__next__()
                if s[2].__len__():          # Note the C-Sharp code matches against the actual *.mnv files. I didnt but should verify if such folders contain anything other than that.
                    self.bd_psp = True
                    del s
        else:
            raise Exception("Instance's dir_root attribute has either not been set or doesnt exist.")
            
            
        if (self.dir_stream):
            if os.path.exists((os.path.join(self.dir_stream, "SSIF", ""))):
                self.dir_ssif = os.path.join(self.dir_stream, "SSIF", "")           
                v = os.walk(self.dir_ssif).__next__()
                if v[2].__len__():
                    self.bd_3d = True
        else:
            raise Exception("Instance's dir_stream attribute has either not been set or doesnt exist.")
            
        return


    def listBDMV(self):
        self.bd_playlists = BDROM.listloader(self.dir_playlist, 'MPLS') if self.dir_playlist else None
        self.bd_streamlists = BDROM.listloader(self.dir_stream, 'M2TS') if self.dir_stream else None
        self.bd_cliplists = BDROM.listloader(self.dir_clip, 'CLPI') if self.dir_clip else None
        self.bd_interleavelists = BDROM.listloader(self.dir_ssif, 'SSIF') if self.dir_ssif else None
        return
        
    def scanBDMV(self):
        self.clipresults = ScanTask.clipfilescan(self.dir_clip, self.bd_cliplists)
        self.playlistsresults = ScanTask.playlistscan(self.dir_playlist, self.bd_playlists, self.bd_cliplists, self.bd_streamlists)
        return

    def sortBDMV(self):
        # Find Main Title (Really it's "Guess Main Title")

        def dsort(k):
            if not x.playlistsresults[k].playlistchapters: # This logic added because there may be a bug with VC-1 video only tracks as evident in Empire Of The Sun 00010.mpls 
                return ("0:00:00.000", 0)
            else:
                v1 = self.convertchaptersecs(timedelta(seconds=x.playlistsresults[k].playlistchapters[-1]))
                v2 = x.playlistsresults[k].playlistchapters.__sizeof__()
            return (v1, v2)
            
        data = sorted(x.playlistsresults, key=dsort, reverse=True)
        data = sorted(data)
        
        print("This is the list sorted: \n\n ", sorted(x.playlistsresults, key=dsort, reverse=True))


    def printBDMV(self, file=None):
        
        # TODO: Checking 'file' because in the future we can develop a use case where we only get info from specific files
        
        for file, mpls in self.playlistsresults.items():
            print("PLAYLIST: ", file)
            print("======================")
            print("FILE" + '\t\t' + "START TIME" + '\t' + "END TIME" + '\t' + "DURATION")
            for index in range(0, len(mpls.chapterclips)):
                print(mpls.chapterclips[index].name + '\t' + self.convertchaptersecs(timedelta(seconds=mpls.chapterclips[index].relativetimein)) + '\t' + self.convertchaptersecs(timedelta(seconds=mpls.chapterclips[index].relativetimeout)) + '\t' + self.convertchaptersecs(timedelta(seconds=mpls.chapterclips[index].length)))
            print()
           

    @staticmethod
    def listloader(dirpath, ftype):
        contents = [x for x in os.listdir(dirpath) if x.endswith(ftype.lower()) or x.endswith(ftype.upper())]        # Think about making this a generator in the future for speed improvements.
        return contents 

    
    @staticmethod
    def convertchaptersecs(secsdelta):
        assert isinstance(secsdelta, timedelta)
        mm, ss = divmod(secsdelta.seconds, 60)
        hh, mm = divmod(mm, 60)
        s = "%d:%02d:%02d" % (hh, mm, ss)
        if secsdelta.days:
            def plural(n):
                return n, abs(n) != 1 and "s" or ""
            s = ("%d day%s, " % plural(secsdelta.days)) + s
        if secsdelta.microseconds == 0: # modified timedelta to only precision output to three decimal places
                s = s + '.000'
        else:
                s = s + ("%.3f" % (secsdelta.microseconds * .000001)).lstrip("0") 
        return s
        
    
