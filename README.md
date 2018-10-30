# About
The Fonz, an "easyer" to use passive scanner and transmiter for the TouchTunes Jukebox (Gen 2 and above) wireless remote. TouchTunes remotes TX at 433.92Mhz, uses ASK/OOK, and uses a pin (000-255) for addressing. 
This script was meant to be used with RfCat and the Yard Stick One.

![screenshot](doc/thefonz.png)

# Quick Start Guide

0.) pip install termcolor pyusb 

1.) git clone https://github.com/notpike/The-Fonz.git

2.) cd The-Fonz

3.) sudo ./The_Fonz.py

4.) Plug in the Yard Stick One

5.) Choose 'Scan' to listen for transmissions

6.) Input captured PIN into your own personal remote or use 'TX' to transmit commands

7.) Pocket your remote or cordinate with your wingman, Smack the jukebox while skiping that one Jusin Bieber song while saying, "AYEEE!!"

8.) Injoy your free drinks from your freinds :D

# Versions
###### UPDATE V0.099999
  - Now uses the proper encoding and decoding methods the for NEC protocol! :D
  - Everything is better now!
  - No more recursion problems!
  - Check out The_Fonz_New.py for the new script!

###### UPDATE V0.8
  - Added Electronic Warfare Mode
  - Tatical Jamming inbetween transsmissions 
  - Stops unwanted signals from reaching the target while you still have full control over the juke box

###### UPDATE V0.7
  - Can be imported threw the iPython interface with RfCat.
  - import The_Fonz as f
  - f.MainMenu()

###### UPDATE V0.6
  - Cleaned up my code
  - Grouped the commands togeather for the Brute Force atack, %50 faster but not tested.
  - Plans: Add RTL-SDR and HackRF suport, Figure out Long TX's.

###### UPDATE V0.5
  - Removed redundant re-transmission in the Brute Force feature, ~20sec faster now.
  - Prints the TX codes during a Brute Force.

###### UPDATE V0.4
  - Added Brute Force feture! You now can try every PIN posability for 1 command. Enter in 999 for the PIN and you'll be able to brute force a command.
  - Improved menu, no longer bugs out when you enter the wrong choice.

###### UPDATE V0.3
  - Added TX feture! You now have a 'hopfully' working remote! (Not Tested Yet, Only compaired to the origional remote)
  - Improved PIN discovery so it only returns 1 answer

# More Info

http://productwarranty.touchtunes.com/download/attachments/1179814/900303-001-Remote%20Control%20User%20Guide-R01.pdf?version=1&modificationDate=1373656509000&api=v2

http://www.pressonproducts.com/t1-jukebox-remote-touchtunes-compatible/

https://fccid.io/2AHXI-T1

https://pastebin.com/Ue7UYAPg


Here's an example of what the transmission looks like (in hex), on/off button with the PIN 000 

==Preamble==  ==Key==  ==Message== ==?==

ffff00a2888a2   aaaa   8888aa2aa22  20


And the on/off button with PIN 255

==Preamble==  ==Key==  ==Message== ==?==

ffff00a2888a2 22222222 8888aa2aa22  20


The message sometimes changes with the key but the key will be same regardless of the button pressed.  
Here's an example of the on/off button with the pin 001
 
==Preamble==  ==Key==  ==Message== ==?==

ffff00a2888a2  2aaa    a2222a8aa88   88


Based off of Michael Osman's code. https://greatscottgadgets.com/

rflib and vstruct pulled from https://github.com/ecc1/rfcat

Ported to Portapack-Havoc by Furrtek https://github.com/furrtek/portapack-havoc

Written by NotPike, @IfNotPike
