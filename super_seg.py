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

    time_length = 0
    detValue = int(detValue)

    if time_set == '1' :
        ff = wave.open(filePath, 'rb')
        samples = ff.getnframes()
        time_length = int(samples/16000)
        time_length = time_length - 60 
    elif time_set == '2' :
        time_user = raw_input("time length(h/m/s) : ")
        time_user = time_user.split("/")
        time_length = (int(time_user[0])*3600) + (int(time_user[1])*60) + (int(time_user[2]))

    with open("/home/antman/noisy_corpus/ui/list_merge", "r") as path_list :
        for path in path_list.readlines() :
            listArr.append(path.splitlines()[0])

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

    return Sxx

def myFloat(mylist) :
    return map(float, mylist)

def Get_index(Sxx, detValue) :
    Sxx = np.transpose(Sxx)
    t = len(Sxx) 
    i = 0
    vSum = 0
    v2Sum = 0
    binaryArr = []

    for i in range(t) :
        v2Sum = sum(Sxx[i][65:])
        vSum = Sxx[i][32] + Sxx[i][64] + Sxx[i][96] + Sxx[i][128] + Sxx[i][160]
        v2Sum = v2Sum - vSum + Sxx[i][32] + Sxx[i][64] 
        if v2Sum != 0 :
            binaryArr.append(1 if vSum/v2Sum >= detValue else 0) 

    return binaryArr


def Find_mValue(binaryArr, detValue) :
    trueArr = []
    start = 0
    count = 0
    end = 100
    
    for value in binaryArr :
        if start == 0 :
            for x in binaryArr[start:end] :
                if x == 1 :
                    count = count + 1 
        elif start < len(binaryArr) - 101 :
            count = count + binaryArr[end+1]
            count = count - binaryArr[start]

        trueArr.append(count)
        start = start + 1 
        end = end + 1

    tmpArr = []
    IsBeep = False
    beepValue = 0
    p1 = 0 
    p2 = 0
    mValue = 0
    mValueArr = []

    for i,value in enumerate(trueArr) :
        if IsBeep == False and value >= 80 :
            IsBeep = True 
            tmpArr.append((i,value))

        elif IsBeep == True and value >= 40 :
            tmpArr.append((i,value))

        elif IsBeep == True and value < 40 :
            IsBeep = False
            beepValue = max(tmpArr, key = lambda x:x[1])
            p1 = 160*(beepValue[0])
            p2 = 160*(beepValue[0]+100)

            mValue = int((p1 + p2) / 2)
            mValueArr.append(mValue)
            tmpArr = []

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
    print "%.3fs" % (time()-t0)
    Sxx = Spectrogram(filePath)
    print ": Spectrogram"
    print "%.3fs" % (time()-t0)
    binaryArr = Get_index(Sxx, detValue)
    print ": Get index"
    print "%.3fs" % (time()-t0)
    mValueArr = Find_mValue(binaryArr, detValue)
    print ": Find mValue"
    print "%.3fs" % (time()-t0)
    nextFilePath = Split_corpus(mValueArr, listArr, filePath, time_length)
    print ": Split corpus"
    print ": All Completed"
    print "%.3fs" % (time()-t0)
    print "next file name : %s" %nextFilePath

Main()
