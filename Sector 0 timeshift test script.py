# -*- coding: utf-8 -*-
#take in target time and shift accordingly

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

                    QIOffset_check = round(QI + phase_err)
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
                
                elif delta_t <= 0.001 and delta_t >= -0.001:
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

                    QIOffset_check = round(QI + phase_err)
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
                
                elif delta_t <= 0.001 and delta_t >= -0.001:
                    print('Time difference is < 1ps , no move required')
                    return

                
            print('Done')
            
            return delta_t


locker = Locker()

TGT_time = input('Current counter time is 1000ns, input target time: ')

locker.set_time(TGT_time)





