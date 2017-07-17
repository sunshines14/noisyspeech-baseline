import struct
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import wave
import os
import math
from time import time
import sys

def User(filePath, time_set, detValue) :
    listArr = []
    
    #command = raw_input("ex) #file_path #time_set(1or2) #detValue\ncommand : ")
    #command = command.split("#")
    #filePath = command[1][:-1]
    #time_set = command[2][:-1]
    #detValue = int(command[3])

    time_length = 0
    detValue = int(detValue)

    if time_set == '1' :
        ff = wave.open(filePath, 'rb')
        samples = ff.getnframes()
        time_length = int(samples/16000)
        time_length = time_length - 60 # 마지막 약 1분간의 무의미한 구간 제외
    elif time_set == '2' :
        time_user = raw_input("time length(h/m/s) : ")
        time_user = time_user.split("/")
        time_length = (int(time_user[0])*3600) + (int(time_user[1])*60) + (int(time_user[2]))

    with open("/home/antman/soonshin/ui/list_merge.txt", "r") as path_list :
        for path in path_list.readlines() :
            listArr.append(path.splitlines()[0])

    """
    for i in tmp :
        i = i.replace("\n", "")
        listArr.append(i)
    """

    return (filePath, listArr, time_length, detValue)


def Spectrogram(filePath) :
    ff = open(filePath, 'rb')
    ff2 = wave.open(filePath, 'rb')

    samples = ff2.getnframes()

    a=ff.read(samples*2)
    h = ''
    for i in range(0, samples) :
        h = h+'h'

    aa = struct.unpack(h, a)
    npa=np.asarray(aa, dtype=np.float32)
    #print npa
    #print npa.shape

    aaa=np.fft.fft(npa, n=512)
    #print aaa
    #print aaa.shape

    freq = np.fft.fftfreq(aaa.shape[-1])

    fs = 16e3
    N = 160e3
    amp = 2*np.sqrt(2)
    noise_power = 0.01 * fs / 2
    time = np.arange(N) / float(fs)
    mod = 500*np.cos(2*np.pi*0.25*time)
    carrier = amp*np.sin(2*np.pi*3e3*time + mod)
    noise = np.random.normal(scale=np.sqrt(noise_power), size=time.shape)
    noise *= np.exp(-time/5)
    x = carrier + noise

    f, t, Sxx = signal.spectrogram(npa, fs, nperseg=512, noverlap=352, nfft=512,return_onesided=True)
    #plt.pcolormesh(t, f, Sxx)
    #plt.ylabel('Frequency [Hz]')
    #plt.xlabel('Time [sec]')
    #plt.show()
    #print f
    #print f.shape
    #print t
    #print t.shape
    #print Sxx.shapei

    ff.close()
    ff2.close()

    return (f, t, Sxx)


def Get_index(f) :
    iArr = []
    iArr2 = []
    
    n = 0

    for i in f :  
        if i == float(1000) or i == float(2000) or i == float(3000) or i == float(4000) or  i == float(5000) :
            iArr.append(n)  
            n = n+1
        elif i < float(2000) and i != float(1000) :
            iArr2.append(n)
            n = n+1
        else :
            n = n+1 
   
    return (iArr, iArr2)


def Get_value(iArr, iArr2, f, t, Sxx) :
    n = 0
    vSum = 0
    v2Sum = 0
    vArr = []
    v2Arr = []

    fSh = f.shape
    tSh = t.shape

    l = len(iArr)
    l2 = int(fSh[0] - l)

    while n < tSh[0] :
        for x in range(fSh[0]) :
            tmp = Sxx[x][n]
            #tmp = math.log(tmp)
            if x in iArr :
                vSum = np.add(vSum, tmp)
            elif (x not in iArr) and (x not in iArr2) :
                v2Sum = np.add(v2Sum, tmp)

        vSum = np.divide(vSum, l)
        v2Sum = np.divide(v2Sum, l2)

        vArr.append(vSum)
        v2Arr.append(v2Sum)

        n = n+1

    return (vArr, v2Arr)


