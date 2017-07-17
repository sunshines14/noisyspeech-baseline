import struct
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
import wave
import os
import math
from time import time
import sys
import multiprocessing 
import logging


def User(filePath, time_set, detValue) :
    listArr = []
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

    aaa=np.fft.fft(npa, n=512)

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

    ff.close()
    ff2.close()

    return (f, t, Sxx)


def Get_index(f) :
    t0 = time()
    iArr = np.zeros((0,0), dtype = np.int64) 
    iArr2 = np.zeros((0,0), dtype = np.int64) 
    n = 0

    for i in f :  
        if i == float(1000) or i == float(2000) or i == float(3000) or i == float(4000) or i == float(5000) :
            iArr = np.append(iArr, n)
            n = n+1
        elif i < float(2000) and i != float(1000) :
            iArr2 = np.append(iArr2, n)
            n = n+1
        else :
            n = n+1 

        print "%.3fs : %d < %d" % (time()-t0, n, len(f))
    
    return (iArr, iArr2)


def Get_value(iArr, iArr2, f, t, Sxx) :
    t0 = time() 
    n = 0
    vSum = 0
    v2Sum = 0
    vArr = np.zeros((0,0), dtype = np.int64) 
    v2Arr = np.zeros((0,0), dtype = np.int64) 

    fSh = f.shape
    tSh = t.shape

    l = len(iArr)
    l2 = int(fSh[0] - l)

    while n < tSh[0] :
        for x in range(fSh[0]) :
            tmp = Sxx[x][n]
            #tmp = math.log(tmp)
            if Binary_Search(iArr, x) == True :
                vSum = np.add(vSum, tmp)
            elif (Binary_Search(iArr, x) != True) and (Binary_Search(iArr2, x) != True) :
                v2Sum = np.add(v2Sum, tmp)
        vSum = np.divide(vSum, l)
        v2Sum = np.divide(v2Sum, l2)

        vArr = np.append(vArr, vSum)
        v2Arr = np.append(v2Arr, v2Sum)
        
        n = n+1

        print "%.3fs : %d < %d" % (time()-t0, n, tSh[0])
    
    return (vArr, v2Arr)


"""
def Get_value(iArr, iArr2, f, t, Sxx, n, cond, result) :
    t0 = time() 
    vSum = 0
    v2Sum = 0
    vArr = np.zeros((0,0), dtype = np.int64)
    v2Arr = np.zeros((0,0), dtype = np.int64)

    fSh = f.shape
    #tSh = t.shape

    l = len(iArr)
    l2 = int(fSh[0] - l)
    
    while n < cond :
        for x in range(fSh[0]) :
            tmp = Sxx[x][n]
            #tmp = math.log(tmp)
            if Binary_Search(iArr, x) == True :
                vSum = np.add(vSum, tmp)
            elif (Binary_Search(iArr, x) != True) and (Binary_Search(iArr2, x) != True) :
                v2Sum = np.add(v2Sum, tmp)
        vSum = np.divide(vSum, l)
        v2Sum = np.divide(v2Sum, l2)

        vArr = np.append(vArr, vSum)
        v2Arr = np.append(v2Arr, v2Sum)
        
        n = n+1 
        print "%.3fs : %d < %d by %d" % (time()-t0, n, cond, os.getpid())
        
    result.put(vArr)
    result.put(v2Arr)

    return  
"""


def Get_ratio(vArr, v2Arr) :
    t0 = time()
    ratio = 0
    ratioArr = np.zeros((0,0), dtype = np.int64) 
    

    for x in range(len(vArr)) :
        ratio = np.divide(vArr[x], v2Arr[x])
        ratioArr = np.append(ratioArr, ratio)

        print "%.3fs : %d < %d" % (time()-t0, x, len(vArr))

    return ratioArr


def Find_mValue(ratioArr, detValue) :
    t0 = time()
    beepArr = np.zeros((0,0), dtype = np.int64) 
    lastArr = np.zeros((0,0), dtype = np.int64) 

    tmpArr = np.zeros((0,0), dtype = np.int64) 
    tmp2Arr = np.zeros((0,0), dtype = np.int64) 

    inx = 0
    t = 0
    IsBeep = False
    count = 0

    for value in ratioArr :
        inx = np.where(ratioArr == value)
        inx = inx[0][0]
        t = inx + 1 

        tmpArr = ratioArr[inx-20 : inx]
        tmp2Arr = ratioArr[inx : inx+20]
        det1 = 0
        det2 = 0

        for x in tmpArr :
            if x >= detValue : 
                det1 = det1 + 1
        for x in tmp2Arr :
            if x >= detValue :
                det2 = det2 + 1

        if (det1 == 0) and (det2 == 20) and (value >= float(detValue)) :
            IsBeep = True
            beepArr = np.append(beepArr, t) #시작값
        
        elif (IsBeep == True) and (value < float(detValue)) :
            if (det1 >= 20) :
                beepArr = np.append(beepArr, t) #끝값
            else :
                IsBeep = False
                beepArr[-1] = -999
                lastArr = np.append(lastArr, (len(beepArr) - 1)) 

        count = count + 1 
        print "%.2f : %d < %d" % (time()-t0, count, len(ratioArr))

    mValueArr = np.zeros((0,0), dtype = np.int64) 
    p1 = 0
    p2 = 0
    mValue = 0
    fst = 0
    count = 0

    for x in lastArr :
        if fst == 0 :
            p1 = 160 * (beepArr[0:x][0])
            p2 = 160 * (beepArr[0:x][-1])
            mValue = (p1 + p2) / 2
            mValueArr = np.append(mValueArr, mValue)
            fst = x
            
        else :
            p1 = 160 * (beepArr[fst+1:x][0])
            p2 = 160 * (beepArr[fst+1:x][-1])
            mValue = (p1 + p2) / 2
            mValueArr = np.append(mValueArr, mValue)
            fst = x 

        count = count + 1
        print "%.3fs : %d < %d" % (time()-t0, count, len(lastArr))
    
    return mValueArr


