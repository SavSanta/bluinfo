#!/bin/env python3

__version__ = 0.8
__author__ = "SavSanta (Ru Uba)"

import tkinter
from tkinter import ttk, filedialog
from bluinfo import BDROM
from datetime import timedelta
from iso_639_2map import codecnamefunc, isolangfunc
from tkinter.constants import *

TEST = 10

class BluinfoApp(tkinter.Tk):

    # GUI Function Definitions
    def quit(self, event=None):
        sys.exit()
    
    def browse_action(self):
        # Allow user to select a directory and store it in global var
        filepath = filedialog.askdirectory()
        self.source_var.set(filepath)
        self.button_scan.configure(state=ACTIVE)
        print(filepath)

    def scan_action(self):
        # scan the bdmv -- improve this
        # ~ try:
        self.bdrom = BDROM(self.source_var.get())
        self.incr_progress(10)
        self.bdrom.checkBDMV()
        self.incr_progress(20)
        self.bdrom.cryptBDMV()
        self.incr_progress(30)
        self.bdrom.listBDMV()
        self.incr_progress(40)
        self.bdrom.specialBDMV()
        self.incr_progress(50)
        self.bdrom.scanBDMV()
        self.incr_progress(60)
        self.bdrom.sortBDMV()
        self.incr_progress(75)
        self.populate_playlistbox_gui()
        self.incr_progress(100)
        self.incr_progress(0)

        # ~ except:
            # ~ pass
            # ~ # error message box
            
    def populate_playlistbox_gui(self):
        ''' Populate the BDROM information into the playlistbox GUI '''
        import time
        time.sleep(1)
        for k, v in self.bdrom.playlistsresults.items():
            self.playlistbox.insert("", END, text="FuntimeMovieTime", values=[v.summary['playlist'], v.summary['hduration'], "NOT IMPLEMENTED"])

    def clear_lower_gui(self):
        self.streambox.delete(*self.streambox.get_children())
        self.langbox.delete(*self.langbox.get_children())

    def populate_lower_gui(self, event):
        # Grab the current selection in the list.
        sel_playlist_item = self.playlistbox.selection()
        
        # Get the target playlist
        target = self.playlistbox.item(sel_playlist_item, 'values')[0]
        
        # clear the lower (streambox and langbox) of the GUI for "redrawing"
        self.clear_lower_gui()
        
        # fill streambox with streamclip data
        for _, clip in enumerate(self.bdrom.playlistsresults[target].streamclips):
            self.streambox.insert("", END, text="StreamFiles", values=[clip.name, BDROM.convertchaptersecs(timedelta(seconds=clip.length)), "NOT IMPLEMENTED"])
        
        # fill langbox with langbox data
        for _, stream in self.bdrom.playlistsresults[target].playliststreams.items():
            self.langbox.insert("", END, text="lang", values=[stream.PID, codecnamefunc(stream.streamtype), isolangfunc(stream.languagecode), stream.__str__()])

    def selall_action(self):
        self.playlistbox.selection_set(playlistbox.get_children())

    def selnone_action(self):
        self.playlistbox.selection_remove(playlistbox.get_children())

    def sett_open(self):
        w_sett = tkinter.Toplevel(pady=10)
        w_sett.title("Settings")
        cbox_filtersecs = tkinter.Checkbutton(w_sett, text="Filter Out Playlists Under 20 seconds", variable=intvar_filtersecs).pack(anchor=W)
        cbox_filterloops = tkinter.Checkbutton(w_sett, text="Filter Out Playlists that Loop", variable=intvar_filterloops).pack(anchor=W)

    def incr_progress(self, amount):
        self.seven_progress['value'] = amount
        self.update_idletasks()

    def fill_header(self, col, listcol):
        ''' Add GUI column headings to for each section. '''
        for i in col:
            listcol.heading(i, text=i.title())

    def __init__(self):
        
        tkinter.Tk.__init__(self)
        
        # Program Version or Generica
        self.configure({'padx':10})

        # Set Window Title
        self.title("bluinfo.py {}".format(__version__))
        
        # BDROM object place holder.
        self.bdrom = False

        # StringVar, IntVar, StringVar - Settings Window, TextVariable on entry
        self.intvar_filtersecs = tkinter.IntVar()
        self.intvar_filterloops = tkinter.IntVar()
        self.source_var = tkinter.StringVar()

        # Create and pack a top frame
        self.topframe = tkinter.Frame(pady=10)
        self.topframe.pack(side=TOP, fill=X)

        #  Create a label and textentry and pack to the left. Super Extraneous
        self.label_selectsource = tkinter.Label(self.topframe, text="Select the BDROM Source:")
        self.entry_entrypath = tkinter.Entry(self.topframe, background="yellow", foreground="green", width=100)
        self.label_selectsource.pack(side=LEFT)
        self.entry_entrypath.pack(side=LEFT, expand=TRUE, fill=Y)

        # Create the clickable buttons for selection and  pack to the right of the top frame
        self.button_browse = tkinter.Button(self.topframe, text="Browse", command=self.browse_action)
        self.button_scan = tkinter.Button(self.topframe, text="Scan", command=self.scan_action, state=DISABLED)
        self.button_scan.pack(side=RIGHT, padx=2)
        self.button_browse.pack(side=RIGHT, padx=2)

        ##################
        # Change Entry Path configuration from above. Disable Entrypath Point. Change DisableBackground to lightblue const.
        # https://www.tcl.tk/man/tcl8.4/TkCmd/entry.htm#M16
        ##################
        self.entry_entrypath.configure(state=DISABLED)
        self.entry_entrypath.configure(disabledbackground="lightblue")

        # Make entrypath linked to a textvariable
        self.entry_entrypath.configure(textvariable=self.source_var)

        # Add Second level frame for containing playlist selection widgets
        self.two = tkinter.Frame(self)
        self.two.pack(side=TOP, fill=X)

        # Pack playlist  label and buttons and pack to the left in order
        self.label_selectplaylist = tkinter.Label(self.two, text="Select Playlist(s):")
        self.button_selall = tkinter.Button(self.two, text="Select All", command=self.selall_action)
        self.button_selnone = tkinter.Button(self.two, text="Select None", command=self.selnone_action)
        self.button_selcustom = tkinter.Button(self.two, text="Custom", command=FALSE)

        self.label_selectplaylist.pack(side=LEFT, padx=2)
        self.button_selall.pack(side=LEFT, padx=2)
        self.button_selnone.pack(side=LEFT, padx=2)
        self.button_selcustom.pack(side=LEFT, padx=2)

        # Add third level frame for containing playlist listbox widgets
        self.three = tkinter.Frame(self)
        self.three.pack(side=TOP, fill=X, pady=1)

        # Add TTK Treeview with no tree to the third frame.
        # May need to implement checkbox style someone made here https://github.com/RedFantom/s/blob/master/s/checkboxtreeview.py
        # See also treeview_multicolumn.py
        # Also https://groups.google.com/forum/#!topic/comp.lang.tcl/VwG4_7-1538
        self.playlist_col = [ "Playlist", "Length", "Size" ]
        self.playlistbox = ttk.Treeview(self.three, show="headings", columns=self.playlist_col, selectmode=BROWSE, height=7)
        
        # Bind double-click/single-click/up/down events to populate streamfile and codecs function.
        self.playlistbox.bind("<ButtonRelease-1>", self.populate_lower_gui)
        self.playlistbox.bind("<KeyRelease-Up>", self.populate_lower_gui)
        self.playlistbox.bind("<KeyRelease-Down>", self.populate_lower_gui)

        # Add appropriate headings text to each column.
        self.fill_header(self.playlist_col, self.playlistbox)

        # Add fourth level frame for containing stream file listbox widgets
        self.four = tkinter.Frame(self)
        self.four.pack(side=TOP, fill=X, pady=1)

        # Add TTK Treeview with no tree to the third frame.
        self.streambox_col = [ "Stream File", "Length", "Size" ]
        self.streambox = ttk.Treeview(self.four, show="headings", columns=self.streambox_col, selectmode=NONE, height=5)

        # Add appropriate headings text to each column.
        self.fill_header(self.streambox_col, self.streambox)

        # Add fifth level frame for containing playlist listbox widgets
        self.five = tkinter.Frame(self)
        self.five.pack(side=TOP, fill=X, pady=1)

        # Add TTK Treeview with no tree to the fifth frame.
        self.langbox_col = [ "PID", "Codec", "Language", "Description" ]
        self.langbox = ttk.Treeview(self.five, show="headings", columns=self.langbox_col, selectmode=NONE, height=7)

        #  Add appropriate headings text to each column.
        self.fill_header(self.langbox_col, self.langbox)

        # Scrollboxes added to playlist, stream, and language boxes above
        self.three_scroll = ttk.Scrollbar(self.three, orient=VERTICAL, command=self.playlistbox.yview)
        self.four_scroll = ttk.Scrollbar(self.four, orient=VERTICAL, command=self.streambox.yview)
        self.five_scroll = ttk.Scrollbar(self.five, orient=VERTICAL, command=self.langbox.yview)

        self.playlistbox.configure(yscrollcommand=self.three_scroll.set)
        self.streambox.configure(yscrollcommand=self.four_scroll.set)
        self.langbox.configure(yscrollcommand=self.five_scroll.set)

        self.playlistbox.pack(side=LEFT, fill=X, expand=TRUE)
        self.streambox.pack(side=LEFT, fill=X, expand=TRUE)
        self.langbox.pack(side=LEFT, fill=X, expand=TRUE)

        self.three_scroll.pack(side=RIGHT, fill=Y)
        self.four_scroll.pack(side=RIGHT, fill=Y)
        self.five_scroll.pack(side=RIGHT, fill=Y)

        # Add sixth level frame for containing  culled  final informational textbox widget
        self.six = tkinter.Frame(self)
        self.six.pack(side=TOP, fill=X, pady=1)

        # Add sixthlevel textbox and scrollbar
        self.info_text = tkinter.Text(self.six, background="lightblue", borderwidth=3, state=DISABLED, height=8)
        self.six_scroll = ttk.Scrollbar(self.six, orient=VERTICAL)
        self.info_text.configure(yscrollcommand=self.six_scroll.set)
        self.six_scroll.configure(command=self.info_text.yview)

        self.info_text.pack(fill=X, side=LEFT, expand=TRUE)
        self.six_scroll.pack(fill=Y, side=RIGHT)

        # Add seventh level frame for containing progressbar widgets
        self.seven = tkinter.Frame(self)
        self.seven.pack(side=TOP, fill=X, pady=1)

        # Add a progressbar to the program and make sure it is about 45% full!
        self.seven_progress = ttk.Progressbar(self.seven, orient=HORIZONTAL, mode="determinate", value=0)
        self.seven_progress.pack(side=LEFT, fill=X, expand=TRUE)

        # Add a settings button
        self.button_settings = tkinter.Button(self.seven, text="Settings", command=self.sett_open)
        self.button_settings.pack(side=RIGHT)

