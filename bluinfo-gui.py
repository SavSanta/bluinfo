#!/bin/env python3

__version__ = 0.7
__author__ = "SavSanta (Ru Uba)"

import tkinter
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter.constants import *


class Bluinfo(tk.Tk):

    # GUI Function Definitions
    def quit(self, event=None):
        sys.exit()
    
    def browse_action(self):
        # Allow user to select a directory and store it in global var
        global source_var
        filepath = filedialog.askdirectory()
        self.source_var.set(filepath)
        print(filepath)

    def selall_action(self):
        self.playlistbox.selection_set(playlistbox.get_children())

    def selnone_action():
        self.playlistbox.selection_remove(playlistbox.get_children())

    def sett_open():
        w_sett = tkinter.Toplevel(pady=10)
        w_sett.title("Settings")
        cbox_filtersecs = tkinter.Checkbutton(w_sett, text="Filter Out Playlists Under 20 seconds", variable=intvar_filtersecs).pack(anchor=W)
        cbox_filterloops = tkinter.Checkbutton(w_sett, text="Filter Out Playlists that Loop", variable=intvar_filterloops).pack(anchor=W)

    def fill_header(self, col, listcol):
        for i in col:
            listcol.heading(i, text=i.title())

    def __init__(self):
        
        tk.Tk.__init__(self)
        
        # Program Version or Generica
        #self.configure({'padx':10})

        # Set Window Title
        #self.title("bluinfo.py {}".format(__version__))

        # StringVar , IntVar, StringVar - Settings Window, TextVariable on entry
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

        # Create the clickable buttons for slection and  pack to the right of the top frame
        self.button_browse = tkinter.Button(self.topframe, text="Browse", command=self.browse_action)
        self.button_scan = tkinter.Button(self.topframe, text="Scan", command=FALSE)
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
        self.playlist_col = [ "Playlist", "File Group", "Length", "Size" ]
        self.playlistbox = ttk.Treeview(self.three, show="headings", columns=self.playlist_col, selectmode=EXTENDED, height=7)

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
        self.langbox_col = [ "Codec", "Language", "Bitrate", "Description" ]
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

        # Add sixthleve textbox and scrollbar
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
        self.seven_progress = ttk.Progressbar(self.seven, orient=HORIZONTAL, mode="determinate", value=45)
        self.seven_progress.pack(side=LEFT, fill=X, expand=TRUE)

        # Add a settings button
        self.button_settings = tkinter.Button(self.seven, text="Settings", command=self.sett_open)
        self.button_settings.pack(side=RIGHT)


# ~ ##################
# ~ #
# ~ #  Live Testing Debug
# ~ #
# ~ #  Generating  a few Treeview listbox entries. Testing scrolling and selections
# ~ ##################

# ~ for i in range(0,12):
    # ~ playlistbox.insert("", END, text="FuntimeMovieTime", values=["000"+repr(i)+".m2ts", "0"+repr(i), "1:2"+repr(i)+":00", "4"+repr(i)+",542,421"])


# ~ for i in range(0,7):
    # ~ langbox.insert("", END, text="XXXTentacion", values=["French", "Francais", "192 kbps", "PushaMan"])
    # ~ if i %2 == 0:
        # ~ streambox.insert("", END, text="Even", values=["English", "English", "142 kbps", "PushaMan"])
        # ~ langbox.insert("", END, text="XXXTentacion", values=["Bulgarian", "Bulgar", "256 kbps", "Savon"])
    # ~ else:
        # ~ streambox.insert("", END, text="Odd", values=["Spanish", "Castellano", "156 kbps", "Sicco Mode"])


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
