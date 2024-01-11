#femtoTEM.py --> script used to control the TEM laser locker built for the Flint/Carbide beam shaping laser system in Sector 0.
#Needs to take in the time difference from the SR620 Time Interval Counter, as well as the requested time shift of the User, then decide how to move the devices in the locker
#Needs access to move the TEM QIOffset & ScanOffset to apply I/Q modulation on the TEM system, and also move TPR Trigfgers to delay the Carbide pulses
#TEM adjusts are for fine timing control, with the I/Q modulation allowing for ~1ps resolution steps
#TPR Trigger delays will be used for coarse timing and, eventually, bucket jump correction


#Import all the libraries needed here
import time
import math
import random
import sys
import watchdog
from pylab import *
from psp.Pv import Pv





#Create variables for each TEM PVs we need to use:
##################################################

QIOffset  = 'QIOffset_PV'
QIActive = 'QIActive_PV'
QIGain = 'QIGain_PV'
ScanEnable = 'ScanEnable_PV'
ScanOffset = 'ScanOffset_PV'
RegOutA = ''
RegOutB = ''
RegOnOff = ''
ErrorScale = ''
RegOnOffA = ''
RegOnOffB = ''
RegOutputOffsetA = ''
RegOutputOffsetB = ''
RegPgainA = ''
RegIgainA = ''
RegDgainA = ''
RegPgainB = ''
RegIgainB = ''
RegDgainB = ''
LockedA = ''
LockedB = ''




#Create variables for SR620 PVs we need:
########################################
time_min = ''
time_max = ''
time_jitter = ''



#Create variables for TPR:
##########################
TPR_1 = ''
TPR_2 = ''
TPR_3 = ''


#Need to add functions to pull and write to various PVs:
########################################################
def get(name): #Pulls current value of PV and updates current variable to match
    try:
        name.get(ctrl=True, timeout=10.0)
        return name.value
    except:
        print(f'Unable to read PV: {name}')
        return None

def put(name,val): #Takes current value of variable and writes it to the PV
    try:
        name.put(val, timeout=10.0)
        print (f'Wrote value {val} to PV: {name}.')
    except:
        print (f'Unable to write value {val} to PV: {name}.')

def read(name): #simple function to read the current value of a PV without updating variable in script
    try:
        return name.value
    except:
        print(f'Unable to read PV: {name}')
        return None


#Need buffer for reading data from SR620: (need to declare buffer size later in code)
#########################################
class CircularBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = [None] * size
        self.head = 0
        self.tail = 0
        self.count = 0

    def is_empty(self):
        return self.count == 0

    def is_full(self):
        return self.count == self.size

    def enqueue(self, item):
        if self.is_full():
            # If the buffer is full, overwrite the oldest element
            self.head = (self.head + 1) % self.size

        self.buffer[self.tail] = item
        self.tail = (self.tail + 1) % self.size
        self.count = min(self.count + 1, self.size)

    def dequeue(self):
        if self.is_empty():
            raise IndexError("Cannot dequeue from an empty buffer")

        item = self.buffer[self.head]
        self.head = (self.head + 1) % self.size
        self.count -= 1
        return item

    def peek(self):
        if self.is_empty():
            raise IndexError("Cannot peek into an empty buffer")

        return self.buffer[self.head]


	




























