#!/bin/env python3

__version__ = 0.7
__author__ = "SavSanta (Ru Uba)"

import tkinter
from tkinter import ttk, filedialog
from tkinter.constants import *


# GUI Function Definitions
def browse_action():
    # Allow user to select a directory and store it in global var
    global source_var
    filepath = filedialog.askdirectory()
    source_var.set(filepath)
    print(filepath)

def selall_action():
    playlistbox.selection_set(playlistbox.get_children())

def selnone_action():
    playlistbox.selection_remove(playlistbox.get_children())

def sett_open():
    w_sett = tkinter.Toplevel(pady=10)
    w_sett.title("Settings")
    cbox_filtersecs = tkinter.Checkbutton(w_sett, text="Filter Out Playlists Under 20 seconds", variable=intvar_filtersecs).pack(anchor=W)
    cbox_filterloops = tkinter.Checkbutton(w_sett, text="Filter Out Playlists that Loop", variable=intvar_filterloops).pack(anchor=W)

def box_header(col, listcol):
    for j in col:
        listcol.heading(j, text=j.title())



# Program Version or Generica
bluapp = tkinter.Tk()
bluapp.configure({'padx':10})

# Set Window Title
bluapp.title("bluinfo.py {}".format(__version__))

# StringVar , IntVar, StringVar - Settings Window, TextVariable on entry
intvar_filtersecs = tkinter.IntVar()
intvar_filterloops = tkinter.IntVar()
source_var = tkinter.StringVar()

# Create and pack a top frame
topframe = tkinter.Frame(pady=10)
topframe.pack(side=TOP, fill=X)

#  Create a label and textentry and pack to the left. Super Extraneous
label_selectsource = tkinter.Label(topframe, text="Select the BDROM Source:")
entry_entrypath = tkinter.Entry(topframe, background="yellow", foreground="green", width=100)
label_selectsource.pack(side=LEFT)
entry_entrypath.pack(side=LEFT, expand=TRUE, fill=Y)

# Create the clickable buttons for slection and  pack to the right of the top frame
button_browse = tkinter.Button(topframe, text="Browse", command=browse_action)
button_scan = tkinter.Button(topframe, text="Scan", command=FALSE)
button_scan.pack(side=RIGHT, padx=2)
button_browse.pack(side=RIGHT, padx=2)

##################
# Change Entry Path configuration from above. Disable Entrypath Point. Change DisableBackground to lightblue const.
# https://www.tcl.tk/man/tcl8.4/TkCmd/entry.htm#M16
##################
entry_entrypath.configure(state=DISABLED)
entry_entrypath.configure(disabledbackground="lightblue")

# Make entrypath linked to a textvariable
entry_entrypath.configure(textvariable=source_var)

# Add Second level frame for containing playlist selection widgets
two = tkinter.Frame(bluapp)
two.pack(side=TOP, fill=X)

# Pack playlist  label and buttons and pack to the left in order
label_selectplaylist = tkinter.Label(two, text="Select Playlist(s):")
button_selall = tkinter.Button(two, text="Select All", command=selall_action)
button_selnone = tkinter.Button(two, text="Select None", command=selnone_action)
button_selcustom = tkinter.Button(two, text="Custom", command=FALSE)

label_selectplaylist.pack(side=LEFT, padx=2)
button_selall.pack(side=LEFT, padx=2)
button_selnone.pack(side=LEFT, padx=2)
button_selcustom.pack(side=LEFT, padx=2)

# Add third level frame for containing playlist listbox widgets
three = tkinter.Frame(bluapp)
three.pack(side=TOP, fill=X, pady=1)

# Add TTK Treeview with no tree to the third frame.
# May need to implement checkbox style someone made here https://github.com/RedFantom/s/blob/master/s/checkboxtreeview.py
# See also treeview_multicolumn.py
# Also https://groups.google.com/forum/#!topic/comp.lang.tcl/VwG4_7-1538
playlist_col = [ "Playlist", "File Group", "Length", "Size" ]
playlistbox = ttk.Treeview(three, show="headings", columns=playlist_col, selectmode=EXTENDED, height=7)

box_header(playlist_col, playlistbox)


# Add fourth level frame for containing stream file listbox widgets
four = tkinter.Frame(bluapp)
four.pack(side=TOP, fill=X, pady=1)

# Add TTK Treeview with no tree to the third frame.
streambox_col = [ "Stream File", "Length", "Size" ]
streambox = ttk.Treeview(four, show="headings", columns=streambox_col, selectmode=NONE, height=5)

# # Add appropriate headings text to each column.
# foreach i {0 1 2} j {"Stream File" Length Size } {
# .four.streambox  heading $i -text $j \
# }

# Add fifth level frame for containing playlist listbox widgets
five = tkinter.Frame(bluapp)
five.pack(side=TOP, fill=X, pady=1)

