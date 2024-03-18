# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 15:42:18 2024

@author: junyangx
"""
import math
import time
import numpy as np
from pylab import *
from epics.pv import PV as Pv
import sys
import random  # random number generator for secondary calibration

class Locker:
    def __init__(self):
        self.TIC_reference = 811.465           #wherever calibration ends up on TIC in ns
        self.reference_t = self.TIC_reference * 1000     #wherever calibration ends up on TIC in ps
        self.OSC_bucket_time = 1/(65e6)*1e12        #ps
        self.TPR_bucket_time = 1/185.714286e6*1e12  #ps
        self.f0 = 2.6                               #GHz
        self.ScanOffset_center = 10000              #ps
        self.QIOffset_center = 180000               #mdeg 
        self.Scanoffset_PV =    'OSC:LR00:100:PLL:QI_OFFSET'
        self.QIoffset_PV =      'OSC:LR00:100:PLL:SCAN_OFFSET'
        self.CarbideRATPR =     'TPR:LGUN:LS01:0:TRG05_SYS2_TDES'
        self.Scanoffset_current = Pv('OSC:LR00:100:PLL:SCAN_OFFSET')
        self.QIoffset_current = Pv('OSC:LR00:100:PLL:QI_OFFSET')
        self.CarbideRATPR_current = Pv('TPR:LGUN:LS01:0:TRG05_SYS2_TDES')
        self.TICgetmean_current = Pv('OSC:LR00:100:GetMeasMean')
        self.Scanoffset_reference = 10000
        self.QIoffset_reference = 180000
        self.CarbideRATPR_reference = 2310.5
        self.calib_range    = 35                    #in ns one full oscillator bucket guaranteed
        self.calib_points   = 57                    #prime
        
    def calibrate(self):
        tctrl = linspace(0, self.calib_range, self.calib_points) # control values to use
        tstep = (self.calib_range / self.calib_points) * 1e-9
        
        tout = array([]) # array to hold measured time data
        counter_good = array([]) # array to hold array of errors
        
        t_trig = self.CarbideRATPR_current.get() # trigger time in nanoseconds
        scanoffset_start = self.Scanoffset_current.get()
        print(scanoffset_start)
        tctrl = (tctrl*1000) + scanoffset_start
        print(*tctrl)
        
        for x in tctrl:  #loop over input array 
            print(x)
            self.Scanoffset_current.put(x)
            time.sleep(3)   #wait for TIC to stabilize
            tout = np.append(tout,(self.TICgetmean_current.get()))
        
        self.Scanoffset_current.put(scanoffset_start)
        
        print(*tout)
        tdiff = np.diff(tout)
        osc_bucket_indx = np.where(abs(tdiff) > (5*tstep))[0]
        print(osc_bucket_indx)
        
        tpr_shift = round((osc_bucket_indx[0] + 1) * (tstep) * 1e9 - self.OSC_bucket_time / 2 / 1000,1) #ns
        print(tstep)
        print(osc_bucket_indx[0])
        print(self.OSC_bucket_time / 2 / 1000)
        print(tpr_shift)
        
locker = Locker()

locker.calibrate()
