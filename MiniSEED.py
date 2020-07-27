# -*- coding: utf-8 -*-
"""
十九中数据解析

@author: mashanmu
"""

from io import StringIO
from Spectrum import Spectrum

import numpy as np
import re
import time
import leancloud

leancloud.init("2vwh1TYLAQQx3lClxPmNj39v-gzGzoHsz", "vOLGzfgbSHRpC1Wpyque8DcY")

class SJZDataTrans:    
    def __init__(self, fileUrl, fileName):
        self.fileUrl = fileUrl
        self.fileName = fileName
        
    
    async def update(self, fileUrl, fileName):
        
        def Filter(data_acc, Low_cutoff, High_cutoff, F_sample, N):
            [Low_point, High_point] = map(lambda F: F/F_sample*N, [Low_cutoff, High_cutoff])
            yf = np.fft.fft(data_acc)
            Filtered_spectrum = [yf[i] if i > Low_point and i <= High_point else 0.0 for i in range(N//2+1)]
            return Filtered_spectrum
    
        def integration_disp(Filtered_spectrum):
            [omiga] = map(lambda x:2*np.pi*x, [xf])
            D_lefthalf = 0.0 - Filtered_spectrum[1:N//2]*(1/(omiga[1:N//2]*omiga[1:N//2]))
            D_righthalf = np.flip(D_lefthalf, 0)
            D_righthalf_conj = np.conjugate(D_righthalf)
            D_index0 = np.insert(D_lefthalf, 0, Filtered_spectrum[0])
            D_index0_ = np.append(D_index0, Filtered_spectrum[-1].real)
            D = np.hstack((D_index0_, D_righthalf_conj))
            return D
    
        def fpy(beta, h, Ts, Te, F_sample, acc):
            N = len(acc)
            freq = np.linspace(0, F_sample, N)
            T = 1/freq
            T[0] = N
            Spec = Spectrum(dt, Ts, Te, T)
            Sa = Spec.responseSpectrum(acc, dt, T, h, beta)
            return Sa
        
        #now = time.strftime('%H%M%S', time.localtime(time.time()))
        date = time.strftime('%Y%m%d', time.localtime(time.time()))
        fileUrl = fileUrl
        fileName = fileName
    #fileUrl = '/Users/mashanmu/Desktop/十九中数据转换/十九中振动监测_20200712063859.txt'
    #fileName = '2020-07-02 06:38:59.txt'
    
        with open(fileUrl, 'rb') as f:
            data = f.read()
            data = data[3002:]
            data = data.decode()
            data = re.split("\r\n|\t", data)
            data.pop()
    
        x = []
        y = []
        z = []
        
        SaX = []
        SaY = []
        SaZ = []
        
        lenth = int(len(data)/35)
        for j in range(0, lenth):
            accX = float(data[32+j*35])
            accY = float(data[33+j*35])
            accZ = float(data[34+j*35])
        
            x.append(accX)
            y.append(accY)
            z.append(accZ)
    
        #print(x)
        
        pga = []
        pgaUD = []
        pgaValue = ''
        pgaUDValue = ''
    
        pga.append(max(x)*100)
        pga.append(max(y)*100)
        pgaUD.append(max(z)*100)
    
        pgaValue = max(pga)
        pgaUDValue = max(pgaUD)
        print(pgaValue)
        print(pgaUDValue)
    
        try:
            TriggeredData = leancloud.Object.extend('SHD_PGAValue')
            triggeredData = TriggeredData()
            triggeredData.set('project', '北京市第十九中学')
            triggeredData.set('device', '震创')
            triggeredData.set('pga', pgaValue)
            triggeredData.set('latitude', '39.969362')
            triggeredData.set('longitude', '116.305142')
            triggeredData.save()
        
        except:
            pass
            print('pga save failed.')
    
        ## %%
        beta = 1/6
        h = 0.05
            
        Ts = 0.1 # Spectrum Period Starts at Ts (Sec)
        Te = 10 # Spectrum Period End at Te (Sec)
        
        F_sample = 100
        dt = 1/F_sample
        N = len(x) # Length of signal
        
        freq = np.linspace(0, F_sample, N)
        xf = np.linspace(0.0, F_sample/2, N//2+1)
        
        T = 1/freq
        T[0] = N
        Spec = Spectrum(dt, Ts, Te, T)
        #SaT = Spec.designSpectrum(T)
        SaX = Spec.responseSpectrum(x, dt, T, h, beta)
        SaY = Spec.responseSpectrum(y, dt, T, h, beta)
        SaZ = Spec.responseSpectrum(z, dt, T, h, beta)
    
        #print(SaX)
    
        ##通道：1-6 5层
        try:
            #for i in range(0, 35):
            str = ''
            lenth = int(len(data)/35)
            
            x = []
            y = []
            z = []
            
            diftX = []
            diftY = []
            
            for j in range(0, lenth):
                
                accX = float(data[3+j*35])*100
                accY = float(data[4+j*35])*100
                accZ = float(data[5+j*35])*100
                
                dispX = float(data[1+j*35])
                dispY = float(data[2+j*35])
                
                value = ';%.6f;%.6f;%.6f;%.6f;%.6f;;%.6f;%.6f;%.6f;' % (accX, accY, accZ, dispX, dispY, SaX[j], SaY[j], SaZ[j])
                str = str + value + '\n'
                
                x.append(accX)
                y.append(accY)
                z.append(accZ)
                
                diftX.append(dispX)
                diftY.append(dispY)
                
            Filtered_spectrum_FLX = Filter(x, 0.1, 10, F_sample, N)
            Filtered_spectrum_FLY = Filter(y, 0.1, 10, F_sample, N)
            
            D_FLX = integration_disp(Filtered_spectrum_FLX)
            D_FLY = integration_disp(Filtered_spectrum_FLY)
            
            d_FLX = np.fft.ifft(D_FLX)
            d_FLY = np.fft.ifft(D_FLY)
            
            maxDiftX = max(d_FLX)
            maxDiftY = max(d_FLY)
            maxDispX = max(diftX)
            #maxDispY = max(diftY)
            
            print("5层东西向最大层间位移及层间位移角", maxDiftX.real, maxDiftX.real/420)
            print("5层南北向最大层间位移及层间位移角", maxDiftY.real, maxDiftY.real/420)
            print("maxDispX", maxDispX)
            print("End")
            
            pga = []
            pgaUD = []
            pgaValue = ''
            pgaUDValue = ''
    
            pga.append(max(x))
            pga.append(max(y))
            pgaUD.append(max(z))
    
            pgaValue = '%.6f' % max(pga)
            pgaUDValue = '%.6f' % max(pgaUD)
    
            summary = 'Sampling Rate; 100'
            str = str + summary
            
            #print(str)
            
            fileData = StringIO(str)
            file = leancloud.File(fileName, fileData)
            file.save()
    
            deviceName = '教学楼L5';
            
            TriggeredData = leancloud.Object.extend('TriggeredData')
            triggeredData = TriggeredData()
            triggeredData.set('project', '北京市第十九中学')
            triggeredData.set('device', deviceName)
            triggeredData.set('date', date)
            triggeredData.set('data', file)
            triggeredData.set('pga', pgaValue)
            triggeredData.set('pgaUD', pgaUDValue)
            triggeredData.save()
        
        except:
            pass
            print('通道：1-6 save file failed.')
        
        
        ##通道：7-11
        try:    
            #for i in range(0, 35):
            str = ''
            lenth = int(len(data)/35)
            
            x = []
            y = []
            z = []
            
            for j in range(0, lenth):
                    
                accX = float(data[8+j*35])*100
                accY = float(data[9+j*35])*100
                accZ = float(data[10+j*35])*100
                
                dispX = float(data[6+j*35])
                dispY = float(data[7+j*35])
                
                value = ';%.6f;%.6f;%.6f;%.6f;%.6f;;%.6f;%.6f;%.6f;' % (accX, accY, accZ, dispX, dispY, SaX[j], SaY[j], SaZ[j])
                str = str + value + '\n'
                
                x.append(accX)
                y.append(accY)
                z.append(accZ)
                
            Filtered_spectrum_FLX = Filter(x, 0.1, 10, F_sample, N)
            Filtered_spectrum_FLY = Filter(y, 0.1, 10, F_sample, N)
            
            D_FLX = integration_disp(Filtered_spectrum_FLX)
            D_FLY = integration_disp(Filtered_spectrum_FLY)
            
            d_FLX = np.fft.ifft(D_FLX)
            d_FLY = np.fft.ifft(D_FLY)
            
            maxDiftX = max(d_FLX)
            maxDiftY = max(d_FLY)
            
            print("4层东西向最大层间位移及层间位移角", maxDiftX.real, maxDiftX.real/420)
            print("4层南北向最大层间位移及层间位移角", maxDiftY.real, maxDiftY.real/420)
            print("End")
            
            pga = []
            pgaUD = []
            pgaValue = ''
            pgaUDValue = ''
    
            pga.append(max(x))
            pga.append(max(y))
            pgaUD.append(max(z))
    
            pgaValue = '%.6f' % max(pga)
            pgaUDValue = '%.6f' % max(pgaUD)
            
            #print(value)
            #print(len(value))
            summary = 'Sampling Rate; 100'
            str = str + summary
            
            #print(str)
                
            fileData = StringIO(str)
            file = leancloud.File(fileName, fileData)
            file.save()
    
            deviceName = '教学楼L4';
            
            TriggeredData = leancloud.Object.extend('TriggeredData')
            triggeredData = TriggeredData()
            triggeredData.set('project', '北京市第十九中学')
            triggeredData.set('device', deviceName)
            triggeredData.set('date', date)
            triggeredData.set('data', file)
            triggeredData.set('pga', pgaValue)
            triggeredData.set('pgaUD', pgaUDValue)
            triggeredData.save()
        
        except:
            pass
            print('通道：7-11 save file failed.')
        
    
        ##通道：12-14
        try:    
            #for i in range(0, 35):
            str = ''
            lenth = int(len(data)/35)
            
            x = []
            y = []
            z = []
            
            for j in range(0, lenth):
                    
                accX = float(data[11+j*35])*100
                accY = float(data[12+j*35])*100
                accZ = float(data[13+j*35])*100
                
                #dispX = float(data[7+j*35])
                #dispY = float(data[8+j*35])
                
                value = ';%.6f;%.6f;%.6f;%.6f;%.6f;;%.6f;%.6f;%.6f;' % (accX, accY, accZ, dispX, dispY, SaX[j], SaY[j], SaZ[j])
                str = str + value + '\n'
                
                x.append(accX)
                y.append(accY)
                z.append(accZ)
                
            Filtered_spectrum_FLX = Filter(x, 0.1, 10, F_sample, N)
            Filtered_spectrum_FLY = Filter(y, 0.1, 10, F_sample, N)
            
            D_FLX = integration_disp(Filtered_spectrum_FLX)
            D_FLY = integration_disp(Filtered_spectrum_FLY)
            
            d_FLX = np.fft.ifft(D_FLX)
            d_FLY = np.fft.ifft(D_FLY)
            
            maxDiftX = max(d_FLX)
            maxDiftY = max(d_FLY)
            
            print("3层东西向最大层间位移及层间位移角", maxDiftX.real, maxDiftX.real/420)
            print("3层南北向最大层间位移及层间位移角", maxDiftY.real, maxDiftY.real/420)
            print("End")
            
            pga = []
            pgaUD = []
            pgaValue = ''
            pgaUDValue = ''
    
            pga.append(max(x))
            pga.append(max(y))
            pgaUD.append(max(z))
    
            pgaValue = '%.6f' % max(pga)
            pgaUDValue = '%.6f' % max(pgaUD)
            
            #print(value)
            #print(len(value))
            summary = 'Sampling Rate; 100'
            str = str + summary
            
            #print(str)
            
            fileData = StringIO(str)
            file = leancloud.File(fileName, fileData)
            file.save()
    
            deviceName = '教学楼L3';
            
            TriggeredData = leancloud.Object.extend('TriggeredData')
            triggeredData = TriggeredData()
            triggeredData.set('project', '北京市第十九中学')
            triggeredData.set('device', deviceName)
            triggeredData.set('date', date)
            triggeredData.set('data', file)
            triggeredData.set('pga', pgaValue)
            triggeredData.set('pgaUD', pgaUDValue)
            triggeredData.save()
        
        except:
            pass
            print('通道：12-14 save file failed.')
        
        
        ##通道：15-19
        try:    
            #for i in range(0, 35):
            str = ''
            lenth = int(len(data)/35)
            
            x = []
            y = []
            z = []
            
            for j in range(0, lenth):
                
                accX = float(data[14+j*35])*100
                accY = float(data[15+j*35])*100
                accZ = float(data[16+j*35])*100
                
                #dispX = float(data[7+j*35])
                #dispY = float(data[8+j*35])
                
                value = ';%.6f;%.6f;%.6f;%.6f;%.6f;;%.6f;%.6f;%.6f;' % (accX, accY, accZ, dispX, dispY, SaX[j], SaY[j], SaZ[j])
                str = str + value + '\n'
                
                x.append(accX)
                y.append(accY)
                z.append(accZ)
            
            Filtered_spectrum_FLX = Filter(x, 0.1, 10, F_sample, N)
            Filtered_spectrum_FLY = Filter(y, 0.1, 10, F_sample, N)
            
            D_FLX = integration_disp(Filtered_spectrum_FLX)
            D_FLY = integration_disp(Filtered_spectrum_FLY)
            
            d_FLX = np.fft.ifft(D_FLX)
            d_FLY = np.fft.ifft(D_FLY)
            
            maxDiftX = max(d_FLX)
            maxDiftY = max(d_FLY)
            
            print("2层东西向最大层间位移及层间位移角", maxDiftX.real, maxDiftX.real/420)
            print("2层南北向最大层间位移及层间位移角", maxDiftY.real, maxDiftY.real/420)
            print("End")
            
            pga = []
            pgaUD = []
            pgaValue = ''
            pgaUDValue = ''
    
            pga.append(max(x))
            pga.append(max(y))
            pgaUD.append(max(z))
    
            pgaValue = '%.6f' % max(pga)
            pgaUDValue = '%.6f' % max(pgaUD)
            
            #print(value)
            #print(len(value))
            summary = 'Sampling Rate; 100'
            str = str + summary
            
            #print(str)
            
            fileData = StringIO(str)
            file = leancloud.File(fileName, fileData)
            file.save()
    
            deviceName = '教学楼L2';
            
            TriggeredData = leancloud.Object.extend('TriggeredData')
            triggeredData = TriggeredData()
            triggeredData.set('project', '北京市第十九中学')
            triggeredData.set('device', deviceName)
            triggeredData.set('date', date)
            triggeredData.set('data', file)
            triggeredData.set('pga', pgaValue)
            triggeredData.set('pgaUD', pgaUDValue)
            triggeredData.save()
        
        except:
            pass
            print('通道：15-19 save file failed.')
        
        
        ##通道：20-22
        try:    
            #for i in range(0, 35):
            str = ''
            lenth = int(len(data)/35)
            
            x = []
            y = []
            z = []
            
            for j in range(0, lenth):
                
                accX = float(data[19+j*35])*100
                accY = float(data[20+j*35])*100
                accZ = float(data[21+j*35])*100
                
                #dispX = float(data[7+j*35])
                #dispY = float(data[8+j*35])
                    
                value = ';%.6f;%.6f;%.6f;%.6f;%.6f;;%.6f;%.6f;%.6f;' % (accX, accY, accZ, dispX, dispY, SaX[j], SaY[j], SaZ[j])
                str = str + value + '\n'
                
                x.append(accX)
                y.append(accY)
                z.append(accZ)
                
            Filtered_spectrum_FLX = Filter(x, 0.1, 10, F_sample, N)
            Filtered_spectrum_FLY = Filter(y, 0.1, 10, F_sample, N)
            
            D_FLX = integration_disp(Filtered_spectrum_FLX)
            D_FLY = integration_disp(Filtered_spectrum_FLY)
            
            d_FLX = np.fft.ifft(D_FLX)
            d_FLY = np.fft.ifft(D_FLY)
            
            maxDiftX = max(d_FLX)
            maxDiftY = max(d_FLY)
            
            print("1层东西向最大层间位移及层间位移角", maxDiftX.real, maxDiftX.real/420)
            print("1层南北向最大层间位移及层间位移角", maxDiftY.real, maxDiftY.real/420)
            print("End")
            
            pga = []
            pgaUD = []
            pgaValue = ''
            pgaUDValue = ''
    
            pga.append(max(x))
            pga.append(max(y))
            pgaUD.append(max(z))
    
            pgaValue = '%.6f' % max(pga)
            pgaUDValue = '%.6f' % max(pgaUD)
            
            #print(value)
            #print(len(value))
            summary = 'Sampling Rate; 100'
            str = str + summary
            
            #print(str)
            
            fileData = StringIO(str)
            file = leancloud.File(fileName, fileData)
            file.save()
    
            deviceName = '教学楼L1';
            
            TriggeredData = leancloud.Object.extend('TriggeredData')
            triggeredData = TriggeredData()
            triggeredData.set('project', '北京市第十九中学')
            triggeredData.set('device', deviceName)
            triggeredData.set('date', date)
            triggeredData.set('data', file)
            triggeredData.set('pga', pgaValue)
            triggeredData.set('pgaUD', pgaUDValue)
            triggeredData.save()
        
        except:
            pass
            print('通道：20-22 save file failed.')
        
        
        ##通道：23-32
        try:    
            #for i in range(0, 35):
            str = ''
            lenth = int(len(data)/35)
            
            x = []
            y = []
            z = []
            
            for j in range(0, lenth):
                
                accX = float(data[22+j*35])*100
                accY = float(data[23+j*35])*100
                accZ = float(data[24+j*35])*100
                
                #dispX = float(data[7+j*35])
                #dispY = float(data[8+j*35])
                    
                value = ';%.6f;%.6f;%.6f;%.6f;%.6f;;%.6f;%.6f;%.6f;' % (accX, accY, accZ, dispX, dispY, SaX[j], SaY[j], SaZ[j])
                str = str + value + '\n'
                
                x.append(accX)
                y.append(accY)
                z.append(accZ)
                
            Filtered_spectrum_FLX = Filter(x, 0.1, 10, F_sample, N)
            Filtered_spectrum_FLY = Filter(y, 0.1, 10, F_sample, N)
            
            D_FLX = integration_disp(Filtered_spectrum_FLX)
            D_FLY = integration_disp(Filtered_spectrum_FLY)
            
            d_FLX = np.fft.ifft(D_FLX)
            d_FLY = np.fft.ifft(D_FLY)
            
            maxDiftX = max(d_FLX)
            maxDiftY = max(d_FLY)
            
            print("B1层东西向最大层间位移及层间位移角", maxDiftX.real, maxDiftX.real/420)
            print("B1层南北向最大层间位移及层间位移角", maxDiftY.real, maxDiftY.real/420)
            print("End")
            
            pga = []
            pgaUD = []
            pgaValue = ''
            pgaUDValue = ''
    
            pga.append(max(x))
            pga.append(max(y))
            pgaUD.append(max(z))
    
            pgaValue = '%.6f' % max(pga)
            pgaUDValue = '%.6f' % max(pgaUD)
            
            #print(value)
            #print(len(value))
            summary = 'Sampling Rate; 100'
            str = str + summary
            
            #print(str)
            
            fileData = StringIO(str)
            file = leancloud.File(fileName, fileData)
            file.save()
    
            deviceName = '教学楼B1';
            
            TriggeredData = leancloud.Object.extend('TriggeredData')
            triggeredData = TriggeredData()
            triggeredData.set('project', '北京市第十九中学')
            triggeredData.set('device', deviceName)
            triggeredData.set('date', date)
            triggeredData.set('data', file)
            triggeredData.set('pga', pgaValue)
            triggeredData.set('pgaUD', pgaUDValue)
            triggeredData.save()
        
        except:
            pass
            print('通道：23-32 save file failed.')
        
    
        ##通道：33-35
        try:    
            #for i in range(0, 35):
            str = ''
            lenth = int(len(data)/35)
            
            x = []
            y = []
            z = []
            
            for j in range(0, lenth):
                
                accX = float(data[32+j*35])*100
                accY = float(data[33+j*35])*100
                accZ = float(data[34+j*35])*100
                
                #dispX = float(data[7+j*35])
                #dispY = float(data[8+j*35])
                
                value = ';%.6f;%.6f;%.6f;%.6f;%.6f;;%.6f;%.6f;%.6f;' % (accX, accY, accZ, dispX, dispY, SaX[j], SaY[j], SaZ[j])
                str = str + value + '\n'
                
                x.append(accX)
                y.append(accY)
                z.append(accZ)
            
            pga = []
            pgaUD = []
            pgaValue = ''
            pgaUDValue = ''
    
            pga.append(max(x))
            pga.append(max(y))
            pgaUD.append(max(z))
    
            pgaValue = '%.6f' % max(pga)
            pgaUDValue = '%.6f' % max(pgaUD)
            
            #print(value)
            #print(len(value))
            summary = 'Sampling Rate; 100'
            str = str + summary
            
            #print(str)
            
            fileData = StringIO(str)
            file = leancloud.File(fileName, fileData)
            file.save()
    
            deviceName = '自由场点';
                
            TriggeredData = leancloud.Object.extend('TriggeredData')
            triggeredData = TriggeredData()
            triggeredData.set('project', '北京市第十九中学')
            triggeredData.set('device', deviceName)
            triggeredData.set('date', date)
            triggeredData.set('data', file)
            triggeredData.set('pga', pgaValue)
            triggeredData.set('pgaUD', pgaUDValue)
            triggeredData.set('isFreeField', '1')
            triggeredData.save()
        
        except:
            pass
            print('通道：33-35 save file failed.')