#femtoTEM.py --> script used to control the TEM laser locker built for the Flint/Carbide beam shaping laser system in Sector 0.
#Needs to take in the time difference from the SR620 Time Interval Counter, as well as the requested time shift of the User, then decide how to move the devices in the locker
#Needs access to move the TEM QIOffset & ScanOffset to apply I/Q modulation on the TEM system, and also move TPR Trigfgers to delay the Carbide pulses
#TEM adjusts are for fine timing control, with the I/Q modulation allowing for ~1ps resolution steps
#TPR Trigger delays will be used for coarse timing and, eventually, bucket jump correction
##############################################################################################################################################################################

#Import all the libraries needed here
#####################################

import time
import math
import random
import sys
import watchdog
from pylab import *
import pyepics




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

current_time = ''
requested_time = ''
time_min = ''
time_max = ''
time_jitter = ''
counter_jitter_high = ''


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




#Time manipulation functions: Getting current time & jitter from SR620, taking in requested user time, moving TPR or TEM to change time, checking again, etc.
#############################################################################################################################################################

#Class for handling the SR620 Time Interval Counter
#Reads the time and time jitter data
#There's a 1e9 scale factor in here before outputting the time
###############################################################

class time_interval_counter: 
    
    def __init__(self):
        #create circular buffers for adding time & jitter meaurements from SR620
        self.time_buffer = CircularBuffer(11) #create buffer of size 11 for time
        self.jitter_buffer = CircularBuffer(11) #create buffer of size 11 for jitter
        self.time_buffer.enqueue(self.get('current_time')) #add first element to buffer for time
        self.time_buffer.enqueue(self.get('time_jitter')) #add first element to buffer for jitter
        
        #scale factor might be needed
        self.scale = 1e9
    
    def get_time(self):
        #Get all our time & jitter variables set up
        jit_high = self.get('counter_jitter_high')
        jit = self.get('time_jitter')
        time = self.get('current_time')
        time_high = self.get('time_max')
        time_low = self.get('time_min')
        
        #Do some logic checks
        if time == self.time_buffer.peek():
            print('No new time data to add')
            return None
        if time > time_high or time < time_low:
            print('Time data out of range')
            return None
        if jit > jit_high:
            print('Jitter is too high')
            return None
        
        #Start adding elements now
        self.time_buffer.enqueue(time)
        self.jitter_buffer.enqueue(jit)
        
        return time*self.scale



#For taking in User requested time, figuring out the delta_time and moving TPR or TEM accordingly


