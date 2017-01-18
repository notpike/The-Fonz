The Fonz, a friendly passive scanner for finding out which pin is being used for a TouchTunes Jukebox (Gen 2 and above) wireless remote. TouchTunes remotes TX at 433.92Mhz, uses ASK/OOK, and uses a pin (000-255) for "security". 
This script was meant to be used with RfCat and the Yard Stick One.

-=Quick Start Guide=-

1.) ~$ git clone https://github.com/notpike/The-Fonz.git\n

2.) ~$ cd The-Fonz

3.) ~$ sudo ./The_Fonz.py

4.) Plug in the Yard Stick One

5.) Wait patiently until bartender uses his remote

6.) Input captured PIN into your own personal remote

7.) Pocket your remote, Smack the jukebox while skiping that one Jusin Bieber song while saying, "AYEEE!!"

8.) Injoy your free drinks from your freinds :D



Here's more info about the wireless remote.

-=User manule=-

http://productwarranty.touchtunes.com/download/attachments/1179814/900303-001-Remote%20Control%20User%20Guide-R01.pdf?version=1&modificationDate=1373656509000&api=v2

-=3rd Aftermarket Replacment Remote (The one I tested)=-

http://www.pressonproducts.com/t1-jukebox-remote-touchtunes-compatible/

-=FCC info=-

https://fccid.io/2AHXI-T1


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

-=Work notes=-
http://pastebin.com/CxuX6XJT


Based off of Michael Osman's code. https://greatscottgadgets.com/
rflib and vstruct pulled from https://github.com/ecc1/rfcat
Written by NotPike, Twitter @pyfurry