# ~ ##################
# ~ #
# ~ #  Live Testing Debug
# ~ #
# ~ #  Generating Lorem Ipsum Data for textbox
# ~ ##################

# ~ lorem="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam euismod ornare convallis. Sed sit amet nisi sem. Integer commodo tincidunt lectus ut cursus. Phasellus at sollicitudin massa. Phasellus scelerisque consequat nibh non finibus. Vestibulum dolor sapien, faucibus et finibus quis, placerat in lacus. Aliquam semper, ligula faucibus dapibus accumsan, tellus urna sagittis eros, a aliquam urna magna sed sapien. \n Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Cras eleifend enim sit amet neque mollis, eu dapibus felis hendrerit. Pellentesque at interdum libero, quis efficitur augue. Nam enim enim, porta eget porta sit amet, tristique non nulla. Nam ac blandit risus, vel consectetur neque. Sed in congue odio. Duis iaculis efficitur mauris, eu eleifend libero pellentesque non. Pellentesque ut justo semper, rhoncus odio vitae, commodo tortor. Nullam sed enim massa. Donec eget luctus nibh, ut venenatis nunc. Donec volutpat, dolor eget mattis congue, lacus mi commodo lacus, in accumsan massa nisi vitae odio. Quisque non tempor nulla. Fusce iaculis, magna vel ornare condimentum, orci erat mattis orci, vitae tincidunt leo felis id magna. Integer in pretium velit, ut vulputate nulla. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Curabitur ut sem condimentum, condimentum nisi nec, facilisis velit."
# ~ info_text.config(state=NORMAL)
# ~ info_text.insert(END, lorem)
# ~ info_text.config(state=DISABLED)


if __name__ == '__main__':
    test = BluinfoApp()
    test.mainloop()