def Get_ratio(vArr, v2Arr) :
    ratio = 0
    ratioArr = []

    for x in range(len(vArr)) :
        ratio = np.divide(vArr[x], v2Arr[x])
        ratioArr.append(ratio)

    return ratioArr


def Find_mValue(ratioArr, detValue) :
    beepArr = []
    lastArr = []
    tmpArr = []
    tmp2Arr = []
    inx = 0
    t = 0
    IsBeep = False

    for value in ratioArr :
        inx = ratioArr.index(value)
        t = inx + 1 

        tmpArr = ratioArr[inx-10 : inx]
        tmp2Arr = ratioArr[inx : inx+10]
        det1 = 0
        det2 = 0

        for x in tmpArr :
            if x >= detValue : 
                det1 = det1 + 1
        for x in tmp2Arr :
            if x >= detValue :
                det2 = det2 + 1

        if (det1 == 0) and (det2 == 10) and (value >= float(detValue)) :
            IsBeep = True
            beepArr.append(t) #시작값
        
        elif (IsBeep == True) and (value < float(detValue)) :
            if (det1 >= 10) :
                beepArr.append(t) #끝값
            else :
                IsBeep = False
                beepArr.pop()
                beepArr.append('\n')
                lastArr.append((len(beepArr) - 1)) 

    mValueArr = []
    p1 = 0
    p2 = 0
    mValue = 0
    fst = 0

    for x in lastArr :
        if fst == 0 :
            p1 = 160 * (beepArr[0:x][0])
            p2 = 160 * (beepArr[0:x][-1])
            mValue = (p1 + p2) / 2
            mValueArr.append(mValue)
            fst = x
            
        else :
            p1 = 160 * (beepArr[fst+1:x][0])
            p2 = 160 * (beepArr[fst+1:x][-1])
            mValue = (p1 + p2) / 2
            mValueArr.append(mValue)
            fst = x 

    return mValueArr


def Split_corpus(mValueArr, listArr, filePath, time_length) :
    n = 0
    p1 = 0
    p2 = 0
    length = 0
    tmp = 0

    while n < len(listArr) :
        
        p1 = mValueArr[n] + 24000
        p2 = mValueArr[n+1] - 24000

        if (p2/16000) >= time_length :
            break

        length = p2 - p1

        inFile = wave.open(filePath, 'rb')
        inFile.setpos(p1)
        tmp = inFile.readframes(length)

        outName = str(listArr[n])
        outName = outName.replace(".wav", "_noise") + ".wav" 
        outFile = wave.open(outName, 'wb')
        outFile.setnchannels(1)
        outFile.setsampwidth(2)
        outFile.setframerate(16000)
        outFile.writeframes(tmp)

        #print "corpus %s : %d ~ %d\n" % (infiles[n], p1, p2)
        n = n+1

        inFile.close()
        outFile.close()

    nextFilePath = listArr[n]
    
    return nextFilePath


def Main() :
    t0 = time()
    filePath, listArr, time_length, detValue = User(sys.argv[1], sys.argv[2], sys.argv[3])
    print ": User"
    print "%.2f" % (time()-t0)
    f,t,Sxx = Spectrogram(filePath)
    print ": Spectrogram"
    print "%.2f" % (time()-t0)
    iArr, iArr2 = Get_index(f)
    print ": Get index"
    print "%.2f" % (time()-t0)
    vArr, v2Arr = Get_value(iArr, iArr2, f, t, Sxx)
    print ": Get value"
    print "%.2f" % (time()-t0)
    ratioArr = Get_ratio(vArr, v2Arr)
    print ": Get ratio"
    print "%.2f" % (time()-t0)
    mValueArr = Find_mValue(ratioArr, detValue)
    print ": Find mValue"
    print "%.2f" % (time()-t0)
    nextFilePath = Split_corpus(mValueArr, listArr, filePath, time_length)
    print ": Split corpus"
    print ": All Completed"
    print "%.2f" % (time()-t0)
    print "next file name : %s" %nextFilePath

Main()
