# -*- coding: utf-8 -*-
"""
Created on Wed Mar 13 15:42:18 2024

@author: junyangx
"""
import math
import time
import math
from pylab import *
from epics.pv import PV as Pv
import sys
import random  # random number generator for secondary calibration

class Locker:
    def __init__(self):
        self.TIC_reference = 30.8690	#wherever calibration ends up on TIC in ns
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
        
    def set_time(self,time):
        set_t = float(time)
        print(f'delta Time entered: {set_t}')
        delta_t = set_t     #ps
        print(f'Time delta: {delta_t}')
        delta_t_ns = delta_t / 1000             #ns
        
        delta_tpr_ns = -round(delta_t_ns)        #ns
        print(f'TPR move: {delta_tpr_ns}')
        self.CarbideRATPR_current.put(self.CarbideRATPR_reference + delta_tpr_ns) 		#TPR increases, TIC decreases
        
        residual = math.modf((delta_t - (round(delta_t / self.OSC_bucket_time) * self.OSC_bucket_time)) / 10)
        print(residual)
        
        delta_scanoffset_ps = residual[1] * 10
        print(f'Scanoffset move: {delta_scanoffset_ps}')
        self.Scanoffset_current.put(self.Scanoffset_reference + delta_scanoffset_ps)	#Scan offset increases, TIC increases
        
        delta_QIoffset_mdeg = round(residual[0] * 10 *1e-12 * (360000 / (1 / (2.6e9))))
        print(f'QIoffset move: {delta_QIoffset_mdeg}')
        self.QIoffset_current.put(self.QIoffset_reference + delta_QIoffset_mdeg)			#QI offset increases, TIC increases
            
locker = Locker()
temp = locker.TICgetmean_current.get() * 1e12
TGT_time = input('input delta time in ps: ')

locker.set_time(TGT_time)
time.sleep(6)
print(locker.TICgetmean_current.get() * 1e12 - temp)