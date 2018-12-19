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

# Create the clickable buttons for slection and  pack to the right of the top frame
button .top.buttonBrowse -text Browse -command fn_browse
button .top.buttonScan -text Scan -command fn_iso
pack .top.buttonScan .top.buttonBrowse  -side right -padx 2

#  Create a label and textentry and pack to the left
label .top.labelSelectSource -text {Select the BDROM Source:}
entry .top.entryBDpath -bg yellow -fg green -relief sunken -width 110 
pack .top.labelSelectSource  -side left
pack .top.entryBDpath -side left -expand true


##################
#
#  Live Testing Debug
#
# Add text to the Entry Path. Disable Entrypath Point. Change DisableBackground to lightblue const.
# https://www.tcl.tk/man/tcl8.4/TkCmd/entry.htm#M16
##################
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

# Add TTK Treeview with no tree to the third frame.
# May need to implement checkbox style someone made here https://github.com/RedFantom/ttkwidgets/blob/master/ttkwidgets/checkboxtreeview.py
# Also https://groups.google.com/forum/#!topic/comp.lang.tcl/VwG4_7-1538
ttk::treeview .three.playlistbox -show {headings} -columns {Playlist "File Group" Length Size } -selectmode extended -height 7

# Add appropriate headings text to each column. 
foreach i {0 1 2 3} j {Playlist "File Group" Length Size } {
.three.playlistbox  heading $i -text $j \
}

# Pack  the langbox  frame with expand and fill
pack conf .three.playlistbox -expand 1 -fill x


# Add fourth level frame for containing stream file listbox widgets
frame .four 
pack .four -side top -fill x -pady 1

# Add TTK Treeview with no tree to the third frame.
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

# Add TTK Treeview with no tree to the fifth frame.
ttk::treeview .five.langbox -show {headings} -columns { Codec Language Bitrate  Description } -selectmode none -height 8

# Add appropriate headings text to each column. 
foreach i {0 1 2 3} j { Codec Language Bitrate  Description } {
.five.langbox  heading $i -text $j \
}

# Pack  the langbox  frame with expand and fill
pack conf .five.langbox -expand 1 -fill x


# Scrollboxes added to playlist, stream, and language boxes above
ttk::scrollbar .three.scroll  -orient vertical -command ".three.playlistbox yview"
ttk::scrollbar .four.scroll -orient vertical -command ".four.streambox yview"
ttk::scrollbar .five.scroll -orient vertical -command ".five.langbox yview"

.three.playlistbox configure -yscrollcommand ".three.scroll set"
.four.streambox configure -yscrollcommand ".four.scroll set"
.five.langbox configure -yscrollcommand ".five.scroll set"

pack .three.playlistbox -side left
pack .four.streambox -side left
pack .five.langbox -side left

pack .three.scroll -side right -fill y
pack .four.scroll -side right -fill y
pack .five.scroll -side right -fill y


# Add sixth level frame for containing  culled  final informational textbox widget
frame .six 
pack .six -side top -fill x -pady 1

# Add sixthleve textbox and scrollbar
ttk::scrollbar .six.scroll  -orient vertical -command ".six.text yview"
text .six.text -background lightblue -borderwidth 3 -state disabled -height 8  -yscrollcommand ".six.scroll set"

pack .six.text -fill x -side left -fill x -expand 1
pack .six.scroll  -fill y -side right

# Add seventh level frame for containing progressbar widgets
frame .seven
pack .seven -side top -fill x -pady 1

ttk::progressbar .seven.progress -orient horizontal -mode determinate -width 50
#-variable  value  

pack .seven.progress -fill x




##################
#
#  Live Testing Debug
#
#  Generating  a few Treeview listbox entries. Testing scrolling and selections
##################
.three.playlistbox children {}
.four.streambox children {} 
.five.langbox children {}

.three.playlistbox delete [.three.playlistbox children {}]
.four.streambox  delete [.four.streambox children {}]
.five.langbox  delete [.five.langbox children {}]

foreach i {0 1 2 3 4 5 6 7} {
.three.playlistbox insert {} end -text FuntimeMovieTime -values [list 000$i.m2ts 0$i  1:2$i:00 4$i,542,421]
}


foreach i {0 1 2 3 4 5 6 7} {
.five.langbox insert {} end -text MichelThomasin -values {French Francais "192 kbps" {PushaMan}}
.five.langbox insert {} end -text MichelThomasin -values {German Deutsch "192 kbps" {PushaMan}} \
}

.four.streambox insert {} end -text XXXTentacion -values {English English 142 80}
.four.streambox insert {} end -text XXXTentacion -values {English English "142 kbps" {PushaMan}}
.four.streambox insert {} end -text XXXTentacion -values {Spanish Castellano "156 kbps" {PushaMan}}
.four.streambox insert {} end -text XXXTentacion -values {Spanish Castellano "192 kbps" {PushaMan}}

##################
#
#  Live Testing Debug
#
#  Generating Lorem Ipsum Data for textbox
##################

set lorem "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam euismod ornare convallis. Sed sit amet nisi sem. Integer commodo tincidunt lectus ut cursus. Phasellus at sollicitudin massa. Phasellus scelerisque consequat nibh non finibus. Vestibulum dolor sapien, faucibus et finibus quis, placerat in lacus. Aliquam semper, ligula faucibus dapibus accumsan, tellus urna sagittis eros, a aliquam urna magna sed sapien. \n Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Cras eleifend enim sit amet neque mollis, eu dapibus felis hendrerit. Pellentesque at interdum libero, quis efficitur augue. Nam enim enim, porta eget porta sit amet, tristique non nulla. Nam ac blandit risus, vel consectetur neque. Sed in congue odio. Duis iaculis efficitur mauris, eu eleifend libero pellentesque non. Pellentesque ut justo semper, rhoncus odio vitae, commodo tortor. Nullam sed enim massa. Donec eget luctus nibh, ut venenatis nunc. Donec volutpat, dolor eget mattis congue, lacus mi commodo lacus, in accumsan massa nisi vitae odio. Quisque non tempor nulla. Fusce iaculis, magna vel ornare condimentum, orci erat mattis orci, vitae tincidunt leo felis id magna. Integer in pretium velit, ut vulputate nulla. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Curabitur ut sem condimentum, condimentum nisi nec, facilisis velit."
.six.text conf -state normal
.six.text insert 1.0 $lorem
.six.text conf -state disabled