def Split_corpus(mValueArr, listArr, filePath, time_length) :
    t0 = time()
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

        inFile.close()
        outFile.close()

        print "corpus %s" % (listArr[n])
        #print "corpus %s : %d ~ %d\n" % (listArr[n], p1, p2)
        print "%.3fs : %d < %d" % (time()-t0, n, len(listArr))

        n = n + 1
    #nextFilePath = listArr[n]
    
    #return nextFilePath


def Binary_Search(array, target) :
    first = 0
    last = len(array)-1
    found = False

    while (first <= last and not found) :
        mid = (first + last) // 2
        if array[mid] == target :
            found = True
        else :
            if target < array[mid] :
                last = mid - 1
            else : 
                first = mid + 1 

    return found 


#def Main() :
if __name__ == '__main__' :
    t0 = time()
    filePath, listArr, time_length, detValue = User(sys.argv[1], sys.argv[2], sys.argv[3])
    t1 = time()-t0
    print "-------------- User Completed (1/7) -------------- Time : %.3fs" % (t1)
    f,t,Sxx = Spectrogram(filePath)
    t2 = time()-t0
    print "-------------- Spectrogram Completed (2/7) -------------- Time : %.3fs" % (t2)
    iArr,iArr2 = Get_index(f)
    t3 = time()-t0
    print "-------------- Get index Completed (3/7) -------------- Time : %.3fs" % (t3)
    """
    tSh = t.shape
    n, cond = 0, tSh[0]
    result = multiprocessing.Queue()
    multiprocessing.log_to_stderr()
    logger = multiprocessing.get_logger()
    logger.setLevel(logging.INFO)
    p1 = multiprocessing.Process(target=Get_value, args=(iArr, iArr2, f, t, Sxx, n, int(cond*(1/2)), result))
    p2 = multiprocessing.Process(target=Get_value, args=(iArr, iArr2, f, t, Sxx, int(cond*(1/2)),int(cond*(2/2)), result))
    p3 = multiprocessing.Process(target=Get_value, args=(iArr, iArr2, f, t, Sxx, int(cond*(2/6)), int(cond*(3/6)), result))
    p4 = multiprocessing.Process(target=Get_value, args=(iArr, iArr2, f, t, Sxx, int(cond*(3/6)), int(cond*(4/6)), result))
    p5 = multiprocessing.Process(target=Get_value, args=(iArr, iArr2, f, t, Sxx, int(cond*(4/6)), int(cond*(5/6)), result))
    p6 = multiprocessing.Process(target=Get_value, args=(iArr, iArr2, f, t, Sxx, int(cond*(5/6)), cond, result))

    p1.start()
    p2.start()
    p3.start()
    p4.start()
    p5.start()  
    p6.start()
  
    p1.join()
    p2.join()
    p3.join()
    p4.join()
    p5.join()
    p6.join()

    result.put('STOP')
    vArr = np.zeros((0,0), dtype = np.int64)
    vArr = np.append(vArr, 0)
    v2Arr = np.zeros((0,0), dtype = np.int64)
    v2Arr = np.append(v2Arr, 0) 
    
    x = 0
    while True :
        tmp = result.get() 
        if tmp == 'STOP' : break
        elif (x%2) == 0 : 
            vArr = np.concatenate((vArr, tmp), axis = 0)
            x = x+1
        else :
            v2Arr = np.concatenate((v2Arr, tmp), axis = 0)
            x = x+1
    vArr = np.delete(vArr, 0)
    v2Arr = np.delete(v2Arr, 0) 
    """
    vArr,v2Arr = Get_value(iArr, iArr2, f, t, Sxx)
    t4 = time()-t0
    print "-------------- Get value Completed (4/7) -------------- Time : %.3fs" % (t4)
    ratioArr = Get_ratio(vArr, v2Arr)
    t5 = time()-t0
    print "-------------- Get ratio Completed (5/7) -------------- Time : %.3fs" % (t5)
    mValueArr = Find_mValue(ratioArr, detValue)
    t6 = time()-t0
    print "-------------- Find mValue Completed (6/7) -------------- Time : %.3fs" % (t6)
    Split_corpus(mValueArr, listArr, filePath, time_length)
    t7 = time()-t0
    print "-------------- Split corpus (7/7) -------------- Time : %.3fs" % (t7)
    print "-------------- All Completed --------------"
    print "User : %.3fs\nSpectrogram : %.3fs\nGet index : %.3fs\nGet value : %.3fs\nGet ratio : %.3fs\nFind mValue : %.3fs\nSplit corpus : %.3fs\nTotal : %.3fs" % (t1, t2, t3, t4, t5, t6 ,t7, time()-t0)
    #print "next file name : %s" %nextFilePath