# Add TTK Treeview with no tree to the fifth frame.
langbox_col = [ "Codec", "Language", "Bitrate", "Description" ]
langbox = ttk.Treeview(five, show="headings", columns=langbox_col, selectmode=NONE, height=7)


# # Add appropriate headings text to each column.
# foreach i {0 1 2 3} j { Codec Language Bitrate  Description } {
# .five.langbox  heading $i -text $j \
# }


# Scrollboxes added to playlist, stream, and language boxes above
three_scroll = ttk.Scrollbar(three, orient=VERTICAL, command=playlistbox.yview)
four_scroll = ttk.Scrollbar(four, orient=VERTICAL, command=streambox.yview)
five_scroll = ttk.Scrollbar(five, orient=VERTICAL, command=langbox.yview)

playlistbox.configure(yscrollcommand=three_scroll.set)
streambox.configure(yscrollcommand=four_scroll.set)
langbox.configure(yscrollcommand=five_scroll.set)

playlistbox.pack(side=LEFT, fill=X, expand=TRUE)
streambox.pack(side=LEFT, fill=X, expand=TRUE)
langbox.pack(side=LEFT, fill=X, expand=TRUE)

three_scroll.pack(side=RIGHT, fill=Y)
four_scroll.pack(side=RIGHT, fill=Y)
five_scroll.pack(side=RIGHT, fill=Y)


# Add sixth level frame for containing  culled  final informational textbox widget
six = tkinter.Frame(bluapp)
six.pack(side=TOP, fill=X, pady=1)

# Add sixthleve textbox and scrollbar
info_text = tkinter.Text(six, background="lightblue", borderwidth=3, state=DISABLED, height=8)
six_scroll = ttk.Scrollbar(six, orient=VERTICAL)
info_text.configure(yscrollcommand=six_scroll.set)
six_scroll.configure(command=info_text.yview)

info_text.pack(fill=X, side=LEFT, expand=TRUE)
six_scroll.pack(fill=Y, side=RIGHT)

# Add seventh level frame for containing progressbar widgets
seven = tkinter.Frame(bluapp)
seven.pack(side=TOP, fill=X, pady=1)

# Add a progressbar to the program and make sure it is about 45% full!
seven_progress = ttk.Progressbar(seven, orient=HORIZONTAL, mode="determinate", value=45)
seven_progress.pack(side=LEFT, fill=X, expand=TRUE)

# Add a settings button
button_settings = tkinter.Button(seven, text="Settings", command=sett_open)
button_settings.pack(side=RIGHT)

##################
#
#  Live Testing Debug
#
#  Generating  a few Treeview listbox entries. Testing scrolling and selections
##################

for i in range(0,12):
    playlistbox.insert("", END, text="FuntimeMovieTime", values=["000"+repr(i)+".m2ts", "0"+repr(i), "1:2"+repr(i)+":00", "4"+repr(i)+",542,421"])


for i in range(0,7):
    langbox.insert("", END, text="XXXTentacion", values=["French", "Francais", "192 kbps", "PushaMan"])
    if i %2 == 0:
        streambox.insert("", END, text="Even", values=["English", "English", "142 kbps", "PushaMan"])
        langbox.insert("", END, text="XXXTentacion", values=["Bulgarian", "Bulgar", "256 kbps", "Savon"])
    else:
        streambox.insert("", END, text="Odd", values=["Spanish", "Castellano", "156 kbps", "Sicco Mode"])


##################
#
#  Live Testing Debug
#
#  Generating Lorem Ipsum Data for textbox
##################

lorem="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam euismod ornare convallis. Sed sit amet nisi sem. Integer commodo tincidunt lectus ut cursus. Phasellus at sollicitudin massa. Phasellus scelerisque consequat nibh non finibus. Vestibulum dolor sapien, faucibus et finibus quis, placerat in lacus. Aliquam semper, ligula faucibus dapibus accumsan, tellus urna sagittis eros, a aliquam urna magna sed sapien. \n Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Cras eleifend enim sit amet neque mollis, eu dapibus felis hendrerit. Pellentesque at interdum libero, quis efficitur augue. Nam enim enim, porta eget porta sit amet, tristique non nulla. Nam ac blandit risus, vel consectetur neque. Sed in congue odio. Duis iaculis efficitur mauris, eu eleifend libero pellentesque non. Pellentesque ut justo semper, rhoncus odio vitae, commodo tortor. Nullam sed enim massa. Donec eget luctus nibh, ut venenatis nunc. Donec volutpat, dolor eget mattis congue, lacus mi commodo lacus, in accumsan massa nisi vitae odio. Quisque non tempor nulla. Fusce iaculis, magna vel ornare condimentum, orci erat mattis orci, vitae tincidunt leo felis id magna. Integer in pretium velit, ut vulputate nulla. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Curabitur ut sem condimentum, condimentum nisi nec, facilisis velit."
info_text.config(state=NORMAL)
info_text.insert(END, lorem)
info_text.config(state=DISABLED)
