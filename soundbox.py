import pygame
import time
import Adafruit_VCNL40xx
import os
import shutil
import random

#populate audio list
audioDir = "/home/pi/SoundBox/audio/"
files = os.listdir(audioDir)
numfiles = len(files)



#create a VCNL4010 instance.
vcnl = Adafruit_VCNL40xx.VCNL4010()
pygame.mixer.init()

#ring buffer for ambient values
ring = [0]*10
avgAmb = 0
ringIndex = 0

#repopulate the ring buffer and calculate new average
def calibrate():
    global ring
    global avgAmb
    print("len ", len(ring))
    for i in range(len(ring)):
        ring[i] = vcnl.read_ambient()

        print(ring[i])
    avgAmb = sum(ring)/len(ring)
    print('avg: ', avgAmb)

#add a new ambient value to the ring buffer
def addNewAmb(amb):
    global ring
    global ringIndex
    global avgAmb

    ring[ringIndex] = amb
    
    ringIndex += 1
    if ringIndex == len(ring):
        ringIndex = 0
    
    avgAmb = sum(ring)/len(ring)

#start playing a random audio track
def start():
    global audioDir
    global files 
    random.seed()
    file = random.choice(files)
    
    print("play " + audioDir + file )
    pygame.mixer.music.load(audioDir + file)    
    pygame.mixer.music.play()
    time.sleep(0.5)

#check if the new ambient value is interesting 
def checkNewAmb(amb):
    global avgAmb
    delta = avgAmb - amb
    print(amb, " | ", avgAmb)
    if delta < 0:
        # amb > avg
        print(delta)
        if abs(delta) > 0.5*avgAmb:
            print("start")
            start()
            calibrate()
    
    if delta > 0:
        # amb < avg
        print(delta)
        if abs(delta) > 0.5*avgAmb:
            print ("stop")
            pygame.mixer.music.stop() 
            time.sleep(1.0) 
            calibrate()



print(files, numfiles)
calibrate()

while True:
    amb =  vcnl.read_ambient()
    checkNewAmb(amb)
    addNewAmb(amb)       
    time.sleep(0.1) 
