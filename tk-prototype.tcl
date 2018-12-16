#!/bin/sh
# the next line restarts using wish \
exec wish "$0" ${1+"$@"}

# Program Version or Generica
set prog_version "0.5"

# Set Window Title
wm title . "bluinfo.py $prog_version"

# Add padding to root window
. conf -padx 10

# Create and pack a top frame
frame .top -pady 10
pack .top -side top -fill x

#Create the clickable buttons for slection and  pack to the right of the top frame
button .top.buttonBrowse -text Browse -command fn_browse
button .top.buttonScan -text Scan -command fn_iso
pack .top.buttonBrowse  .top.buttonScan -side right -padx 2

#  Create a label and textentry and pack to the left
label .top.labelSelectSource -text {Select the BDROM Source:}
entry .top.entryBDpath -bg yellow -fg green -relief sunken -width 110 
pack .top.labelSelectSource  -side left
pack .top.entryBDpath -side left -expand true

# Live Testing
# Add text to the Entry Path. Disable Entrypath Point. Change DisableBackground to lightblue const.
# https://www.tcl.tk/man/tcl8.4/TkCmd/entry.htm#M16
.top.entryBDpath conf -state disabled
.top.entryBDpath conf -disabledbackground blue
.top.entryBDpath conf -disabledbackground lightblue

# Make entrypath linked to a textvariable
.top.entryBDpath  conf -textvariable var_entrypath

# Add Second level frame for containing playlist selection widgets
frame .two 
pack .two -side top -fill x 

# Pack playlist  label and buttons and pack to the left in order
label .two.label -text "Select Playlist(s):"
button .two.buttonSelectAll -text "Select All"
button .two.buttonSelectNone -text "Select None"
button .two.buttonSelectCustom -text "Custom"
pack .two.label .two.buttonSelectAll .two.buttonSelectNone .two.buttonSelectCustom -side left -padx 2

# Add third level frame for containing playlist listbox widgets
frame .three 
pack .three -side top -fill x -pady 1

#Add TTK Treeview with no tree to the third frame.
ttk::treeview .three.playlistbox -show {headings} -columns {Playlist "File Group" Length Size } -selectmode none -height 5

# Add appropriate headings text to each column. 
foreach i {0 1 2 3} j {Playlist "File Group" Length Size } {
.three.playlistbox  heading $i -text $j \
}

# Add fourth level frame for containing stream file listbox widgets
frame .four 
pack .four -side top -fill x -pady 1

#Add TTK Treeview with no tree to the third frame.
ttk::treeview .four.streambox -show {headings} -columns {"Stream File" Length Size } -selectmode none -height 5

# Add appropriate headings text to each column. 
foreach i {0 1 2} j {"Stream File" Length Size } {
.four.streambox  heading $i -text $j \
}

# Pack  the stream file listbox  frameframe with expand and fill
pack conf .four.streambox -expand 1 -fill x

# Add fifth level frame for containing playlist listbox widgets
frame .five 
pack .five -side top -fill x -pady 1

#Add TTK Treeview with no tree to the fifth frame.
ttk::treeview .five.languagebox -show {headings} -columns { Codec Language Bitrate  Description } -selectmode none -height 5

# Add appropriate headings text to each column. 
foreach i {0 1 2 3} j { Codec Language Bitrate  Description } {
.five.languagebox  heading $i -text $j \
}

# Pack  the languagebox  frame with expand and fill
pack conf .five.languagebox -expand 1 -fill x



# Add sixth level frame for containing  culled  final informational textbox widget
frame .six 
pack .six -side top -fill x

# Add seventh level frame for containing progressbar widgets
frame .seven
pack .seven -side top -fill x