class Locker:
    def __init__(self):
        self.counter_time = 1000
        self.TPR_delay = 500
        self.ScanOffset = 0
        self.QIOffset = 180000

    def set_time(self,time):
        t = float(time)
        print(f'Time entered: {t}')
        delta_t = t - self.counter_time
        print(f'time difference is: {delta_t}\n')
        delay = self.TPR_delay
        offset = self.ScanOffset
        QI = self.QIOffset
        
        if delta_t > 0:
            while delta_t > 0.001:
                if delta_t >= 15.38:
                    print('**in TPR delay loop**\n')
                   
                    delay += 15.38
                    delta_t -= 15.38
                    
                    print(f'new TPR delay: {delay}')
                    print(f'new time offset: {delta_t}\n')

                elif delta_t < 15.38 and delta_t > 0.005:
                    print('**in ScanOffset loop**\n')
                    
                    offset += 0.005
                    delta_t -= 0.005
                    
                    print(f'new ScanOffset: {offset}')
                    print(f'new time offset: {delta_t}\n')

                elif delta_t <= 0.005 and delta_t >= -0.005:
                    print('**In QIOffset loop**\n')
                    #resolution in fs/step
                    step_res_fs = 5.87
                    #step resolution in mdeg/step
                    step_res_mdeg = 5.49

                    #CONVERSIONS

                    #convert to fs
                    delta_t_fs = delta_t*1e6
                    print(f'Current delta_t: {delta_t}\n')
                    print(f'Current delta_t_fs: {delta_t_fs}')
                    #convert to steps
                    steps = delta_t_fs / step_res_fs
                    print(f'Number of steps needed: {steps}')
                    #phase error conversion (UNITS OF MDEG)
                    phase_err = (steps*step_res_mdeg)
                    print(f'Total phase error in mdeg: {phase_err}\n')

                    #logic check to make sure we're not at the edge of QIOffset range
                    #QIOffset goes from 0 to 360000 mdeg

                    QIOffset_check = QI + phase_err
                    print(f'QIOffset check value: {QIOffset_check}\n')

                    if QIOffset_check > 360000:
                        print('QIOffset too high')
                        QI_delta = QIOffset_check - 360000
                        QI_delta_steps = QI_delta/step_res_mdeg
                        QI_delta_fs = QI_delta_steps*step_res_fs

                        offset += QI_delta_fs
                        delta_t -= QI_delta_fs
                        
                        print(f'new ScanOffset: {offset}')
                        print(f'new time offset: {delta_t}\n')

                    elif QIOffset_check < 0:
                        print('QIOffset too low')
                        QI_delta = 0 + QIOffset_check
                        QI_delta_steps = QI_delta/step_res_mdeg
                        QI_delta_fs = QI_delta_steps*step_res_fs

                        offset += QI_delta_fs
                        delta_t += QI_delta_fs
                        
                        print(f'new ScanOffset: {offset}')
                        print(f'new time offset: {delta_t}\n')

                    elif QIOffset_check <= 360000 and QIOffset_check >= 0:
                        print('QIOffset in range')
                        QI = QIOffset_check
                        delta_t = 0
                        
                        print(f'new QIOffset: {QI}')
                        print(f'new time offset: {delta_t}\n')
                
                elif delta_t <= 0.001 and delat_t >= -0.001:
                    return

            print('Done')
            return delta_t  

        elif delta_t < 0:
            while delta_t < -0.001:
                if delta_t <= -15.38:
                    print('**in TPR delay loop**')
                   
                    delay -= 15.38
                    delta_t += 15.38
                    
                    print(f'new TPR delay: {delay}')
                    print(f'new time offset: {delta_t}\n')
                
                elif delta_t > -15.38 and delta_t < -0.005:
                    print('**in ScanOffset loop**\n')
                    
                    offset -= 0.005
                    delta_t += 0.005
                    
                    print(f'new ScanOffset: {offset}')
                    print(f'new time offset: {delta_t}\n')
                
                elif delta_t >= -0.005 and delta_t <= 0.005:
                    print('**In QIOffset loop**\n')
                    #resolution in fs/step
                    step_res_fs = 5.87
                    #step resolution in mdeg/step
                    step_res_mdeg = 5.49

                    #CONVERSIONS

                    #convert to fs
                    delta_t_fs = delta_t*1e6
                    print(f'Current delta_t: {delta_t}\n')
                    print(f'Current delta_t_fs: {delta_t_fs}')
                    #convert to steps
                    steps = delta_t_fs / step_res_fs
                    print(f'Number of steps needed: {steps}')
                    #phase error conversion (UNITS OF MDEG)
                    phase_err = (steps*step_res_mdeg)
                    print(f'Total phase error in mdeg: {phase_err}\n')

                    #logic check to make sure we're not at the edge of QIOffset range
                    #QIOffset goes from 0 to 360000 mdeg

                    QIOffset_check = QI + phase_err
                    print(f'QIOffset check value: {QIOffset_check}\n')

                    if QIOffset_check > 360000:
                        print('QIOffset too high')
                        QI_delta = QIOffset_check - 360000
                        QI_delta_steps = QI_delta/step_res_mdeg
                        QI_delta_fs = QI_delta_steps*step_res_fs

                        offset += QI_delta_fs
                        delta_t -= QI_delta_fs
                        
                        print(f'new ScanOffset: {offset}')
                        print(f'new time offset: {delta_t}\n')

                    elif QIOffset_check < 0:
                        print('QIOffset too low')
                        QI_delta = 0 + QIOffset_check
                        QI_delta_steps = QI_delta/step_res_mdeg
                        QI_delta_fs = QI_delta_steps*step_res_fs

                        offset += (QI_delta_fs/1e6)
                        delta_t += (QI_delta_fs/1e6)
                        
                        print(f'new ScanOffset: {offset}')
                        print(f'new time offset: {delta_t}\n')

                    elif QIOffset_check <= 360000 and QIOffset_check >= 0:
                        print('QIOffset in range')
                        QI = QIOffset_check
                        delta_t = 0
                        
                        print(f'new QIOffset: {QI}')
                        print(f'new time offset: {delta_t}\n')
                
                elif delta_t <= 0.001 and delat_t >= -0.001:
                    return


            print('Done')
            return delta_t























